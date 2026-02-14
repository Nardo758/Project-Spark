import logging
from datetime import datetime
from typing import Optional, Dict, Any, List
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func

from app.models.enhanced_workspace import (
    EnhancedUserWorkspace, EnhancedWorkflowStage, EnhancedWorkflowTask,
    EnhancedResearchArtifact, WorkflowType, EnhancedWorkflowStatus,
    ArtifactType, WORKFLOW_TEMPLATES
)
from app.models.opportunity import Opportunity
from app.models.workspace import UserWorkspace

logger = logging.getLogger(__name__)


class EnhancedWorkspaceService:
    def __init__(self, db: Session):
        self.db = db

    def get_workspace(self, workspace_id: int, user_id: int) -> Optional[EnhancedUserWorkspace]:
        return self.db.query(EnhancedUserWorkspace).options(
            joinedload(EnhancedUserWorkspace.stages).joinedload(EnhancedWorkflowStage.tasks),
            joinedload(EnhancedUserWorkspace.artifacts),
        ).filter(
            EnhancedUserWorkspace.id == workspace_id,
            EnhancedUserWorkspace.user_id == user_id
        ).first()

    def list_workspaces(self, user_id: int, skip: int = 0, limit: int = 20) -> tuple:
        query = self.db.query(EnhancedUserWorkspace).filter(
            EnhancedUserWorkspace.user_id == user_id
        ).order_by(EnhancedUserWorkspace.updated_at.desc())

        total = query.count()
        workspaces = query.options(
            joinedload(EnhancedUserWorkspace.stages).joinedload(EnhancedWorkflowStage.tasks),
            joinedload(EnhancedUserWorkspace.artifacts),
        ).offset(skip).limit(limit).all()

        return workspaces, total

    def create_workspace(
        self,
        user_id: int,
        opportunity_id: int,
        workflow_type: WorkflowType,
        custom_title: Optional[str] = None,
        description: Optional[str] = None,
        custom_stages: Optional[List[dict]] = None
    ) -> EnhancedUserWorkspace:
        opportunity = self.db.query(Opportunity).filter(Opportunity.id == opportunity_id).first()
        if not opportunity:
            raise ValueError("Opportunity not found")

        existing = self.db.query(EnhancedUserWorkspace).filter(
            EnhancedUserWorkspace.user_id == user_id,
            EnhancedUserWorkspace.opportunity_id == opportunity_id
        ).first()
        if existing:
            raise ValueError("Enhanced workspace already exists for this opportunity")

        base_workspace = self.db.query(UserWorkspace).filter(
            UserWorkspace.user_id == user_id,
            UserWorkspace.opportunity_id == opportunity_id
        ).first()

        workspace = EnhancedUserWorkspace(
            user_id=user_id,
            opportunity_id=opportunity_id,
            workspace_id=base_workspace.id if base_workspace else None,
            custom_title=custom_title or opportunity.title,
            description=description,
            workflow_type=workflow_type,
            status=EnhancedWorkflowStatus.NOT_STARTED,
            progress_percent=0,
        )
        self.db.add(workspace)
        self.db.flush()

        if workflow_type == WorkflowType.CUSTOM and custom_stages:
            self._create_custom_stages(workspace, custom_stages)
        elif workflow_type in WORKFLOW_TEMPLATES:
            self._create_template_stages(workspace, WORKFLOW_TEMPLATES[workflow_type])

        if workspace.stages:
            workspace.current_stage = workspace.stages[0].name

        self.db.commit()
        self.db.refresh(workspace)
        return workspace

    def _create_template_stages(self, workspace: EnhancedUserWorkspace, template: dict):
        for stage_def in template["stages"]:
            stage = EnhancedWorkflowStage(
                workspace_id=workspace.id,
                name=stage_def["name"],
                description=stage_def.get("description", ""),
                stage_order=stage_def["order"],
                status=EnhancedWorkflowStatus.NOT_STARTED,
            )
            self.db.add(stage)
            self.db.flush()

            for i, task_title in enumerate(stage_def.get("tasks", [])):
                task = EnhancedWorkflowTask(
                    stage_id=stage.id,
                    workspace_id=workspace.id,
                    title=task_title,
                    sort_order=i,
                )
                self.db.add(task)

    def _create_custom_stages(self, workspace: EnhancedUserWorkspace, stages: List[dict]):
        for i, stage_def in enumerate(stages):
            stage = EnhancedWorkflowStage(
                workspace_id=workspace.id,
                name=stage_def.get("name", f"Stage {i + 1}"),
                description=stage_def.get("description", ""),
                stage_order=i + 1,
                status=EnhancedWorkflowStatus.NOT_STARTED,
            )
            self.db.add(stage)
            self.db.flush()

            for j, task_title in enumerate(stage_def.get("tasks", [])):
                task = EnhancedWorkflowTask(
                    stage_id=stage.id,
                    workspace_id=workspace.id,
                    title=task_title if isinstance(task_title, str) else task_title.get("title", ""),
                    sort_order=j,
                )
                self.db.add(task)

    def update_workspace(self, workspace_id: int, user_id: int, updates: dict) -> Optional[EnhancedUserWorkspace]:
        workspace = self.db.query(EnhancedUserWorkspace).filter(
            EnhancedUserWorkspace.id == workspace_id,
            EnhancedUserWorkspace.user_id == user_id
        ).first()
        if not workspace:
            return None

        for key, value in updates.items():
            if value is not None and hasattr(workspace, key):
                setattr(workspace, key, value)

        workspace.last_activity_at = func.now()
        self.db.commit()
        self.db.refresh(workspace)
        return workspace

    def complete_task(self, workspace_id: int, task_id: int, user_id: int, is_completed: bool = True) -> Optional[EnhancedWorkflowTask]:
        workspace = self.db.query(EnhancedUserWorkspace).filter(
            EnhancedUserWorkspace.id == workspace_id,
            EnhancedUserWorkspace.user_id == user_id
        ).first()
        if not workspace:
            return None

        task = self.db.query(EnhancedWorkflowTask).filter(
            EnhancedWorkflowTask.id == task_id,
            EnhancedWorkflowTask.workspace_id == workspace_id
        ).first()
        if not task:
            return None

        task.is_completed = is_completed
        task.completed_at = datetime.utcnow() if is_completed else None

        self._update_progress(workspace)
        workspace.last_activity_at = func.now()

        if workspace.status == EnhancedWorkflowStatus.NOT_STARTED:
            workspace.status = EnhancedWorkflowStatus.IN_PROGRESS
            workspace.started_at = datetime.utcnow()

        self.db.commit()
        self.db.refresh(task)
        return task

    def add_task(self, workspace_id: int, stage_id: int, user_id: int, title: str, description: Optional[str] = None) -> Optional[EnhancedWorkflowTask]:
        workspace = self.db.query(EnhancedUserWorkspace).filter(
            EnhancedUserWorkspace.id == workspace_id,
            EnhancedUserWorkspace.user_id == user_id
        ).first()
        if not workspace:
            return None

        stage = self.db.query(EnhancedWorkflowStage).filter(
            EnhancedWorkflowStage.id == stage_id,
            EnhancedWorkflowStage.workspace_id == workspace_id
        ).first()
        if not stage:
            return None

        max_order = self.db.query(func.max(EnhancedWorkflowTask.sort_order)).filter(
            EnhancedWorkflowTask.stage_id == stage_id
        ).scalar() or 0

        task = EnhancedWorkflowTask(
            stage_id=stage_id,
            workspace_id=workspace_id,
            title=title,
            description=description,
            sort_order=max_order + 1,
        )
        self.db.add(task)
        self.db.commit()
        self.db.refresh(task)
        return task

    def create_artifact(
        self, workspace_id: int, user_id: int,
        artifact_type: ArtifactType, title: str,
        content: Optional[dict] = None, summary: Optional[str] = None,
        tags: Optional[list] = None, source: Optional[str] = None
    ) -> Optional[EnhancedResearchArtifact]:
        workspace = self.db.query(EnhancedUserWorkspace).filter(
            EnhancedUserWorkspace.id == workspace_id,
            EnhancedUserWorkspace.user_id == user_id
        ).first()
        if not workspace:
            return None

        artifact = EnhancedResearchArtifact(
            workspace_id=workspace_id,
            artifact_type=artifact_type,
            title=title,
            content=content,
            summary=summary,
            tags=tags,
            source=source,
        )
        self.db.add(artifact)
        workspace.last_activity_at = func.now()
        self.db.commit()
        self.db.refresh(artifact)
        return artifact

    def delete_artifact(self, workspace_id: int, artifact_id: int, user_id: int) -> bool:
        workspace = self.db.query(EnhancedUserWorkspace).filter(
            EnhancedUserWorkspace.id == workspace_id,
            EnhancedUserWorkspace.user_id == user_id
        ).first()
        if not workspace:
            return False

        artifact = self.db.query(EnhancedResearchArtifact).filter(
            EnhancedResearchArtifact.id == artifact_id,
            EnhancedResearchArtifact.workspace_id == workspace_id
        ).first()
        if not artifact:
            return False

        self.db.delete(artifact)
        self.db.commit()
        return True

    def get_analytics(self, workspace_id: int, user_id: int) -> Optional[dict]:
        workspace = self.get_workspace(workspace_id, user_id)
        if not workspace:
            return None

        all_tasks = []
        stage_progress = []
        for stage in workspace.stages:
            completed = sum(1 for t in stage.tasks if t.is_completed)
            total = len(stage.tasks)
            stage_progress.append({
                "stage_id": stage.id,
                "name": stage.name,
                "order": stage.stage_order,
                "status": stage.status.value if hasattr(stage.status, 'value') else stage.status,
                "total_tasks": total,
                "completed_tasks": completed,
                "progress": round((completed / total * 100) if total > 0 else 0),
            })
            all_tasks.extend(stage.tasks)

        artifacts_by_type = {}
        for artifact in workspace.artifacts:
            atype = artifact.artifact_type.value if hasattr(artifact.artifact_type, 'value') else artifact.artifact_type
            artifacts_by_type[atype] = artifacts_by_type.get(atype, 0) + 1

        total_tasks = len(all_tasks)
        completed_tasks = sum(1 for t in all_tasks if t.is_completed)

        return {
            "workspace_id": workspace_id,
            "total_tasks": total_tasks,
            "completed_tasks": completed_tasks,
            "completion_rate": round((completed_tasks / total_tasks * 100) if total_tasks > 0 else 0, 1),
            "total_artifacts": len(workspace.artifacts),
            "artifacts_by_type": artifacts_by_type,
            "stage_progress": stage_progress,
            "validation_score": workspace.validation_score,
            "ai_recommendations": workspace.ai_recommendations,
        }

    def generate_ai_insight(self, workspace_id: int, user_id: int, insight_type: str, context: Optional[dict] = None) -> Optional[dict]:
        workspace = self.get_workspace(workspace_id, user_id)
        if not workspace:
            return None

        opportunity = workspace.opportunity
        opp_context = {
            "title": opportunity.title if opportunity else "Unknown",
            "category": opportunity.category if opportunity else "Unknown",
            "description": opportunity.description if opportunity else "",
        }

        all_tasks = []
        for stage in workspace.stages:
            for task in stage.tasks:
                all_tasks.append({"title": task.title, "completed": task.is_completed, "stage": stage.name})

        workspace_context = {
            "workflow_type": workspace.workflow_type.value if hasattr(workspace.workflow_type, 'value') else workspace.workflow_type,
            "progress": workspace.progress_percent,
            "current_stage": workspace.current_stage,
            "tasks": all_tasks,
            "artifacts_count": len(workspace.artifacts),
        }

        insight_generators = {
            "summary": self._generate_summary,
            "recommendations": self._generate_recommendations,
            "validation_score": self._generate_validation_score,
            "interview_guide": self._generate_interview_guide,
            "survey_questions": self._generate_survey_questions,
            "competitor_analysis": self._generate_competitor_analysis,
            "financial_model": self._generate_financial_model,
        }

        generator = insight_generators.get(insight_type)
        if not generator:
            return {"insight_type": insight_type, "content": {"error": f"Unknown insight type: {insight_type}"}, "confidence": 0}

        try:
            result = generator(opp_context, workspace_context, context or {})
            return {
                "insight_type": insight_type,
                "content": result,
                "confidence": result.get("confidence", 0.7),
                "generated_at": datetime.utcnow().isoformat(),
            }
        except Exception as e:
            logger.error(f"AI insight generation failed: {e}")
            return {"insight_type": insight_type, "content": {"error": str(e)}, "confidence": 0}

    def _generate_summary(self, opp: dict, ws: dict, ctx: dict) -> dict:
        completed = sum(1 for t in ws["tasks"] if t["completed"])
        total = len(ws["tasks"])
        stages_done = set()
        for t in ws["tasks"]:
            if t["completed"]:
                stages_done.add(t["stage"])

        return {
            "opportunity": opp["title"],
            "category": opp["category"],
            "workflow": ws["workflow_type"].replace("_", " ").title(),
            "overall_progress": ws["progress"],
            "tasks_completed": f"{completed}/{total}",
            "stages_with_progress": list(stages_done),
            "current_focus": ws["current_stage"] or "Not started",
            "key_findings": [
                f"Working on {opp['title']} in {opp['category']} category",
                f"Using {ws['workflow_type'].replace('_', ' ').title()} workflow",
                f"Completed {completed} of {total} tasks ({ws['progress']}%)",
                f"Created {ws['artifacts_count']} research artifacts",
            ],
            "next_steps": self._suggest_next_steps(ws),
            "confidence": 0.85,
        }

    def _generate_recommendations(self, opp: dict, ws: dict, ctx: dict) -> dict:
        recommendations = []
        incomplete_stages = {}
        for t in ws["tasks"]:
            if not t["completed"]:
                incomplete_stages.setdefault(t["stage"], []).append(t["title"])

        for stage, tasks in incomplete_stages.items():
            recommendations.append({
                "priority": "high" if len(tasks) > 2 else "medium",
                "area": stage,
                "suggestion": f"Focus on completing {len(tasks)} remaining tasks in {stage}",
                "tasks": tasks[:3],
            })

        if ws["artifacts_count"] < 3:
            recommendations.append({
                "priority": "medium",
                "area": "Research",
                "suggestion": "Add more research artifacts to strengthen your validation",
                "tasks": ["Conduct customer interviews", "Gather market data", "Document competitor findings"],
            })

        return {"recommendations": recommendations, "total_suggestions": len(recommendations), "confidence": 0.75}

    def _generate_validation_score(self, opp: dict, ws: dict, ctx: dict) -> dict:
        completed = sum(1 for t in ws["tasks"] if t["completed"])
        total = len(ws["tasks"])
        task_score = (completed / total * 40) if total > 0 else 0
        artifact_score = min(30, ws["artifacts_count"] * 6)
        progress_score = ws["progress"] * 0.3

        total_score = round(task_score + artifact_score + progress_score)

        return {
            "overall_score": min(100, total_score),
            "breakdown": {
                "task_completion": round(task_score),
                "research_depth": round(artifact_score),
                "progress": round(progress_score),
            },
            "rating": "Strong" if total_score >= 70 else "Moderate" if total_score >= 40 else "Early Stage",
            "confidence": 0.7,
        }

    def _generate_interview_guide(self, opp: dict, ws: dict, ctx: dict) -> dict:
        return {
            "title": f"Interview Guide: {opp['title']}",
            "target_audience": ctx.get("audience", "Potential customers"),
            "duration": "30-45 minutes",
            "sections": [
                {
                    "name": "Opening & Context",
                    "duration": "5 min",
                    "questions": [
                        f"Can you tell me about your experience with {opp['category'].lower()}?",
                        "Walk me through a typical day/week when you encounter this problem.",
                        "How long have you been dealing with this challenge?",
                    ]
                },
                {
                    "name": "Problem Exploration",
                    "duration": "15 min",
                    "questions": [
                        "What's the biggest frustration you face in this area?",
                        "How does this problem affect your work/life?",
                        "What have you tried to solve it? What worked and what didn't?",
                        "How much time/money do you currently spend on this?",
                    ]
                },
                {
                    "name": "Solution Feedback",
                    "duration": "10 min",
                    "questions": [
                        "If you could wave a magic wand, what would the ideal solution look like?",
                        "What features would be most important to you?",
                        "What would make you switch from your current approach?",
                    ]
                },
                {
                    "name": "Closing",
                    "duration": "5 min",
                    "questions": [
                        "Is there anything else you'd like to share about this topic?",
                        "Would you be interested in testing a solution when it's ready?",
                        "Can you recommend others who face similar challenges?",
                    ]
                },
            ],
            "tips": [
                "Listen more than you talk (80/20 rule)",
                "Ask follow-up questions: 'Tell me more about that'",
                "Take notes on emotions, not just facts",
                "Avoid leading questions or pitching your solution",
            ],
            "confidence": 0.85,
        }

    def _generate_survey_questions(self, opp: dict, ws: dict, ctx: dict) -> dict:
        return {
            "title": f"Validation Survey: {opp['title']}",
            "estimated_time": "5-7 minutes",
            "target_responses": 50,
            "sections": [
                {
                    "name": "Demographics",
                    "questions": [
                        {"type": "multiple_choice", "question": "What best describes your role?", "options": ["Individual", "Small business owner", "Manager", "Executive", "Other"]},
                        {"type": "multiple_choice", "question": f"How often do you encounter issues related to {opp['category'].lower()}?", "options": ["Daily", "Weekly", "Monthly", "Rarely", "Never"]},
                    ]
                },
                {
                    "name": "Problem Validation",
                    "questions": [
                        {"type": "scale", "question": "How significant is this problem for you? (1-10)", "min": 1, "max": 10},
                        {"type": "multiple_choice", "question": "How do you currently solve this?", "options": ["Manual process", "Existing software", "Hire someone", "Don't solve it", "Other"]},
                        {"type": "scale", "question": "How satisfied are you with current solutions? (1-10)", "min": 1, "max": 10},
                    ]
                },
                {
                    "name": "Willingness to Pay",
                    "questions": [
                        {"type": "multiple_choice", "question": "How much would you pay monthly for a solution?", "options": ["Free only", "$1-10", "$11-50", "$51-100", "$100+"]},
                        {"type": "scale", "question": "How likely would you be to try a new solution? (1-10)", "min": 1, "max": 10},
                    ]
                },
            ],
            "confidence": 0.80,
        }

    def _generate_competitor_analysis(self, opp: dict, ws: dict, ctx: dict) -> dict:
        return {
            "title": f"Competitive Landscape: {opp['title']}",
            "framework": "Porter's Five Forces + Direct Competitors",
            "analysis_areas": [
                {
                    "area": "Direct Competitors",
                    "description": "Companies solving the same problem",
                    "action_items": ["Research top 5 competitors", "Compare pricing models", "Analyze feature sets", "Read customer reviews"],
                },
                {
                    "area": "Indirect Competitors",
                    "description": "Alternative approaches to solving the problem",
                    "action_items": ["Identify workaround solutions", "Map substitute products", "Analyze DIY approaches"],
                },
                {
                    "area": "Market Position",
                    "description": "Where you can differentiate",
                    "action_items": ["Define unique value proposition", "Identify underserved segments", "Find pricing gaps"],
                },
            ],
            "comparison_template": {
                "columns": ["Company", "Pricing", "Key Features", "Target Market", "Strengths", "Weaknesses"],
                "rows": [],
            },
            "confidence": 0.75,
        }

    def _generate_financial_model(self, opp: dict, ws: dict, ctx: dict) -> dict:
        return {
            "title": f"Financial Projections: {opp['title']}",
            "timeframe": "12 months",
            "model_type": "SaaS/Subscription",
            "assumptions": {
                "monthly_growth_rate": "15-20%",
                "churn_rate": "5-8%",
                "average_revenue_per_user": "$29-99/mo",
                "customer_acquisition_cost": "$50-200",
            },
            "revenue_projections": {
                "month_3": {"customers": 50, "mrr": 2500},
                "month_6": {"customers": 200, "mrr": 12000},
                "month_12": {"customers": 800, "mrr": 56000},
            },
            "key_metrics": [
                {"metric": "LTV/CAC Ratio", "target": "> 3:1", "description": "Customer lifetime value vs acquisition cost"},
                {"metric": "Payback Period", "target": "< 12 months", "description": "Time to recover CAC"},
                {"metric": "Gross Margin", "target": "> 70%", "description": "Revenue minus cost of goods sold"},
                {"metric": "Burn Rate", "target": "< $10k/mo", "description": "Monthly cash expenditure"},
            ],
            "action_items": [
                "Validate pricing with 10 potential customers",
                "Calculate actual CAC from initial marketing tests",
                "Build detailed cost structure",
                "Model 3 scenarios: conservative, moderate, optimistic",
            ],
            "confidence": 0.65,
        }

    def _suggest_next_steps(self, ws: dict) -> list:
        steps = []
        for t in ws["tasks"]:
            if not t["completed"]:
                steps.append(f"Complete: {t['title']} ({t['stage']})")
                if len(steps) >= 3:
                    break
        if not steps:
            steps.append("All tasks completed! Review your findings and prepare for the next phase.")
        return steps

    def _update_progress(self, workspace: EnhancedUserWorkspace):
        all_tasks = self.db.query(EnhancedWorkflowTask).filter(
            EnhancedWorkflowTask.workspace_id == workspace.id
        ).all()

        if not all_tasks:
            return

        completed = sum(1 for t in all_tasks if t.is_completed)
        workspace.progress_percent = round(completed / len(all_tasks) * 100)

        for stage in workspace.stages:
            stage_tasks = [t for t in all_tasks if t.stage_id == stage.id]
            if stage_tasks:
                stage_completed = sum(1 for t in stage_tasks if t.is_completed)
                stage.progress_percent = round(stage_completed / len(stage_tasks) * 100)

                if stage_completed == len(stage_tasks):
                    stage.status = EnhancedWorkflowStatus.COMPLETED
                    stage.completed_at = datetime.utcnow()
                elif stage_completed > 0:
                    stage.status = EnhancedWorkflowStatus.IN_PROGRESS
                    if not stage.started_at:
                        stage.started_at = datetime.utcnow()

        if workspace.progress_percent == 100:
            workspace.status = EnhancedWorkflowStatus.COMPLETED
            workspace.completed_at = datetime.utcnow()
