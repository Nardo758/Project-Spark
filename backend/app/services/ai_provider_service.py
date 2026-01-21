"""
AI Provider Service - Unified abstraction layer for multiple AI providers
Supports Claude and OpenAI with both Replit AI Integrations and BYOK (Bring Your Own Key)
"""

import os
import logging
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List, AsyncIterator
from enum import Enum
from dataclasses import dataclass
import asyncio

logger = logging.getLogger(__name__)

AI_CALL_TIMEOUT_SECONDS = 60


class AIProviderType(Enum):
    """Supported AI providers"""
    CLAUDE = "claude"
    OPENAI = "openai"


class AIProviderMode(Enum):
    """How the AI provider is accessed"""
    REPLIT = "replit"  # Uses Replit AI Integrations (no API key needed)
    BYOK = "byok"      # Bring Your Own Key


@dataclass
class AIProviderConfig:
    """Configuration for an AI provider"""
    provider: AIProviderType
    mode: AIProviderMode
    api_key: Optional[str] = None
    model: Optional[str] = None


class BaseAIProvider(ABC):
    """Abstract base class for AI providers"""
    
    @abstractmethod
    async def chat(
        self,
        messages: List[Dict[str, str]],
        system_prompt: Optional[str] = None,
        max_tokens: int = 4096,
        temperature: float = 0.7,
    ) -> str:
        """Send a chat completion request"""
        pass
    
    @abstractmethod
    async def chat_json(
        self,
        messages: List[Dict[str, str]],
        system_prompt: Optional[str] = None,
        max_tokens: int = 4096,
    ) -> Dict[str, Any]:
        """Send a chat completion request expecting JSON response"""
        pass
    
    @property
    @abstractmethod
    def provider_name(self) -> str:
        """Return the provider name for logging"""
        pass


class ReplitClaudeAdapter(BaseAIProvider):
    """Claude adapter using Replit AI Integrations"""
    
    def __init__(self):
        import anthropic
        self.client = anthropic.Anthropic()
        # the newest Anthropic model is "claude-sonnet-4-20250514" which was released May 14, 2025
        self.default_model = "claude-sonnet-4-20250514"
    
    @property
    def provider_name(self) -> str:
        return "Claude (Replit AI)"
    
    async def chat(
        self,
        messages: List[Dict[str, str]],
        system_prompt: Optional[str] = None,
        max_tokens: int = 4096,
        temperature: float = 0.7,
    ) -> str:
        def sync_call():
            kwargs = {
                "model": self.default_model,
                "max_tokens": max_tokens,
                "messages": messages,
            }
            if system_prompt:
                kwargs["system"] = system_prompt
            return self.client.messages.create(**kwargs)
        
        try:
            response = await asyncio.wait_for(
                asyncio.get_event_loop().run_in_executor(None, sync_call),
                timeout=AI_CALL_TIMEOUT_SECONDS
            )
            return response.content[0].text
        except asyncio.TimeoutError:
            logger.error("Claude API call timed out")
            raise TimeoutError("AI request timed out")
        except Exception as e:
            logger.error(f"Claude API error: {e}")
            raise
    
    async def chat_json(
        self,
        messages: List[Dict[str, str]],
        system_prompt: Optional[str] = None,
        max_tokens: int = 4096,
    ) -> Dict[str, Any]:
        import json
        json_system = (system_prompt or "") + "\n\nRespond with valid JSON only."
        response = await self.chat(messages, json_system, max_tokens, temperature=0.3)
        try:
            if "```json" in response:
                response = response.split("```json")[1].split("```")[0]
            elif "```" in response:
                response = response.split("```")[1].split("```")[0]
            return json.loads(response.strip())
        except json.JSONDecodeError:
            logger.error(f"Failed to parse JSON from Claude: {response[:200]}")
            return {"error": "Failed to parse response", "raw": response}


class BYOKClaudeAdapter(BaseAIProvider):
    """Claude adapter using user's own API key"""
    
    def __init__(self, api_key: str, model: Optional[str] = None):
        import anthropic
        self.client = anthropic.Anthropic(api_key=api_key)
        self.default_model = model or "claude-sonnet-4-20250514"
    
    @property
    def provider_name(self) -> str:
        return "Claude (BYOK)"
    
    async def chat(
        self,
        messages: List[Dict[str, str]],
        system_prompt: Optional[str] = None,
        max_tokens: int = 4096,
        temperature: float = 0.7,
    ) -> str:
        def sync_call():
            kwargs = {
                "model": self.default_model,
                "max_tokens": max_tokens,
                "messages": messages,
            }
            if system_prompt:
                kwargs["system"] = system_prompt
            return self.client.messages.create(**kwargs)
        
        try:
            response = await asyncio.wait_for(
                asyncio.get_event_loop().run_in_executor(None, sync_call),
                timeout=AI_CALL_TIMEOUT_SECONDS
            )
            return response.content[0].text
        except asyncio.TimeoutError:
            logger.error("BYOK Claude API call timed out")
            raise TimeoutError("AI request timed out")
        except Exception as e:
            logger.error(f"BYOK Claude API error: {e}")
            raise
    
    async def chat_json(
        self,
        messages: List[Dict[str, str]],
        system_prompt: Optional[str] = None,
        max_tokens: int = 4096,
    ) -> Dict[str, Any]:
        import json
        json_system = (system_prompt or "") + "\n\nRespond with valid JSON only."
        response = await self.chat(messages, json_system, max_tokens, temperature=0.3)
        try:
            if "```json" in response:
                response = response.split("```json")[1].split("```")[0]
            elif "```" in response:
                response = response.split("```")[1].split("```")[0]
            return json.loads(response.strip())
        except json.JSONDecodeError:
            logger.error(f"Failed to parse JSON from BYOK Claude: {response[:200]}")
            return {"error": "Failed to parse response", "raw": response}


