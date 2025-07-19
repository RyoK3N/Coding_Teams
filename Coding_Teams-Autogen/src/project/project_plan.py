from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from datetime import datetime
from enum import Enum

class StepStatus(Enum):
    PENDING = "PENDING"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"
    BLOCKED = "BLOCKED"
    FAILED = "FAILED"

@dataclass
class ProjectStep:
    step_id: str
    name: str
    description: str
    owner: str
    assisting_agents: List[str] = field(default_factory=list)
    dependencies: List[str] = field(default_factory=list)
    deliverables: List[str] = field(default_factory=list)
    acceptance_criteria: List[str] = field(default_factory=list)
    status: StepStatus = StepStatus.PENDING
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    artifacts: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def start_step(self):
        self.status = StepStatus.IN_PROGRESS
        self.start_time = datetime.now()
        
    def complete_step(self, artifacts: List[str] = None):
        self.status = StepStatus.COMPLETED
        self.end_time = datetime.now()
        if artifacts:
            self.artifacts.extend(artifacts)
            
    def block_step(self, reason: str):
        self.status = StepStatus.BLOCKED
        self.metadata["block_reason"] = reason
        
    def fail_step(self, reason: str):
        self.status = StepStatus.FAILED
        self.metadata["failure_reason"] = reason

@dataclass
class ProjectPlan:
    project_name: str
    description: str
    steps: List[ProjectStep] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def add_step(self, step: ProjectStep):
        self.steps.append(step)
        
    def get_step_by_id(self, step_id: str) -> Optional[ProjectStep]:
        for step in self.steps:
            if step.step_id == step_id:
                return step
        return None
        
    def get_next_step(self) -> Optional[ProjectStep]:
        for step in self.steps:
            if step.status == StepStatus.PENDING:
                # Check if all dependencies are completed
                dependencies_met = all(
                    self.get_step_by_id(dep_id).status == StepStatus.COMPLETED
                    for dep_id in step.dependencies
                )
                if dependencies_met:
                    return step
        return None
        
    def get_current_step(self) -> Optional[ProjectStep]:
        for step in self.steps:
            if step.status == StepStatus.IN_PROGRESS:
                return step
        return None
        
    def is_complete(self) -> bool:
        return all(step.status == StepStatus.COMPLETED for step in self.steps)
        
    def get_progress_summary(self) -> Dict[str, Any]:
        total_steps = len(self.steps)
        completed_steps = sum(1 for step in self.steps if step.status == StepStatus.COMPLETED)
        in_progress_steps = sum(1 for step in self.steps if step.status == StepStatus.IN_PROGRESS)
        blocked_steps = sum(1 for step in self.steps if step.status == StepStatus.BLOCKED)
        failed_steps = sum(1 for step in self.steps if step.status == StepStatus.FAILED)
        
        return {
            "total_steps": total_steps,
            "completed_steps": completed_steps,
            "in_progress_steps": in_progress_steps,
            "blocked_steps": blocked_steps,
            "failed_steps": failed_steps,
            "progress_percentage": (completed_steps / total_steps * 100) if total_steps > 0 else 0
        }
        
    def to_dict(self) -> Dict[str, Any]:
        return {
            "project_name": self.project_name,
            "description": self.description,
            "created_at": self.created_at.isoformat(),
            "metadata": self.metadata,
            "steps": [
                {
                    "step_id": step.step_id,
                    "name": step.name,
                    "description": step.description,
                    "owner": step.owner,
                    "assisting_agents": step.assisting_agents,
                    "dependencies": step.dependencies,
                    "deliverables": step.deliverables,
                    "acceptance_criteria": step.acceptance_criteria,
                    "status": step.status.value,
                    "start_time": step.start_time.isoformat() if step.start_time else None,
                    "end_time": step.end_time.isoformat() if step.end_time else None,
                    "artifacts": step.artifacts,
                    "metadata": step.metadata
                }
                for step in self.steps
            ]
        } 