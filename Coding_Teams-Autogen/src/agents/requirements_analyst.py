import asyncio
import json
from typing import Dict, List, Any, Optional
from autogen import AssistantAgent
from src.agents.base_agent import BaseAgent, MessageTag

class RequirementsAnalyst(BaseAgent):
    def __init__(self, claude_config: Dict[str, Any], workspace_manager=None, tools=None):
        super().__init__(
            name="requirements_analyst",
            role="Requirements Analyst (RA)",
            system_prompt="""
You are a Requirements Analyst for a multi-agent coding team. Your primary responsibilities are:

1. Extract and clarify functional and non-functional requirements from problem statements
2. Identify ambiguities and potential issues in requirements
3. Create detailed requirement specifications
4. Validate requirements with stakeholders
5. Document acceptance criteria for each requirement
6. Flag missing or contradictory requirements

When analyzing requirements:
- Ask clarifying questions about vague or ambiguous statements
- Break down complex requirements into specific, measurable components
- Identify functional requirements (what the system should do)
- Identify non-functional requirements (performance, security, usability)
- Consider edge cases and error conditions
- Document assumptions and constraints

Communication style:
- Be precise and thorough in requirement documentation
- Ask specific, targeted questions for clarification
- Highlight potential risks or issues early
- Provide clear, actionable requirement specifications
""",
            workspace_manager=workspace_manager,
            tools=tools
        )
        
        self.claude_agent = AssistantAgent(
            name="requirements_analyst_claude",
            llm_config=claude_config,
            system_message=self.system_prompt,
            human_input_mode="NEVER"
        )
        
        self.requirements: List[Dict[str, Any]] = []
        self.ambiguities: List[str] = []
        self.assumptions: List[str] = []
        
    def get_success_signal(self) -> str:
        return "REQS_CONFIRMED"
        
    def get_termination_signal(self) -> str:
        return "RA_EXIT"
        
    async def execute_step(self, step_info: Dict[str, Any]) -> None:
        step_name = step_info.get("step_name", "").lower()
        
        if "requirements" in step_name or "analysis" in step_name:
            await self.analyze_requirements(step_info)
        elif "clarify" in step_name:
            await self.clarify_requirements(step_info.get("clarifications", []))
        elif "finalize" in step_name:
            await self.finalize_requirements()
        else:
            # Default to requirements analysis
            await self.analyze_requirements(step_info)
            
    async def analyze_requirements(self, step_info: Dict[str, Any]) -> None:
        await self.signal_step_start("REQUIREMENTS_ANALYSIS")
        
        step_name = step_info.get("step_name", "")
        step_description = step_info.get("description", "")
        acceptance_criteria = step_info.get("acceptance_criteria", [])
        
        requirements_prompt = f"""
You are analyzing requirements for this specific step:

STEP: {step_name}
DESCRIPTION: {step_description}
ACCEPTANCE_CRITERIA: {', '.join(acceptance_criteria)}

Based on the step description, analyze and extract specific requirements. Return JSON:

{{
  "functional_requirements": [
    {{
      "id": "FR001",
      "title": "[Specific functional requirement based on step description]",
      "description": "[Detailed description of what the system should do for this step]",
      "priority": "HIGH|MEDIUM|LOW",
      "acceptance_criteria": ["[Specific criteria based on the step requirements]"]
    }}
  ],
  "non_functional_requirements": [
    {{
      "id": "NFR001",
      "category": "[Performance|Security|Usability|Reliability|etc]",
      "title": "[Non-functional requirement title]",
      "description": "[Description relevant to this step]",
      "metric": "[How to measure it]",
      "target": "[Target value]"
    }}
  ],
  "technical_requirements": [
    {{
      "id": "TR001",
      "title": "[Technical requirement]",
      "description": "[Technology or implementation requirement]",
      "justification": "[Why this is needed for this step]"
    }}
  ],
  "assumptions": ["[Assumptions made based on step description]"],
  "constraints": ["[Constraints identified from step description]"],
  "dependencies": ["[External dependencies needed for this step]"]
}}

IMPORTANT - Generate requirements specific to the step description:

FOR CNN/ML MODEL STEPS:
- Model accuracy requirements
- Training data requirements  
- Inference time constraints
- Model size limitations
- Hardware requirements

FOR API DEVELOPMENT STEPS:
- Endpoint functionality requirements
- Response time requirements
- Data validation requirements
- Error handling requirements
- Authentication requirements

FOR WEB FRONTEND STEPS:
- User interface requirements
- Browser compatibility requirements
- Responsive design requirements
- Accessibility requirements
- Performance requirements

FOR TESTING STEPS:
- Test coverage requirements
- Testing framework requirements
- Performance testing requirements
- Security testing requirements
- Integration testing requirements

Analyze the specific step and generate appropriate requirements for that domain and task.
"""
        
        try:
            # For simple cases or fallback, generate basic requirements
            if not step_description or len(step_description.strip()) < 10:
                requirements_data = self._generate_basic_requirements(step_name, acceptance_criteria)
            else:
                # Use LLM for complex analysis
                response = await self.claude_agent.a_generate_reply(
                    messages=[{"role": "user", "content": requirements_prompt}]
                )
                
                # Handle response format
                if isinstance(response, dict):
                    if 'content' in response:
                        content = response['content']
                        if "{" in content and "}" in content:
                            start = content.find("{")
                            end = content.rfind("}") + 1
                            json_str = content[start:end]
                            requirements_data = json.loads(json_str)
                        else:
                            requirements_data = json.loads(content)
                    else:
                        requirements_data = response
                elif isinstance(response, str):
                    if "{" in response and "}" in response:
                        start = response.find("{")
                        end = response.rfind("}") + 1
                        json_str = response[start:end]
                        requirements_data = json.loads(json_str)
                    else:
                        requirements_data = self._generate_basic_requirements(step_name, acceptance_criteria)
                else:
                    requirements_data = self._generate_basic_requirements(step_name, acceptance_criteria)
            
            self.requirements = requirements_data.get("functional_requirements", []) + \
                             requirements_data.get("non_functional_requirements", []) + \
                             requirements_data.get("technical_requirements", [])
            self.assumptions = requirements_data.get("assumptions", [])
            
            # Write requirements to file
            await self.write_file("requirements.json", json.dumps(requirements_data, indent=2))
            
            # Create requirements document
            req_summary = self._format_requirements_summary(requirements_data)
            await self.write_file("REQUIREMENTS.md", req_summary)
            
            self.report_progress(f"Analyzed requirements: {len(self.requirements)} requirements identified")
            
            artifacts = ["requirements.json", "REQUIREMENTS.md"]
            await self.signal_step_success("REQUIREMENTS_ANALYSIS", req_summary, artifacts)
            
        except Exception as e:
            self.report_blocker(f"Failed to analyze requirements: {str(e)}")
            await self.fail_current_step(str(e))
    
    def _generate_basic_requirements(self, step_name: str, acceptance_criteria: List[str]) -> Dict[str, Any]:
        """Generate basic requirements when LLM analysis fails or for simple cases"""
        return {
            "functional_requirements": [
                {
                    "id": "FR001",
                    "title": f"Implement {step_name}",
                    "description": f"Successfully complete the {step_name} step as specified",
                    "priority": "HIGH",
                    "acceptance_criteria": acceptance_criteria if acceptance_criteria else [f"{step_name} completed successfully"]
                }
            ],
            "non_functional_requirements": [
                {
                    "id": "NFR001",
                    "category": "Performance",
                    "title": "Reasonable Response Time",
                    "description": "System should respond within acceptable time limits",
                    "metric": "Response time",
                    "target": "< 2 seconds"
                }
            ],
            "technical_requirements": [
                {
                    "id": "TR001",
                    "title": "Standard Implementation",
                    "description": "Use industry standard practices and technologies",
                    "justification": "Ensures maintainability and compatibility"
                }
            ],
            "assumptions": ["Standard development environment", "Basic infrastructure available"],
            "constraints": ["Limited development time", "Standard hardware resources"],
            "dependencies": ["Development tools", "Required libraries"]
        }
        
    def _format_requirements_summary(self, analysis_data: Dict[str, Any]) -> str:
        summary = "Requirements Analysis Summary\n\n"
        
        # Functional Requirements
        if analysis_data.get("functional_requirements"):
            summary += "Functional Requirements:\n"
            for req in analysis_data["functional_requirements"]:
                summary += f"- {req['id']}: {req['title']} ({req['priority']})\n"
                summary += f"  Description: {req['description']}\n"
                if req.get('acceptance_criteria'):
                    summary += f"  Acceptance Criteria: {', '.join(req['acceptance_criteria'])}\n"
                summary += "\n"
        
        # Non-Functional Requirements
        if analysis_data.get("non_functional_requirements"):
            summary += "Non-Functional Requirements:\n"
            for req in analysis_data["non_functional_requirements"]:
                summary += f"- {req['id']}: {req['title']} ({req['category']})\n"
                summary += f"  Description: {req['description']}\n"
                if req.get('metric'):
                    summary += f"  Metric: {req['metric']}\n"
                if req.get('target'):
                    summary += f"  Target: {req['target']}\n"
                summary += "\n"
        
        # Technical Requirements
        if analysis_data.get("technical_requirements"):
            summary += "Technical Requirements:\n"
            for req in analysis_data["technical_requirements"]:
                summary += f"- {req['id']}: {req['title']}\n"
                summary += f"  Description: {req['description']}\n"
                if req.get('justification'):
                    summary += f"  Justification: {req['justification']}\n"
                summary += "\n"
        
        # Ambiguities
        if analysis_data.get("ambiguities"):
            summary += "Identified Ambiguities:\n"
            for amb in analysis_data["ambiguities"]:
                summary += f"- {amb}\n"
            summary += "\n"
        
        # Assumptions
        if analysis_data.get("assumptions"):
            summary += "Assumptions:\n"
            for assumption in analysis_data["assumptions"]:
                summary += f"- {assumption}\n"
            summary += "\n"
        
        # Constraints
        if analysis_data.get("constraints"):
            summary += "Constraints:\n"
            for constraint in analysis_data["constraints"]:
                summary += f"- {constraint}\n"
            summary += "\n"

        # Dependencies
        if analysis_data.get("dependencies"):
            summary += "Dependencies:\n"
            for dep in analysis_data["dependencies"]:
                summary += f"- {dep}\n"
            summary += "\n"
        
        return summary
        
    async def clarify_requirements(self, clarifications: List[Dict[str, str]]) -> None:
        self.report_progress("Processing requirement clarifications")
        
        clarification_prompt = f"""
Based on the following clarifications provided by stakeholders, please update the requirements:

Clarifications:
{json.dumps(clarifications, indent=2)}

Current Requirements:
{json.dumps(self.requirements, indent=2)}

Please provide updated requirements that incorporate these clarifications and resolve any ambiguities.
"""
        
        response = await self.claude_agent.a_generate_reply(
            messages=[{"role": "user", "content": clarification_prompt}]
        )
        
        try:
            # Handle both string and dict responses from Claude API
            if isinstance(response, dict):
                # Claude API returns a dict with 'content' key
                if 'content' in response:
                    content = response['content']
                    # Extract JSON from content
                    if "{" in content and "}" in content:
                        start = content.find("{")
                        end = content.rfind("}") + 1
                        json_str = content[start:end]
                        updated_data = json.loads(json_str)
                    else:
                        updated_data = json.loads(content)
                else:
                    updated_data = response
                
            self.requirements = updated_data.get("requirements", self.requirements)
            self.report_progress("Requirements updated based on clarifications")
            
        except Exception as e:
            self.report_blocker(f"Failed to process clarifications: {str(e)}")
            
    async def finalize_requirements(self) -> None:
        if not self.requirements:
            self.report_blocker("No requirements to finalize")
            return
            
        if self.ambiguities:
            self.report_blocker(f"Cannot finalize requirements - {len(self.ambiguities)} ambiguities remain unresolved")
            return
            
        # Create final requirements document
        final_doc = {
            "requirements": self.requirements,
            "assumptions": self.assumptions,
            "total_requirements": len(self.requirements),
            "high_priority_count": sum(1 for req in self.requirements if req.get("priority") == "HIGH"),
            "medium_priority_count": sum(1 for req in self.requirements if req.get("priority") == "MEDIUM"),
            "low_priority_count": sum(1 for req in self.requirements if req.get("priority") == "LOW")
        }
        
        summary = f"Requirements finalized successfully!\n\n"
        summary += f"Total Requirements: {final_doc['total_requirements']}\n"
        summary += f"High Priority: {final_doc['high_priority_count']}\n"
        summary += f"Medium Priority: {final_doc['medium_priority_count']}\n"
        summary += f"Low Priority: {final_doc['low_priority_count']}\n\n"
        summary += f"All ambiguities resolved and requirements documented."
        
        self.signal_step_success("REQUIREMENTS_FINALIZATION", summary, ["final_requirements.json"])
        self.terminate()
        
    def validate_requirement(self, requirement: Dict[str, Any]) -> List[str]:
        issues = []
        
        if not requirement.get("id"):
            issues.append("Missing requirement ID")
        if not requirement.get("title"):
            issues.append("Missing requirement title")
        if not requirement.get("description"):
            issues.append("Missing requirement description")
        if not requirement.get("priority"):
            issues.append("Missing requirement priority")
        if not requirement.get("acceptance_criteria"):
            issues.append("Missing acceptance criteria")
            
        return issues
        
    def get_requirements_status(self) -> Dict[str, Any]:
        return {
            "total_requirements": len(self.requirements),
            "unresolved_ambiguities": len(self.ambiguities),
            "assumptions_count": len(self.assumptions),
            "high_priority_requirements": sum(1 for req in self.requirements if req.get("priority") == "HIGH"),
            "requirements_finalized": len(self.ambiguities) == 0
        } 