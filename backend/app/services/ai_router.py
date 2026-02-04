"""
AI Model Router - Cost-Optimized Multi-Model Architecture
Routes different task types to appropriate AI models based on complexity and cost.

Architecture:
- Brain (Opus/Sonnet): Complex reasoning, decision-making, analysis
- Muscles (Specialized Models): Task-specific execution
  - Codex/GPT-4: Code generation, debugging
  - Gemini: Web search, data retrieval, summarization
  - Grok: Social media analysis, trend detection (via API)
"""

import os
import requests
from enum import Enum
from typing import Optional, Dict, Any
from anthropic import Anthropic
import openai
import google.generativeai as genai

# Initialize clients
anthropic_client = Anthropic(
    api_key=os.environ.get("AI_INTEGRATIONS_ANTHROPIC_API_KEY"),
    base_url=os.environ.get("AI_INTEGRATIONS_ANTHROPIC_BASE_URL")
)

openai.api_key = os.environ.get("OPENAI_API_KEY")
genai.configure(api_key=os.environ.get("GOOGLE_API_KEY"))

DEEPSEEK_API_KEY = os.environ.get("DEEPSEEK_API_KEY")
DEEPSEEK_BASE_URL = "https://api.deepseek.com/v1"


class TaskType(Enum):
    """Task categories for routing"""
    # Brain tasks (use Claude Opus/Sonnet)
    COMPLEX_REASONING = "complex_reasoning"
    STRATEGIC_ANALYSIS = "strategic_analysis"
    USER_CONVERSATION = "user_conversation"
    OPPORTUNITY_ANALYSIS = "opportunity_analysis"
    
    # Muscle tasks (use specialized models)
    CODE_GENERATION = "code_generation"
    CODE_DEBUG = "code_debug"
    WEB_SEARCH = "web_search"
    DATA_SUMMARIZATION = "data_summarization"
    SOCIAL_ANALYSIS = "social_analysis"
    TREND_DETECTION = "trend_detection"
    SIMPLE_CLASSIFICATION = "simple_classification"


class ModelProvider(Enum):
    """Available model providers"""
    ANTHROPIC_OPUS = "anthropic_opus"          # Most expensive, most capable
    ANTHROPIC_SONNET = "anthropic_sonnet"      # Balanced (current default)
    ANTHROPIC_HAIKU = "anthropic_haiku"        # Fast, cheap
    DEEPSEEK_CHAT = "deepseek_chat"           # Excellent for code, very cheap
    DEEPSEEK_CODER = "deepseek_coder"         # Specialized for coding
    OPENAI_GPT4 = "openai_gpt4"               # Good for code (expensive)
    OPENAI_GPT35 = "openai_gpt35"             # Cheap for simple tasks
    GOOGLE_GEMINI = "google_gemini"            # Good for search/data
    GROK = "grok"                              # Social media analysis (future)


# Task routing map
TASK_ROUTING = {
    # Brain tasks → Claude Sonnet (default)
    TaskType.COMPLEX_REASONING: ModelProvider.ANTHROPIC_SONNET,
    TaskType.STRATEGIC_ANALYSIS: ModelProvider.ANTHROPIC_SONNET,
    TaskType.USER_CONVERSATION: ModelProvider.ANTHROPIC_SONNET,
    TaskType.OPPORTUNITY_ANALYSIS: ModelProvider.ANTHROPIC_SONNET,
    
    # Muscle tasks → Specialized models (DeepSeek for code - 10x cheaper than GPT-4)
    TaskType.CODE_GENERATION: ModelProvider.DEEPSEEK_CODER,  # Was GPT-4
    TaskType.CODE_DEBUG: ModelProvider.DEEPSEEK_CODER,        # Was GPT-4
    TaskType.WEB_SEARCH: ModelProvider.GOOGLE_GEMINI,
    TaskType.DATA_SUMMARIZATION: ModelProvider.GOOGLE_GEMINI,
    TaskType.SOCIAL_ANALYSIS: ModelProvider.GOOGLE_GEMINI,  # Grok when available
    TaskType.TREND_DETECTION: ModelProvider.GOOGLE_GEMINI,
    TaskType.SIMPLE_CLASSIFICATION: ModelProvider.ANTHROPIC_HAIKU,  # Fast + cheap
}


# Cost per 1M tokens (approximate)
MODEL_COSTS = {
    ModelProvider.ANTHROPIC_OPUS: {"input": 15.0, "output": 75.0},
    ModelProvider.ANTHROPIC_SONNET: {"input": 3.0, "output": 15.0},
    ModelProvider.ANTHROPIC_HAIKU: {"input": 0.25, "output": 1.25},
    ModelProvider.DEEPSEEK_CHAT: {"input": 0.14, "output": 0.28},      # Ultra cheap!
    ModelProvider.DEEPSEEK_CODER: {"input": 0.14, "output": 0.28},     # Ultra cheap!
    ModelProvider.OPENAI_GPT4: {"input": 10.0, "output": 30.0},
    ModelProvider.OPENAI_GPT35: {"input": 0.5, "output": 1.5},
    ModelProvider.GOOGLE_GEMINI: {"input": 0.5, "output": 1.5},
}


