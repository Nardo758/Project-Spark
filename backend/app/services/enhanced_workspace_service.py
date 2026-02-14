# 🚀 ENHANCED WORKSPACE SERVICE
# Production-ready service layer for OppGrid enhanced workspace

from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
from datetime import datetime

from app.models.enhanced_workspace import (
    EnhancedUserWorkspace, EnhancedWorkflowStage, EnhancedWorkflowTask,
    EnhancedResearchArtifact, CustomWorkflow, WorkflowType, WorkflowStatus,
    ResearchArtifactType, ResearchArtifactStatus
)
from app.services.ai_orchestrator import AIOrchestrator

class EnhancedWorkspaceService:
    def __init__(self, db: Session):
        self.db = db
        self.ai_service = AIOrchestrator()

    def create_enhanced_workspace(self, user_id: int, opportunity_id: int, 
                                workflow_type: WorkflowType = WorkflowType.CUSTOM,
                                custom_title: Optional[str] = None) -> EnhancedUserWorkspace:
        """Create enhanced workspace with custom workflow"""
        
        # Create enhanced workspace
        workspace = EnhancedUserWorkspace(
            user_id=user_id,
            opportunity_id=opportunity_id,
            custom_title=custom_title,
            workflow_type=workflow_type,
            status=WorkflowStatus.NOT_STARTED,
            progress_percent=0
        )
        
        self.db.add(workspace)
        self.db.flush()
        
        # Initialize workflow based on type
        self._initialize_workflow_stages(workspace, workflow_type)
        
        return workspace

    def _initialize_workflow_stages(self, workspace: EnhancedUserWorkspace, workflow_type: WorkflowType):
        """Initialize workflow stages based on type"""
        
        workflow_configs = {
            WorkflowType.LEAN_VALIDATION: [
                {"name": "Problem Validation", "description": "Validate the problem exists", "duration_weeks": 2},
                {"name": "Market Research", "description": "Research market size and trends", "duration_weeks": 2},
                {"name": "Customer Discovery", "description": "Interview potential customers", "duration_weeks": 3},
                {"name": "Solution Validation", "description": "Validate solution with customers", "duration_weeks": 3}
            ],
            WorkflowType.ENTERPRISE_B2B: [
                {"name": "Enterprise Research", "description": "Research enterprise landscape", "duration_weeks": 2},
                {"name": "Stakeholder Analysis", "description": "Identify key stakeholders", "duration_weeks": 2},
                {"name": "Decision Process", "description": "Understand decision-making process", "duration_weeks": 3},
                {"name": "Procurement Analysis", "description": "Analyze procurement requirements", "duration_weeks": 3}
            ],
            WorkflowType.PRODUCT_MARKET_FIT: [
                {"name": "Market Analysis", "description": "Analyze market opportunities", "duration_weeks": 2},
                {"name": "Customer Segmentation", "description": "Segment target customers", "duration_weeks": 2},
                {"name": "Product Testing", "description": "Test product with users", "duration_weeks": 3},
                {"name": "Market Validation", "description": "Validate market fit", "duration_weeks": 3}
            ],
            WorkflowType.CUSTOM: [
                {"name": "Validate", "description": "Validate the core problem and demand", "duration_weeks": 2},
                {"name": "Research", "description": "Research market, users, and competitors", "duration_weeks": 2},
                {"name": "Plan", "description": "Define solution strategy and milestones", "duration_weeks": 2},
                {"name": "Execute", "description": "Run implementation and launch tasks", "duration_weeks": 4}
            ]
        }
        
        stages_config = workflow_configs.get(workflow_type, workflow_configs[WorkflowType.LEAN_VALIDATION])
        
        for idx, stage_config in enumerate(stages_config):
            stage = EnhancedWorkflowStage(
                workspace_id=workspace.id,
                name=stage_config["name"],
                description=stage_config["description"],
                order_index=idx,
                duration_weeks=stage_config.get("duration_weeks"),
                status=WorkflowStatus.NOT_STARTED
            )
            self.db.add(stage)
            
            # Add default tasks for each stage
            self._add_default_tasks(stage, workflow_type, idx)

    def _add_default_tasks(self, stage: EnhancedWorkflowStage, workflow_type: WorkflowType, stage_index: int):
        """Add default tasks for each stage"""
        
        task_configs = {
            WorkflowType.LEAN_VALIDATION: {
                0: [  # Problem Validation
                    {"name": "Define Problem Statement", "description": "Clearly define the problem you're solving"},
                    {"name": "Problem Hypothesis", "description": "Formulate hypothesis about the problem"},
                    {"name": "Initial Market Research", "description": "Conduct initial market research"}
                ],
                1: [  # Market Research
                    {"name": "Market Size Analysis", "description": "Analyze total addressable market"},
                    {"name": "Competitor Analysis", "description": "Research existing competitors"},
                    {"name": "Industry Trends", "description": "Analyze industry trends and patterns"}
                ],
                2: [  # Customer Discovery
                    {"name": "Customer Interview Plan", "description": "Plan customer interview strategy"},
                    {"name": "Conduct Interviews", "description": "Interview potential customers"},
                    {"name": "Interview Analysis", "description": "Analyze interview insights"}
                ],
                3: [  # Solution Validation
                    {"name": "Solution Prototype", "description": "Create solution prototype"},
                    {"name": "Customer Testing", "description": "Test solution with customers"},
                    {"name": "Feedback Analysis", "description": "Analyze customer feedback"}
                ]
            }
        }
        
        stage_tasks = task_configs.get(workflow_type, {}).get(stage_index, [])
        
        for idx, task_config in enumerate(stage_tasks):
            task = EnhancedWorkflowTask(
                stage=stage,
                name=task_config["name"],
                description=task_config["description"],
                sort_order=idx
            )
            self.db.add(task)

    def create_research_artifact(self, workspace_id: int, stage_id: Optional[int], 
                               name: str, artifact_type: ResearchArtifactType,
                               content: Optional[str] = None, **kwargs) -> EnhancedResearchArtifact:
        """Create research artifact with AI insights"""
        if "metadata" in kwargs and "artifact_metadata" not in kwargs:
            kwargs["artifact_metadata"] = kwargs.pop("metadata")
        
        artifact = EnhancedResearchArtifact(
            workspace_id=workspace_id,
            stage_id=stage_id,
            name=name,
            artifact_type=artifact_type,
            content=content,
            **kwargs
        )
        
        # Generate AI insights based on artifact type
        if content:
            artifact.ai_insights = self._generate_ai_insights(artifact_type, content)
            artifact.ai_summary = self._generate_ai_summary(content)
            artifact.ai_recommendations = self._generate_ai_recommendations(artifact_type, content)
        
        self.db.add(artifact)
        self.db.flush()
        
        return artifact

    def _generate_ai_insights(self, artifact_type: ResearchArtifactType, content: str) -> Dict[str, Any]:
        """Generate AI insights based on artifact type"""
        
        if artifact_type == ResearchArtifactType.INTERVIEW:
            # Extract themes and sentiment from interview content
            return self.ai_service.extract_interview_insights(content)
        elif artifact_type == ResearchArtifactType.SURVEY:
            # Analyze survey responses
            return self.ai_service.analyze_survey_responses(content)
        elif artifact_type == ResearchArtifactType.COMPETITOR:
            # Analyze competitor data
            return self.ai_service.analyze_competitor_data(content)
        elif artifact_type == ResearchArtifactType.MARKET:
            # Analyze market data
            return self.ai_service.analyze_market_data(content)
        
        return {}

    def _generate_ai_summary(self, content: str) -> str:
        """Generate AI summary of content"""
        return self.ai_service.generate_summary(content)

    def _generate_ai_recommendations(self, artifact_type: ResearchArtifactType, content: str) -> Dict[str, Any]:
        """Generate AI recommendations based on artifact type"""
        
        if artifact_type == ResearchArtifactType.INTERVIEW:
            return self.ai_service.generate_interview_recommendations(content)
        elif artifact_type == ResearchArtifactType.SURVEY:
            return self.ai_service.generate_survey_recommendations(content)
        elif artifact_type == ResearchArtifactType.COMPETITOR:
            return self.ai_service.generate_competitor_recommendations(content)
        
        return {}

    def update_workspace_progress(self, workspace_id: int) -> Dict[str, Any]:
        """Update workspace progress and validation scores"""
        
        workspace = self.db.query(EnhancedUserWorkspace).filter(
            EnhancedUserWorkspace.id == workspace_id
        ).first()
        
        if not workspace:
            return {"error": "Workspace not found"}
        
        # Calculate progress based on completed tasks
        total_tasks = 0
        completed_tasks = 0
        
        for stage in workspace.workflow_stages:
            for task in stage.tasks:
                total_tasks += 1
                if task.is_completed:
                    completed_tasks += 1
        
        progress_percent = int((completed_tasks / total_tasks * 100)) if total_tasks > 0 else 0
        workspace.progress_percent = progress_percent
        
        # Update validation score based on research artifacts
        workspace.validation_score = self._calculate_validation_score(workspace)
        
        # Update research summary
        workspace.research_summary = self._generate_research_summary(workspace)
        
        # Update AI recommendations
        workspace.ai_recommendations = self._generate_workspace_recommendations(workspace)
        
        self.db.commit()
        
        return {
            "progress_percent": progress_percent,
            "validation_score": workspace.validation_score,
            "research_summary": workspace.research_summary,
            "ai_recommendations": workspace.ai_recommendations
        }

    def _calculate_validation_score(self, workspace: EnhancedUserWorkspace) -> Dict[str, int]:
        """Calculate validation score based on research artifacts"""
        
        scores = {
            "problem": 0,
            "market": 0,
            "solution": 0,
            "competition": 0,
            "overall": 0
        }
        
        # Analyze research artifacts by type
        interview_count = 0
        survey_count = 0
        competitor_count = 0
        market_count = 0
        
        for artifact in workspace.research_artifacts:
            if artifact.artifact_type == ResearchArtifactType.INTERVIEW:
                interview_count += 1
            elif artifact.artifact_type == ResearchArtifactType.SURVEY:
                survey_count += 1
            elif artifact.artifact_type == ResearchArtifactType.COMPETITOR:
                competitor_count += 1
            elif artifact.artifact_type == ResearchArtifactType.MARKET:
                market_count += 1
        
        # Calculate scores based on research depth
        scores["problem"] = min(100, interview_count * 15 + survey_count * 10)
        scores["market"] = min(100, market_count * 20 + survey_count * 8)
        scores["solution"] = min(100, interview_count * 20)
        scores["competition"] = min(100, competitor_count * 25)
        
        # Calculate overall score
        scores["overall"] = int(
            (scores["problem"] + scores["market"] + scores["solution"] + scores["competition"]) / 4
        )
        
        return scores

    def _generate_research_summary(self, workspace: EnhancedUserWorkspace) -> Dict[str, Any]:
        """Generate research summary based on artifacts"""
        
        summary = {
            "total_artifacts": len(workspace.research_artifacts),
            "artifacts_by_type": {},
            "completed_stages": 0,
            "total_stages": len(workspace.workflow_stages),
            "active_research_areas": [],
            "key_insights": []
        }
        
        # Count artifacts by type
        for artifact in workspace.research_artifacts:
            artifact_type = artifact.artifact_type.value
            if artifact_type not in summary["artifacts_by_type"]:
                summary["artifacts_by_type"][artifact_type] = 0
            summary["artifacts_by_type"][artifact_type] += 1
        
        # Count completed stages
        for stage in workspace.workflow_stages:
            if stage.status == WorkflowStatus.COMPLETED:
                summary["completed_stages"] += 1
        
        # Extract key insights from AI insights
        for artifact in workspace.research_artifacts:
            if artifact.ai_insights and "key_insights" in artifact.ai_insights:
                summary["key_insights"].extend(artifact.ai_insights["key_insights"][:3])
        
        return summary

    def _generate_workspace_recommendations(self, workspace: EnhancedUserWorkspace) -> Dict[str, Any]:
        """Generate AI recommendations for workspace"""
        
        recommendations = {
            "next_steps": [],
            "priority_actions": [],
            "research_gaps": [],
            "validation_opportunities": []
        }
        
        # Analyze current progress and suggest next steps
        if workspace.progress_percent < 25:
            recommendations["next_steps"].append("Focus on problem validation through customer interviews")
            recommendations["priority_actions"].append("Conduct at least 10 customer interviews")
        elif workspace.progress_percent < 50:
            recommendations["next_steps"].append("Expand market research and competitor analysis")
            recommendations["priority_actions"].append("Complete comprehensive competitor analysis")
        elif workspace.progress_percent < 75:
            recommendations["next_steps"].append("Validate solution with potential customers")
            recommendations["priority_actions"].append("Create and test solution prototype")
        else:
            recommendations["next_steps"].append("Prepare for launch and scaling")
            recommendations["priority_actions"].append("Finalize go-to-market strategy")
        
        # Identify research gaps
        artifact_types = [a.artifact_type for a in workspace.research_artifacts]
        
        if ResearchArtifactType.INTERVIEW not in artifact_types:
            recommendations["research_gaps"].append("Customer interviews needed for problem validation")
        
        if ResearchArtifactType.COMPETITOR not in artifact_types:
            recommendations["research_gaps"].append("Competitor analysis needed for market positioning")
        
        if ResearchArtifactType.MARKET not in artifact_types:
            recommendations["research_gaps"].append("Market research needed for sizing and trends")
        
        return recommendations

    def get_workspace_analytics(self, workspace_id: int) -> Dict[str, Any]:
        """Get comprehensive workspace analytics"""
        
        workspace = self.db.query(EnhancedUserWorkspace).filter(
            EnhancedUserWorkspace.id == workspace_id
        ).first()
        
        if not workspace:
            return {"error": "Workspace not found"}
        
        # Calculate time-based metrics
        if workspace.started_at:
            days_active = (datetime.utcnow() - workspace.started_at).days
        else:
            days_active = 0
        
        # Calculate research velocity
        research_velocity = len(workspace.research_artifacts) / max(1, days_active)
        
        # Calculate completion rate
        total_tasks = sum(len(stage.tasks) for stage in workspace.workflow_stages)
        completed_tasks = sum(
            len([task for task in stage.tasks if task.is_completed]) 
            for stage in workspace.workflow_stages
        )
        completion_rate = (completed_tasks / max(1, total_tasks)) * 100
        
        return {
            "workspace_id": workspace_id,
            "days_active": days_active,
            "research_velocity": round(research_velocity, 2),
            "completion_rate": round(completion_rate, 2),
            "validation_score": workspace.validation_score,
            "research_summary": workspace.research_summary,
            "ai_recommendations": workspace.ai_recommendations,
            "progress_trend": self._calculate_progress_trend(workspace),
            "research_quality_score": self._calculate_research_quality_score(workspace)
        }

    def _calculate_progress_trend(self, workspace: EnhancedUserWorkspace) -> str:
        """Calculate progress trend based on recent activity"""
        
        # Simple trend calculation based on recent task completions
        recent_completions = 0
        for stage in workspace.workflow_stages:
            for task in stage.tasks:
                if task.completed_at and (datetime.utcnow() - task.completed_at).days <= 7:
                    recent_completions += 1
        
        if recent_completions >= 3:
            return "accelerating"
        elif recent_completions >= 1:
            return "steady"
        else:
            return "slowing"

    def _calculate_research_quality_score(self, workspace: EnhancedUserWorkspace) -> int:
        """Calculate research quality score based on artifact quality"""
        
        if not workspace.research_artifacts:
            return 0
        
        quality_factors = 0
        
        for artifact in workspace.research_artifacts:
            # Check for AI insights
            if artifact.ai_insights:
                quality_factors += 25
            
            # Check for AI summary
            if artifact.ai_summary:
                quality_factors += 25
            
            # Check for AI recommendations
            if artifact.ai_recommendations:
                quality_factors += 25
            
            # Check for content
            if artifact.content and len(artifact.content) > 100:
                quality_factors += 25
        
        return min(100, quality_factors // len(workspace.research_artifacts))