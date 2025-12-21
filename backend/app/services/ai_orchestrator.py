"""
AI Orchestrator - Coordinates between DeepSeek and Claude AI services
Implements the dual-AI architecture from the OppGrid roadmap
"""

from enum import Enum
from typing import Dict, Any, Optional
import logging
import os

logger = logging.getLogger(__name__)


class AITaskType(Enum):
    """Types of AI tasks for routing decisions"""
    PLATFORM_COORDINATION = "platform_coordination"
    OPPORTUNITY_VALIDATION = "opportunity_validation"
    CONTENT_REWRITING = "content_rewriting"
    BUSINESS_PLAN_GENERATION = "business_plan_generation"
    MARKET_RESEARCH = "market_research"
    IDEA_ANALYSIS = "idea_analysis"
    DOCUMENT_GENERATION = "document_generation"
    LEAD_SCORING = "lead_scoring"
    EXPERT_MATCHING = "expert_matching"


class AIOrchestrator:
    """Routes requests between DeepSeek and Claude based on task type"""

    def __init__(self):
        self.deepseek_tasks = {
            AITaskType.PLATFORM_COORDINATION,
            AITaskType.OPPORTUNITY_VALIDATION,
            AITaskType.LEAD_SCORING,
        }
        self.claude_tasks = {
            AITaskType.BUSINESS_PLAN_GENERATION,
            AITaskType.MARKET_RESEARCH,
            AITaskType.DOCUMENT_GENERATION,
        }
        self.hybrid_tasks = {
            AITaskType.CONTENT_REWRITING,
            AITaskType.IDEA_ANALYSIS,
            AITaskType.EXPERT_MATCHING,
        }

    async def process_request(
        self, task_type: AITaskType, data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Route AI request to appropriate service based on task type

        Args:
            task_type: Type of AI task from AITaskType enum
            data: Input data for processing

        Returns:
            Processed results from AI service
        """
        logger.info(f"Processing {task_type.value} request")

        if task_type in self.deepseek_tasks:
            return await self._call_deepseek(data, task_type)
        elif task_type in self.claude_tasks:
            return await self._call_claude(data, task_type)
        elif task_type in self.hybrid_tasks:
            return await self._process_hybrid(data, task_type)
        else:
            raise ValueError(f"Unknown task type: {task_type}")

    async def _call_deepseek(
        self, data: Dict[str, Any], task_type: AITaskType
    ) -> Dict[str, Any]:
        """Call DeepSeek service for platform coordination tasks"""
        from .llm_ai_engine import llm_ai_engine_service
        
        engine = llm_ai_engine_service
        
        prompt = self._build_prompt_for_task(task_type, data)
        
        try:
            result = await engine.generate_response(prompt)
            return {
                "ai_service": "deepseek",
                "task_type": task_type.value,
                "processed": True,
                "result": result,
            }
        except Exception as e:
            logger.error(f"DeepSeek processing error: {e}")
            return {
                "ai_service": "deepseek",
                "task_type": task_type.value,
                "processed": False,
                "error": str(e),
            }

    async def _call_claude(
        self, data: Dict[str, Any], task_type: AITaskType
    ) -> Dict[str, Any]:
        """Call Claude service for creative generation tasks"""
        from .llm_ai_engine import llm_ai_engine_service
        
        engine = llm_ai_engine_service
        
        prompt = self._build_prompt_for_task(task_type, data)
        
        try:
            result = await engine.generate_response(prompt, model="claude")
            return {
                "ai_service": "claude",
                "task_type": task_type.value,
                "processed": True,
                "result": result,
            }
        except Exception as e:
            logger.error(f"Claude processing error: {e}")
            return {
                "ai_service": "claude",
                "task_type": task_type.value,
                "processed": False,
                "error": str(e),
            }

    async def _process_hybrid(
        self, data: Dict[str, Any], task_type: AITaskType
    ) -> Dict[str, Any]:
        """Process tasks requiring both DeepSeek and Claude"""
        platform_result = await self._call_deepseek(data, task_type)
        
        enriched_data = {**data, "platform_insights": platform_result}
        enriched_result = await self._call_claude(enriched_data, task_type)

        return {
            "ai_service": "hybrid",
            "task_type": task_type.value,
            "deepseek_phase": platform_result,
            "claude_phase": enriched_result,
        }

    def _build_prompt_for_task(
        self, task_type: AITaskType, data: Dict[str, Any]
    ) -> str:
        """Build appropriate prompt based on task type"""
        prompts = {
            AITaskType.PLATFORM_COORDINATION: f"Analyze and coordinate the following platform data: {data}",
            AITaskType.OPPORTUNITY_VALIDATION: f"Validate this business opportunity: {data}",
            AITaskType.CONTENT_REWRITING: f"Rewrite this content professionally: {data}",
            AITaskType.BUSINESS_PLAN_GENERATION: f"Generate a comprehensive business plan for: {data}",
            AITaskType.MARKET_RESEARCH: f"Conduct market research analysis for: {data}",
            AITaskType.IDEA_ANALYSIS: f"Analyze this business idea: {data}",
            AITaskType.DOCUMENT_GENERATION: f"Generate a professional document for: {data}",
            AITaskType.LEAD_SCORING: f"Score this lead based on quality indicators: {data}",
            AITaskType.EXPERT_MATCHING: f"Find expert matches for this opportunity: {data}",
        }
        return prompts.get(task_type, f"Process this data: {data}")


ai_orchestrator = AIOrchestrator()