class AIRouter:
    """Routes AI tasks to optimal models based on task type"""
    
    def __init__(self, user_api_key: Optional[str] = None):
        """
        Initialize router
        
        Args:
            user_api_key: Optional user's own API key (BYOK)
        """
        self.user_api_key = user_api_key
        self.usage_log = []  # Track costs
    
    def route(
        self, 
        task_type: TaskType, 
        prompt: str,
        system_prompt: Optional[str] = None,
        max_tokens: int = 4096,
        temperature: float = 0.7,
        force_model: Optional[ModelProvider] = None
    ) -> Dict[str, Any]:
        """
        Route task to appropriate model and execute
        
        Args:
            task_type: Type of task (determines model selection)
            prompt: User prompt
            system_prompt: System prompt (optional)
            max_tokens: Max tokens to generate
            temperature: Sampling temperature
            force_model: Override routing logic (for testing)
        
        Returns:
            {
                "response": str,
                "model_used": ModelProvider,
                "tokens_used": {"input": int, "output": int},
                "estimated_cost_usd": float
            }
        """
        
        # Determine which model to use
        model = force_model or TASK_ROUTING.get(task_type, ModelProvider.ANTHROPIC_SONNET)
        
        # Execute based on provider
        if model in [ModelProvider.ANTHROPIC_OPUS, ModelProvider.ANTHROPIC_SONNET, ModelProvider.ANTHROPIC_HAIKU]:
            return self._execute_anthropic(model, prompt, system_prompt, max_tokens, temperature)
        
        elif model in [ModelProvider.DEEPSEEK_CHAT, ModelProvider.DEEPSEEK_CODER]:
            return self._execute_deepseek(model, prompt, system_prompt, max_tokens, temperature)
        
        elif model in [ModelProvider.OPENAI_GPT4, ModelProvider.OPENAI_GPT35]:
            return self._execute_openai(model, prompt, system_prompt, max_tokens, temperature)
        
        elif model == ModelProvider.GOOGLE_GEMINI:
            return self._execute_gemini(prompt, system_prompt, max_tokens, temperature)
        
        else:
            raise ValueError(f"Model {model} not yet implemented")
    
    def _execute_anthropic(
        self, 
        model: ModelProvider, 
        prompt: str,
        system_prompt: Optional[str],
        max_tokens: int,
        temperature: float
    ) -> Dict[str, Any]:
        """Execute Claude API call"""
        
        model_map = {
            ModelProvider.ANTHROPIC_OPUS: "claude-3-opus-20240229",
            ModelProvider.ANTHROPIC_SONNET: "claude-3-5-sonnet-20241022",
            ModelProvider.ANTHROPIC_HAIKU: "claude-3-5-haiku-20241022"
        }
        
        # Use user's key if provided (BYOK)
        client = Anthropic(api_key=self.user_api_key) if self.user_api_key else anthropic_client
        
        response = client.messages.create(
            model=model_map[model],
            max_tokens=max_tokens,
            temperature=temperature,
            system=system_prompt or "",
            messages=[{"role": "user", "content": prompt}]
        )
        
        tokens_used = {
            "input": response.usage.input_tokens,
            "output": response.usage.output_tokens
        }
        
        cost = self._calculate_cost(model, tokens_used)
        
        result = {
            "response": response.content[0].text,
            "model_used": model.value,
            "tokens_used": tokens_used,
            "estimated_cost_usd": cost
        }
        
        self.usage_log.append(result)
        return result
    
    def _execute_deepseek(
        self,
        model: ModelProvider,
        prompt: str,
        system_prompt: Optional[str],
        max_tokens: int,
        temperature: float
    ) -> Dict[str, Any]:
        """Execute DeepSeek API call (OpenAI-compatible)"""
        
        model_map = {
            ModelProvider.DEEPSEEK_CHAT: "deepseek-chat",
            ModelProvider.DEEPSEEK_CODER: "deepseek-coder"
        }
        
        headers = {
            "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
            "Content-Type": "application/json"
        }
        
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})
        
        payload = {
            "model": model_map[model],
            "messages": messages,
            "max_tokens": max_tokens,
            "temperature": temperature
        }
        
        response = requests.post(
            f"{DEEPSEEK_BASE_URL}/chat/completions",
            headers=headers,
            json=payload
        )
        response.raise_for_status()
        data = response.json()
        
        tokens_used = {
            "input": data["usage"]["prompt_tokens"],
            "output": data["usage"]["completion_tokens"]
        }
        
        cost = self._calculate_cost(model, tokens_used)
        
        result = {
            "response": data["choices"][0]["message"]["content"],
            "model_used": model.value,
            "tokens_used": tokens_used,
            "estimated_cost_usd": cost
        }
        
        self.usage_log.append(result)
        return result
    
    def _execute_openai(
        self,
        model: ModelProvider,
        prompt: str,
        system_prompt: Optional[str],
        max_tokens: int,
        temperature: float
    ) -> Dict[str, Any]:
        """Execute OpenAI API call"""
        
        model_map = {
            ModelProvider.OPENAI_GPT4: "gpt-4-turbo-preview",
            ModelProvider.OPENAI_GPT35: "gpt-3.5-turbo"
        }
        
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})
        
        response = openai.chat.completions.create(
            model=model_map[model],
            messages=messages,
            max_tokens=max_tokens,
            temperature=temperature
        )
        
        tokens_used = {
            "input": response.usage.prompt_tokens,
            "output": response.usage.completion_tokens
        }
        
        cost = self._calculate_cost(model, tokens_used)
        
        result = {
            "response": response.choices[0].message.content,
            "model_used": model.value,
            "tokens_used": tokens_used,
            "estimated_cost_usd": cost
        }
        
        self.usage_log.append(result)
        return result
    
    def _execute_gemini(
        self,
        prompt: str,
        system_prompt: Optional[str],
        max_tokens: int,
        temperature: float
    ) -> Dict[str, Any]:
        """Execute Google Gemini API call"""
        
        model = genai.GenerativeModel('gemini-pro')
        
        full_prompt = f"{system_prompt}\n\n{prompt}" if system_prompt else prompt
        
        response = model.generate_content(
            full_prompt,
            generation_config=genai.types.GenerationConfig(
                max_output_tokens=max_tokens,
                temperature=temperature
            )
        )
        
        # Gemini doesn't provide exact token counts - estimate
        tokens_used = {
            "input": len(prompt.split()) * 1.3,  # Rough estimate
            "output": len(response.text.split()) * 1.3
        }
        
        cost = self._calculate_cost(ModelProvider.GOOGLE_GEMINI, tokens_used)
        
        result = {
            "response": response.text,
            "model_used": ModelProvider.GOOGLE_GEMINI.value,
            "tokens_used": tokens_used,
            "estimated_cost_usd": cost
        }
        
        self.usage_log.append(result)
        return result
    
    def _calculate_cost(self, model: ModelProvider, tokens_used: Dict[str, int]) -> float:
        """Calculate estimated cost in USD"""
        costs = MODEL_COSTS.get(model, {"input": 0, "output": 0})
        
        input_cost = (tokens_used["input"] / 1_000_000) * costs["input"]
        output_cost = (tokens_used["output"] / 1_000_000) * costs["output"]
        
        return round(input_cost + output_cost, 6)
    
    def get_total_cost(self) -> float:
        """Get total cost for this router session"""
        return sum(log["estimated_cost_usd"] for log in self.usage_log)
    
    def get_usage_summary(self) -> Dict[str, Any]:
        """Get usage statistics"""
        total_tokens = {
            "input": sum(log["tokens_used"]["input"] for log in self.usage_log),
            "output": sum(log["tokens_used"]["output"] for log in self.usage_log)
        }
        
        models_used = {}
        for log in self.usage_log:
            model = log["model_used"]
            models_used[model] = models_used.get(model, 0) + 1
        
        return {
            "total_cost_usd": self.get_total_cost(),
            "total_tokens": total_tokens,
            "total_requests": len(self.usage_log),
            "models_used": models_used
        }