class ReplitOpenAIAdapter(BaseAIProvider):
    """OpenAI adapter using Replit AI Integrations"""
    
    def __init__(self):
        from openai import OpenAI
        # the newest OpenAI model is "gpt-5" which was released August 7, 2025.
        # do not change this unless explicitly requested by the user
        self.client = OpenAI(
            api_key=os.environ.get("AI_INTEGRATIONS_OPENAI_API_KEY"),
            base_url=os.environ.get("AI_INTEGRATIONS_OPENAI_BASE_URL")
        )
        self.default_model = "gpt-5"
    
    @property
    def provider_name(self) -> str:
        return "OpenAI (Replit AI)"
    
    async def chat(
        self,
        messages: List[Dict[str, str]],
        system_prompt: Optional[str] = None,
        max_tokens: int = 4096,
        temperature: float = 0.7,
    ) -> str:
        def sync_call():
            all_messages = []
            if system_prompt:
                all_messages.append({"role": "system", "content": system_prompt})
            all_messages.extend(messages)
            
            return self.client.chat.completions.create(
                model=self.default_model,
                messages=all_messages,
                max_completion_tokens=max_tokens,
            )
        
        try:
            response = await asyncio.wait_for(
                asyncio.get_event_loop().run_in_executor(None, sync_call),
                timeout=AI_CALL_TIMEOUT_SECONDS
            )
            return response.choices[0].message.content or ""
        except asyncio.TimeoutError:
            logger.error("OpenAI API call timed out")
            raise TimeoutError("AI request timed out")
        except Exception as e:
            logger.error(f"OpenAI API error: {e}")
            raise
    
    async def chat_json(
        self,
        messages: List[Dict[str, str]],
        system_prompt: Optional[str] = None,
        max_tokens: int = 4096,
    ) -> Dict[str, Any]:
        import json
        
        def sync_call():
            all_messages = []
            json_system = (system_prompt or "") + "\n\nRespond with valid JSON only."
            all_messages.append({"role": "system", "content": json_system})
            all_messages.extend(messages)
            
            return self.client.chat.completions.create(
                model=self.default_model,
                messages=all_messages,
                max_completion_tokens=max_tokens,
                response_format={"type": "json_object"},
            )
        
        try:
            response = await asyncio.wait_for(
                asyncio.get_event_loop().run_in_executor(None, sync_call),
                timeout=AI_CALL_TIMEOUT_SECONDS
            )
            content = response.choices[0].message.content or "{}"
            return json.loads(content)
        except asyncio.TimeoutError:
            logger.error("OpenAI JSON API call timed out")
            raise TimeoutError("AI request timed out")
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON from OpenAI: {e}")
            return {"error": "Failed to parse response"}
        except Exception as e:
            logger.error(f"OpenAI API error: {e}")
            raise


class BYOKOpenAIAdapter(BaseAIProvider):
    """OpenAI adapter using user's own API key"""
    
    def __init__(self, api_key: str, model: Optional[str] = None):
        from openai import OpenAI
        self.client = OpenAI(api_key=api_key)
        self.default_model = model or "gpt-4o"
    
    @property
    def provider_name(self) -> str:
        return "OpenAI (BYOK)"
    
    async def chat(
        self,
        messages: List[Dict[str, str]],
        system_prompt: Optional[str] = None,
        max_tokens: int = 4096,
        temperature: float = 0.7,
    ) -> str:
        def sync_call():
            all_messages = []
            if system_prompt:
                all_messages.append({"role": "system", "content": system_prompt})
            all_messages.extend(messages)
            
            return self.client.chat.completions.create(
                model=self.default_model,
                messages=all_messages,
                max_tokens=max_tokens,
                temperature=temperature,
            )
        
        try:
            response = await asyncio.wait_for(
                asyncio.get_event_loop().run_in_executor(None, sync_call),
                timeout=AI_CALL_TIMEOUT_SECONDS
            )
            return response.choices[0].message.content or ""
        except asyncio.TimeoutError:
            logger.error("BYOK OpenAI API call timed out")
            raise TimeoutError("AI request timed out")
        except Exception as e:
            logger.error(f"BYOK OpenAI API error: {e}")
            raise
    
    async def chat_json(
        self,
        messages: List[Dict[str, str]],
        system_prompt: Optional[str] = None,
        max_tokens: int = 4096,
    ) -> Dict[str, Any]:
        import json
        
        def sync_call():
            all_messages = []
            json_system = (system_prompt or "") + "\n\nRespond with valid JSON only."
            all_messages.append({"role": "system", "content": json_system})
            all_messages.extend(messages)
            
            return self.client.chat.completions.create(
                model=self.default_model,
                messages=all_messages,
                max_tokens=max_tokens,
                temperature=0.3,
                response_format={"type": "json_object"},
            )
        
        try:
            response = await asyncio.wait_for(
                asyncio.get_event_loop().run_in_executor(None, sync_call),
                timeout=AI_CALL_TIMEOUT_SECONDS
            )
            content = response.choices[0].message.content or "{}"
            return json.loads(content)
        except asyncio.TimeoutError:
            logger.error("BYOK OpenAI JSON API call timed out")
            raise TimeoutError("AI request timed out")
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON from BYOK OpenAI: {e}")
            return {"error": "Failed to parse response"}
        except Exception as e:
            logger.error(f"BYOK OpenAI API error: {e}")
            raise


