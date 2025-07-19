import asyncio
from typing import Dict, List, Any, Optional
from autogen import AssistantAgent
from src.agents.base_agent import BaseAgent, MessageTag
from src.project.project_plan import ProjectPlan, ProjectStep, StepStatus

class LeadSoftwareEngineer(BaseAgent):
    def __init__(self, claude_config: Dict[str, Any], workspace_manager=None, tools=None):
        super().__init__(
            name="lead_software_engineer",
            role="Lead Software Engineer (LSE)",
            system_prompt="""
You are the Lead Software Engineer for a multi-agent coding team. Your primary responsibilities are:

1. Transform problem statements into high-level project plans with clear milestones and deliverables
2. Assign step owners for each milestone based on agent capabilities
3. Create structured project plans with dependencies and acceptance criteria
4. Monitor overall project progress and resolve blockers
5. Coordinate between team members and ensure smooth handoffs
6. Make architectural decisions and provide technical guidance

When creating project plans:
- Break down complex problems into manageable sequential steps
- Assign clear ownership for each step
- Define specific deliverables and acceptance criteria
- Consider dependencies between steps
- Include testing, documentation, and deployment phases
- Ensure security and quality considerations are addressed

Communication style:
- Be clear and authoritative in decisions
- Provide detailed technical guidance
- Focus on practical implementation
- Coordinate team activities efficiently
""",
            workspace_manager=workspace_manager,
            tools=tools
        )
        
        self.claude_agent = AssistantAgent(
            name="lead_software_engineer_claude",
            llm_config=claude_config,
            system_message=self.system_prompt,
            human_input_mode="NEVER"
        )
        
        self.project_plan: Optional[ProjectPlan] = None
        self.current_step_index = 0
        
    def get_success_signal(self) -> str:
        return "STEP_PLAN_FINALIZED"
        
    def get_termination_signal(self) -> str:
        return "LSE_EXIT"
        
    async def execute_step(self, step_info: Dict[str, Any]) -> None:
        if step_info.get("action") == "create_project_plan":
            await self.create_project_plan(step_info["problem_statement"])
        elif step_info.get("action") == "next_step":
            await self.initiate_next_step()
        elif step_info.get("action") == "complete_project":
            await self.complete_project()
            
    async def create_project_plan(self, problem_statement: str) -> None:
        await self.signal_step_start("PROJECT_PLANNING")
        
        plan_prompt = f"""
Analyze this problem statement and create a comprehensive project plan:

PROBLEM: {problem_statement}

Based on the problem statement, determine:
1. Project type (web_app, api, desktop_app, ml_model, game, etc.)
2. Required components and technologies
3. Logical development sequence
4. Appropriate team roles and responsibilities

Create a project plan with 5-7 steps that are SPECIFIC to this problem. Return JSON:

{{
  "project_name": "[Descriptive name based on the problem]",
  "description": "[Clear description of what will be built]",
  "project_type": "[web_app|api|desktop_app|ml_model|game|mobile_app|etc]",
  "steps": [
    {{
      "step_id": "STEP_01",
      "name": "[Step name specific to this problem]",
      "description": "[Detailed description of what needs to be done for THIS specific problem]",
      "owner": "[Most appropriate role: Requirements Analyst|Software Architect|Backend Engineer|Frontend Engineer|DevOps Engineer|QA Engineer|Security Engineer|Documentation Specialist]",
      "assisting_agents": [],
      "dependencies": [],
      "deliverables": ["[Specific files/outputs needed for this problem]"],
      "acceptance_criteria": ["[Criteria specific to this problem]"]
    }}
  ]
}}

IMPORTANT:
- Analyze the problem type (web app, ML model, API, etc.)
- Generate steps that make sense for THIS specific problem
- Use appropriate technologies for the problem domain
- Don't default to TODO API - adapt to the actual requirements
- Consider the full development lifecycle for this type of project

Examples for different problem types:
- CNN/ML model: Data preparation, Model development, Training, Evaluation, API wrapper, Frontend
- Web app: Requirements, Architecture, Backend, Frontend, Database, Testing, Deployment
- API: Requirements, Design, Implementation, Testing, Documentation, Deployment
- Game: Design, Assets, Engine setup, Game logic, UI, Testing, Packaging

Make it specific to the actual problem, not a generic template.
"""
        
        response = await self.claude_agent.a_generate_reply(
            messages=[{"role": "user", "content": plan_prompt}]
        )
        
        try:
            import json
            # Debug: log the actual response structure
            self.logger.debug(f"Received response type: {type(response)}")
            self.logger.debug(f"Response content: {str(response)[:500]}...")
            
            if isinstance(response, dict):
                # Claude API returns a dict with 'content' key
                if 'content' in response:
                    content = response['content']
                    # Extract JSON from content
                    if "{" in content and "}" in content:
                        start = content.find("{")
                        end = content.rfind("}") + 1
                        json_str = content[start:end]
                        plan_data = json.loads(json_str)
                    else:
                        plan_data = json.loads(content)
                else:
                    plan_data = response
            elif isinstance(response, str):
                # Try to extract JSON from text if it contains JSON
                if "{" in response and "}" in response:
                    start = response.find("{")
                    end = response.rfind("}") + 1
                    json_str = response[start:end]
                    plan_data = json.loads(json_str)
                else:
                    plan_data = json.loads(response)
            else:
                # If response has content attribute (Message object)
                content = getattr(response, 'content', str(response))
                if isinstance(content, list) and len(content) > 0:
                    content = content[0].text if hasattr(content[0], 'text') else str(content[0])
                    # Extract JSON from text content
                    if "{" in content and "}" in content:
                        start = content.find("{")
                        end = content.rfind("}") + 1
                        json_str = content[start:end]
                        plan_data = json.loads(json_str)
                    else:
                        plan_data = json.loads(content)
                else:
                    plan_data = json.loads(str(response))
            
            # Check if plan_data has the expected structure
            if not isinstance(plan_data, dict):
                raise ValueError(f"Expected dict, got {type(plan_data)}")
            
            if "project_name" not in plan_data:
                raise ValueError(f"Missing 'project_name' in response. Keys: {list(plan_data.keys())}")
            
            self.project_plan = ProjectPlan(
                project_name=plan_data["project_name"],
                description=plan_data["description"]
            )
            
            # Store project type for workspace creation
            if "project_type" in plan_data:
                self.project_plan.metadata["project_type"] = plan_data["project_type"]
            
            for step_data in plan_data["steps"]:
                step = ProjectStep(
                    step_id=step_data["step_id"],
                    name=step_data["name"],
                    description=step_data["description"],
                    owner=step_data["owner"],
                    assisting_agents=step_data.get("assisting_agents", []),
                    dependencies=step_data.get("dependencies", []),
                    deliverables=step_data["deliverables"],
                    acceptance_criteria=step_data["acceptance_criteria"]
                )
                self.project_plan.add_step(step)
                
            self.report_progress(f"Created project plan with {len(self.project_plan.steps)} steps")
            
            plan_summary = self._format_project_plan()
            await self.signal_step_success("PROJECT_PLANNING", plan_summary, ["project_plan.json"])
            
        except Exception as e:
            self.report_blocker(f"Failed to create project plan: {str(e)}")
        
    def _format_project_plan(self) -> str:
        if not self.project_plan:
            return "No project plan created"
            
        summary = f"Project: {self.project_plan.project_name}\n"
        summary += f"Description: {self.project_plan.description}\n\n"
        summary += "Steps:\n"
        
        for i, step in enumerate(self.project_plan.steps, 1):
            summary += f"{i}. {step.name} (Owner: {step.owner})\n"
            summary += f"   Description: {step.description}\n"
            if step.dependencies:
                summary += f"   Dependencies: {', '.join(step.dependencies)}\n"
            if step.assisting_agents:
                summary += f"   Assisting: {', '.join(step.assisting_agents)}\n"
            summary += f"   Deliverables: {', '.join(step.deliverables)}\n"
            summary += "\n"
            
        return summary
        
    async def initiate_next_step(self) -> None:
        if not self.project_plan:
            self.report_blocker("No project plan available to execute")
            return
            
        next_step = self.project_plan.get_next_step()
        if not next_step:
            if self.project_plan.is_complete():
                await self.complete_project()
            else:
                self.report_blocker("No next step available - check for blocked steps")
            return
            
        next_step.start_step()
        self.send_message(
            MessageTag.NEXT_STEP,
            f"Initiating {next_step.name}",
            f"Starting step {next_step.step_id}: {next_step.name}\n"
            f"Owner: {next_step.owner}\n"
            f"Assisting agents: {', '.join(next_step.assisting_agents)}\n"
            f"Description: {next_step.description}"
        )
        
    async def complete_project(self) -> None:
        if not self.project_plan:
            self.report_blocker("No project plan to complete")
            return
            
        progress = self.project_plan.get_progress_summary()
        
        self.send_message(
            MessageTag.PROJECT_COMPLETE,
            "Project Completed Successfully",
            f"All project steps completed successfully!\n\n"
            f"Project: {self.project_plan.project_name}\n"
            f"Total steps: {progress['total_steps']}\n"
            f"Completed steps: {progress['completed_steps']}\n"
            f"Progress: {progress['progress_percentage']:.1f}%\n\n"
            f"Final deliverables:\n" + 
            "\n".join([f"- {artifact}" for step in self.project_plan.steps for artifact in step.artifacts])
        )
        
        self.terminate()
        
    def get_project_status(self) -> Dict[str, Any]:
        if not self.project_plan:
            return {"status": "No project plan"}
            
        return {
            "project_name": self.project_plan.project_name,
            "description": self.project_plan.description,
            "progress": self.project_plan.get_progress_summary(),
            "current_step": self.project_plan.get_current_step().name if self.project_plan.get_current_step() else None,
            "next_step": self.project_plan.get_next_step().name if self.project_plan.get_next_step() else None
        }
        
    def handle_step_completion(self, step_id: str, artifacts: List[str] = None) -> None:
        if not self.project_plan:
            return
            
        step = self.project_plan.get_step_by_id(step_id)
        if step:
            step.complete_step(artifacts)
            self.report_progress(f"Step {step_id} completed successfully")
            
    def handle_step_blocker(self, step_id: str, reason: str) -> None:
        if not self.project_plan:
            return
            
        step = self.project_plan.get_step_by_id(step_id)
        if step:
            step.block_step(reason)
            self.report_blocker(f"Step {step_id} blocked: {reason}")
            
    def escalate_issue(self, issue: str) -> None:
        self.send_message(
            MessageTag.PROGRESS,
            "Escalation Notice",
            f"ESCALATE: {issue}\n\nRequesting immediate attention from all active agents."
        ) 