# Convenience functions for common tasks

def analyze_opportunity(opportunity_text: str, user_api_key: Optional[str] = None) -> str:
    """Analyze an opportunity (uses Sonnet - brain task)"""
    router = AIRouter(user_api_key)
    
    result = router.route(
        task_type=TaskType.OPPORTUNITY_ANALYSIS,
        prompt=f"Analyze this business opportunity:\n\n{opportunity_text}",
        system_prompt="You are an expert business analyst. Provide a comprehensive analysis including market potential, feasibility, and recommendations."
    )
    
    return result["response"]


def generate_code(code_task: str, user_api_key: Optional[str] = None) -> str:
    """Generate code (uses GPT-4 - cheaper for code)"""
    router = AIRouter(user_api_key)
    
    result = router.route(
        task_type=TaskType.CODE_GENERATION,
        prompt=code_task,
        system_prompt="You are an expert programmer. Write clean, efficient, well-documented code."
    )
    
    return result["response"]


def search_and_summarize(search_query: str, user_api_key: Optional[str] = None) -> str:
    """Web search and summarization (uses Gemini - cheapest)"""
    router = AIRouter(user_api_key)
    
    result = router.route(
        task_type=TaskType.WEB_SEARCH,
        prompt=f"Search for and summarize information about: {search_query}",
        system_prompt="You are a research assistant. Provide concise, accurate summaries of search results."
    )
    
    return result["response"]


def classify_opportunity_category(title: str, description: str) -> str:
    """Simple classification (uses Haiku - fastest + cheapest)"""
    router = AIRouter()
    
    categories = [
        "Work & Productivity",
        "Money & Finance",
        "Health & Wellness",
        "Home & Living",
        "Technology",
        "Transportation",
        "Shopping & Services",
        "Education & Learning"
    ]
    
    result = router.route(
        task_type=TaskType.SIMPLE_CLASSIFICATION,
        prompt=f"Classify this opportunity into ONE category:\n\nTitle: {title}\nDescription: {description}\n\nCategories: {', '.join(categories)}",
        system_prompt="Respond with ONLY the category name, nothing else.",
        max_tokens=50
    )
    
    return result["response"].strip()