class AIProviderService:
    """
    Unified AI Provider Service
    Routes requests to the appropriate provider based on user preferences
    """
    
    def __init__(self, db_session=None):
        self.db = db_session
        self._provider_cache: Dict[int, BaseAIProvider] = {}
    
    def get_provider(
        self,
        user_id: Optional[int] = None,
        config: Optional[AIProviderConfig] = None,
    ) -> BaseAIProvider:
        """
        Get an AI provider based on user preferences or explicit config
        
        Args:
            user_id: User ID to look up preferences for
            config: Explicit configuration (overrides user preferences)
        
        Returns:
            Configured AI provider adapter
        """
        if config:
            return self._create_provider_from_config(config)
        
        if user_id and self.db:
            return self._get_provider_for_user(user_id)
        
        return self._get_default_provider()
    
    def _create_provider_from_config(self, config: AIProviderConfig) -> BaseAIProvider:
        """Create a provider from explicit configuration"""
        if config.provider == AIProviderType.CLAUDE:
            if config.mode == AIProviderMode.BYOK and config.api_key:
                return BYOKClaudeAdapter(config.api_key, config.model)
            return ReplitClaudeAdapter()
        
        elif config.provider == AIProviderType.OPENAI:
            if config.mode == AIProviderMode.BYOK and config.api_key:
                return BYOKOpenAIAdapter(config.api_key, config.model)
            return ReplitOpenAIAdapter()
        
        return ReplitClaudeAdapter()
    
    def _get_provider_for_user(self, user_id: int) -> BaseAIProvider:
        """Get provider based on user's stored preferences"""
        if user_id in self._provider_cache:
            return self._provider_cache[user_id]
        
        from app.models.user import UserAIPreference
        
        try:
            prefs = self.db.query(UserAIPreference).filter(
                UserAIPreference.user_id == user_id
            ).first()
            
            if not prefs:
                return self._get_default_provider()
            
            provider_type = AIProviderType(prefs.provider)
            mode = AIProviderMode(prefs.mode)
            
            config = AIProviderConfig(
                provider=provider_type,
                mode=mode,
                api_key=prefs.get_api_key() if mode == AIProviderMode.BYOK else None,
                model=prefs.model,
            )
            
            provider = self._create_provider_from_config(config)
            self._provider_cache[user_id] = provider
            return provider
            
        except Exception as e:
            logger.error(f"Error getting user AI preferences: {e}")
            return self._get_default_provider()
    
    def _get_default_provider(self) -> BaseAIProvider:
        """Get the default provider (Replit Claude)"""
        return ReplitClaudeAdapter()
    
    def clear_cache(self, user_id: Optional[int] = None):
        """Clear the provider cache"""
        if user_id:
            self._provider_cache.pop(user_id, None)
        else:
            self._provider_cache.clear()
    
    async def chat(
        self,
        messages: List[Dict[str, str]],
        user_id: Optional[int] = None,
        system_prompt: Optional[str] = None,
        max_tokens: int = 4096,
        temperature: float = 0.7,
    ) -> str:
        """Convenience method for chat completions"""
        provider = self.get_provider(user_id=user_id)
        logger.info(f"Using provider: {provider.provider_name}")
        return await provider.chat(messages, system_prompt, max_tokens, temperature)
    
    async def chat_json(
        self,
        messages: List[Dict[str, str]],
        user_id: Optional[int] = None,
        system_prompt: Optional[str] = None,
        max_tokens: int = 4096,
    ) -> Dict[str, Any]:
        """Convenience method for JSON chat completions"""
        provider = self.get_provider(user_id=user_id)
        logger.info(f"Using provider for JSON: {provider.provider_name}")
        return await provider.chat_json(messages, system_prompt, max_tokens)


ai_provider_service = AIProviderService()
