import asyncio
import json
from typing import Dict, List, Any, Optional, Tuple
from autogen import AssistantAgent
from src.agents.base_agent import BaseAgent, MessageTag

class PrincipleSoftwareEngineer(BaseAgent):
    def __init__(self, claude_config: Dict[str, Any], workspace_manager=None, tools=None):
        super().__init__(
            name="principle_software_engineer",
            role="Principle Software Engineer (PSE)",
            system_prompt="""
You are the Principle Software Engineer leading a multi-agent coding team. Your core responsibilities:

1. ANALYZE PROBLEMS: Deep analysis of problem statements to understand exact requirements
2. DETERMINE FILE STRUCTURE: Decide precisely what files are needed (no more, no less)
3. DESIGN ARCHITECTURE: Define function names, signatures, and responsibilities
4. COORDINATE TEAM: Assign specific tasks to appropriate agents based on expertise
5. QUALITY CONTROL: Ensure minimal, focused solutions without unnecessary complexity

Your approach:
- Problem-first thinking: What's the MINIMUM viable solution?
- Function-level design: Define exact functions needed and their interfaces
- Team coordination: Match tasks to agent expertise precisely
- No templates: Every solution is custom-designed for the specific problem
- Iterative refinement: Build incrementally, validate at each step

Analysis Process:
1. Parse problem statement for core functionality
2. Identify ONLY essential files needed
3. Design function architecture with clear responsibilities
4. Create work packages for each agent
5. Monitor progress and adjust dynamically

Communication style:
- Precise and technical
- Focus on minimum viable solutions
- Clear task delegation
- Evidence-based decisions
""",
            workspace_manager=workspace_manager,
            tools=tools
        )
        
        self.claude_agent = AssistantAgent(
            name="principle_software_engineer_claude",
            llm_config=claude_config,
            system_message=self.system_prompt,
            human_input_mode="NEVER"
        )
        
        self.problem_analysis: Optional[Dict[str, Any]] = None
        self.file_architecture: Optional[Dict[str, Any]] = None
        self.function_design: Optional[Dict[str, Any]] = None
        self.work_packages: List[Dict[str, Any]] = []
        
    def get_success_signal(self) -> str:
        return "PRINCIPLE_COMPLETE"
        
    def get_termination_signal(self) -> str:
        return "PSE_EXIT"
        
    async def execute_step(self, step_info: Dict[str, Any]) -> None:
        action = step_info.get("action", "")
        
        if action == "analyze_problem":
            await self.analyze_problem(step_info["problem_statement"])
        elif action == "design_architecture":
            await self.design_file_architecture()
        elif action == "create_work_packages":
            await self.create_work_packages()
        else:
            # Default: full problem solving pipeline
            await self.solve_problem_systematically(step_info.get("problem_statement", ""))
            
    async def solve_problem_systematically(self, problem_statement: str) -> None:
        """Execute the complete problem-solving pipeline"""
        await self.signal_step_start("SYSTEMATIC_PROBLEM_SOLVING")
        
        try:
            # Step 1: Deep problem analysis
            await self.analyze_problem(problem_statement)
            
            # Step 2: Design minimal file architecture
            await self.design_file_architecture()
            
            # Step 3: Create precise work packages
            await self.create_work_packages()
            
            # Step 4: Save design artifacts
            await self.save_design_artifacts()
            
            self.report_progress("Systematic problem analysis completed")
            await self.signal_step_success("SYSTEMATIC_PROBLEM_SOLVING", 
                                         "Problem analyzed and work packages created", 
                                         ["problem_analysis.json", "file_architecture.json", "work_packages.json"])
            
        except Exception as e:
            self.report_blocker(f"Failed to solve problem systematically: {str(e)}")
            
    async def analyze_problem(self, problem_statement: str) -> None:
        """Deep analysis of the problem to understand exact requirements"""
        
        analysis_prompt = f"""
Analyze this problem statement and determine the EXACT requirements:

PROBLEM: {problem_statement}

Perform deep analysis and return JSON with:

{{
  "problem_type": "web_app|api|ml_model|desktop_app|game|cli_tool|library|etc",
  "core_functionality": [
    "Essential function 1",
    "Essential function 2"
  ],
  "user_interactions": [
    "How users will interact with the system"
  ],
  "data_requirements": {{
    "inputs": ["What data comes in"],
    "outputs": ["What data goes out"],
    "storage": ["What needs to be stored"]
  }},
  "technical_constraints": [
    "Performance requirements",
    "Platform requirements",
    "Integration requirements"
  ],
  "success_criteria": [
    "Measurable success criteria"
  ],
  "complexity_assessment": {{
    "level": "simple|medium|complex",
    "justification": "Why this complexity level",
    "estimated_files": "number"
  }}
}}

Focus on UNDERSTANDING the problem, not proposing solutions yet.
"""
        
        response = await self.claude_agent.a_generate_reply(
            messages=[{"role": "user", "content": analysis_prompt}]
        )
        
        try:
            self.problem_analysis = self._parse_json_response(response)
            self.report_progress(f"Problem analyzed: {self.problem_analysis['problem_type']} with {self.problem_analysis['complexity_assessment']['level']} complexity")
            
        except Exception as e:
            # Fallback analysis
            self.problem_analysis = {
                "problem_type": "unknown",
                "core_functionality": ["Basic functionality"],
                "user_interactions": ["User interaction"],
                "data_requirements": {"inputs": [], "outputs": [], "storage": []},
                "technical_constraints": [],
                "success_criteria": ["System works"],
                "complexity_assessment": {"level": "medium", "justification": "Unknown", "estimated_files": 5}
            }
            self.report_progress(f"Using fallback problem analysis due to: {str(e)}")
            
    async def design_file_architecture(self) -> None:
        """Design the minimal file structure needed"""
        
        if not self.problem_analysis:
            raise Exception("Problem analysis must be completed first")
            
        architecture_prompt = f"""
Based on the problem analysis, design the MINIMAL file structure needed:

PROBLEM ANALYSIS: {json.dumps(self.problem_analysis, indent=2)}

Design the absolute minimum files needed. Return JSON:

{{
  "project_structure": {{
    "directory_name": [
      "file1.ext",
      "file2.ext"
    ]
  }},
  "file_purposes": {{
    "file1.ext": {{
      "purpose": "What this file does",
      "key_functions": [
        "function_name: purpose"
      ],
      "dependencies": ["other_file.ext"],
      "agent_assignment": "backend_engineer|frontend_engineer|etc"
    }}
  }},
  "critical_path": [
    "Order of file creation for dependencies"
  ]
}}

Rules:
- ONLY include files that are absolutely necessary
- No placeholder or template files
- Each file must have a clear, specific purpose
- Consider dependencies between files
- Assign each file to the most appropriate agent

For {self.problem_analysis['problem_type']} type problems, think about the minimal viable solution.
"""
        
        response = await self.claude_agent.a_generate_reply(
            messages=[{"role": "user", "content": architecture_prompt}]
        )
        
        try:
            self.file_architecture = self._parse_json_response(response)
            total_files = sum(len(files) for files in self.file_architecture.get("project_structure", {}).values())
            self.report_progress(f"File architecture designed: {total_files} essential files")
            
        except Exception as e:
            # Fallback minimal structure
            self.file_architecture = {
                "project_structure": {
                    "src": ["main.py"],
                    "tests": ["test_main.py"],
                    "docs": ["README.md"]
                },
                "file_purposes": {
                    "main.py": {
                        "purpose": "Main application logic",
                        "key_functions": ["main: entry point"],
                        "dependencies": [],
                        "agent_assignment": "backend_engineer"
                    }
                },
                "critical_path": ["main.py", "test_main.py", "README.md"]
            }
            self.report_progress(f"Using fallback architecture due to: {str(e)}")
            
    async def create_work_packages(self) -> None:
        """Create specific work packages for each agent"""
        
        if not self.file_architecture:
            raise Exception("File architecture must be designed first")
            
        work_prompt = f"""
Create specific work packages for agents based on the file architecture:

FILE ARCHITECTURE: {json.dumps(self.file_architecture, indent=2)}
PROBLEM ANALYSIS: {json.dumps(self.problem_analysis, indent=2)}

Create work packages. Return JSON:

{{
  "work_packages": [
    {{
      "package_id": "WP001",
      "agent": "backend_engineer|frontend_engineer|etc",
      "title": "Specific task title",
      "description": "Detailed description of what to implement",
      "files_to_create": [
        {{
          "file_path": "path/to/file.ext",
          "content_specification": {{
            "functions": [
              {{
                "name": "function_name",
                "parameters": ["param1: type", "param2: type"],
                "return_type": "type",
                "purpose": "What this function does"
              }}
            ],
            "classes": [
              {{
                "name": "ClassName",
                "methods": ["method1", "method2"],
                "purpose": "What this class represents"
              }}
            ],
            "imports": ["required imports"],
            "configuration": ["any config needed"]
          }}
        }}
      ],
      "dependencies": ["WP002"],
      "acceptance_criteria": [
        "Specific measurable criteria"
      ]
    }}
  ]
}}

Make each work package:
- Specific and actionable
- Include exact function signatures
- Specify all imports and dependencies
- Have clear acceptance criteria
- Be assignable to appropriate agent expertise
"""
        
        response = await self.claude_agent.a_generate_reply(
            messages=[{"role": "user", "content": work_prompt}]
        )
        
        try:
            work_data = self._parse_json_response(response)
            self.work_packages = work_data.get("work_packages", [])
            self.report_progress(f"Created {len(self.work_packages)} specific work packages")
            
        except Exception as e:
            # Fallback work packages
            self.work_packages = [
                {
                    "package_id": "WP001",
                    "agent": "backend_engineer",
                    "title": "Implement core functionality",
                    "description": "Create the main application logic",
                    "files_to_create": [
                        {
                            "file_path": "src/main.py",
                            "content_specification": {
                                "functions": [{"name": "main", "parameters": [], "return_type": "None", "purpose": "Entry point"}],
                                "classes": [],
                                "imports": [],
                                "configuration": []
                            }
                        }
                    ],
                    "dependencies": [],
                    "acceptance_criteria": ["Application runs successfully"]
                }
            ]
            self.report_progress(f"Using fallback work packages due to: {str(e)}")
            
    async def save_design_artifacts(self) -> None:
        """Save all design artifacts for team coordination"""
        
        artifacts = [
            ("problem_analysis.json", self.problem_analysis),
            ("file_architecture.json", self.file_architecture),
            ("work_packages.json", {"work_packages": self.work_packages})
        ]
        
        for filename, data in artifacts:
            if data:
                await self.write_file(filename, json.dumps(data, indent=2))
                
    def _parse_json_response(self, response) -> Dict[str, Any]:
        """Parse JSON from Claude response, handling various formats"""
        
        # Handle different response formats
        if isinstance(response, dict):
            if 'content' in response:
                content = response['content']
            else:
                return response
        else:
            content = str(response)
            
        # Extract JSON from content
        if "{" in content and "}" in content:
            start = content.find("{")
            end = content.rfind("}") + 1
            json_str = content[start:end]
            return json.loads(json_str)
        else:
            return json.loads(content)
            
    def get_work_package_by_agent(self, agent_name: str) -> List[Dict[str, Any]]:
        """Get work packages assigned to a specific agent"""
        return [wp for wp in self.work_packages if wp.get("agent") == agent_name]
        
    def get_next_available_package(self, completed_packages: List[str]) -> Optional[Dict[str, Any]]:
        """Get the next work package that can be executed based on dependencies"""
        for package in self.work_packages:
            if package["package_id"] in completed_packages:
                continue
                
            # Check if all dependencies are completed
            dependencies = package.get("dependencies", [])
            if all(dep in completed_packages for dep in dependencies):
                return package
                
        return None
        
    def get_design_summary(self) -> Dict[str, Any]:
        """Get summary of the design process"""
        return {
            "problem_analysis": self.problem_analysis,
            "total_files": sum(len(files) for files in self.file_architecture.get("project_structure", {}).values()) if self.file_architecture else 0,
            "work_packages_count": len(self.work_packages),
            "complexity_level": self.problem_analysis.get("complexity_assessment", {}).get("level", "unknown") if self.problem_analysis else "unknown"
        } 