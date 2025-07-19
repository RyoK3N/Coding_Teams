import asyncio
import os
import json
from typing import Dict, List, Any, Optional
from autogen import AssistantAgent
from src.agents.base_agent import BaseAgent, MessageTag

class SoftwareArchitect(BaseAgent):
    def __init__(self, claude_config: Dict[str, Any], workspace_path: str = "./workspace", tools=None):
        super().__init__(
            name="software_architect",
            role="Software Architect (SA)",
            system_prompt="""
You are a Software Architect for a multi-agent coding team. Your primary responsibilities are:

1. Design system architecture and component structure
2. Choose appropriate technology stack and frameworks
3. Create architectural diagrams and documentation
4. Define API contracts and data models
5. Establish coding standards and best practices
6. Design scalable and maintainable solutions

When designing architecture:
- Consider scalability, performance, and maintainability
- Choose modern, well-supported technologies
- Design clear separation of concerns
- Plan for testing and deployment
- Document architectural decisions
- Consider security implications

Communication style:
- Be thorough in architectural documentation
- Justify technology choices with clear reasoning
- Provide detailed technical specifications
- Focus on long-term maintainability
""",
            tools=tools
        )
        
        self.claude_agent = AssistantAgent(
            name="software_architect_claude",
            llm_config=claude_config,
            system_message=self.system_prompt,
            human_input_mode="NEVER"
        )
        
        self.workspace_path = workspace_path
        self.architecture_design = {}
        self.tech_stack = {}
        
    def get_success_signal(self) -> str:
        return "ARCH_APPROVED"
        
    def get_termination_signal(self) -> str:
        return "SA_EXIT"
        
    async def execute_step(self, step_info: Dict[str, Any]) -> None:
        step_id = step_info.get("step_id", "")
        
        if "architecture" in step_info.get("step_name", "").lower():
            await self.design_architecture(step_info)
        elif "tech_stack" in step_info.get("step_name", "").lower():
            await self.choose_tech_stack(step_info)
        else:
            await self.design_architecture(step_info)
            
    async def design_architecture(self, step_info: Dict[str, Any]) -> None:
        await self.signal_step_start(step_info["step_name"])
        
        problem_description = step_info.get('description', '')
        requirements = step_info.get('acceptance_criteria', [])
        step_name = step_info.get('step_name', '')
        
        architecture_prompt = f"""
You are designing system architecture for this specific problem:

STEP: {step_name}
DESCRIPTION: {problem_description}
REQUIREMENTS: {', '.join(requirements)}

Analyze the problem and create a detailed architecture design. Return JSON:

{{
  "project_type": "[Determine type: web_app|api|ml_model|desktop_app|game|mobile_app|etc based on description]",
  "system_overview": "[Clear overview of the system being built based on the actual problem]",
  "directory_structure": {{
    "[primary_folder]": [
      "[appropriate files for this problem type]"
    ],
    "[secondary_folder]": [
      "[more appropriate files]"
    ]
  }},
  "components": [
    {{
      "name": "[Component name relevant to this problem]",
      "purpose": "[Purpose specific to this domain]",
      "technology": "[Appropriate technology for this problem]",
      "responsibilities": "[Responsibilities for this specific use case]"
    }}
  ],
  "tech_stack": {{
    "primary": "[Main technology choice based on problem type]",
    "secondary": "[Supporting technologies]",
    "database": "[Database choice if needed]",
    "deployment": "[Deployment strategy]",
    "testing": "[Testing framework]"
  }},
  "implementation_details": {{
    "key_features": ["[Features specific to this problem]"],
    "data_flow": "[How data flows through the system for this use case]",
    "scalability_considerations": "[Scalability needs for this problem]"
  }}
}}

IMPORTANT - Adapt to the actual problem type:

FOR CNN/ML MODELS:
- Include: model/, data/, notebooks/, training/, inference/, api/, frontend/
- Components: Data Pipeline, Model Training, Inference Engine, Web Interface
- Tech: Python, TensorFlow/PyTorch, FastAPI, React/HTML, Docker

FOR WEB APPLICATIONS:
- Include: backend/, frontend/, database/, api/, static/, templates/
- Components: Web Server, Database, Frontend, API Gateway
- Tech: React/Vue/Angular + Node.js/Python/Java + PostgreSQL/MySQL

FOR APIS:
- Include: api/, models/, routes/, middleware/, tests/, docs/
- Components: API Gateway, Business Logic, Data Layer
- Tech: FastAPI/Express/Spring + Database + Docker

FOR GAMES:
- Include: src/, assets/, scripts/, levels/, audio/, graphics/
- Components: Game Engine, Asset Manager, Input Handler, Renderer
- Tech: Unity/Godot/Custom + C#/C++/Python

FOR DESKTOP APPS:
- Include: src/, ui/, resources/, config/, build/
- Components: UI Layer, Business Logic, Data Layer
- Tech: Electron/Tkinter/Qt + Python/JavaScript/C++

Analyze the problem description and choose the most appropriate architecture pattern.
"""
        
        response = await self.claude_agent.a_generate_reply(
            messages=[{"role": "user", "content": architecture_prompt}]
        )
        
        try:
            # Handle response format
            if isinstance(response, dict):
                if 'content' in response:
                    content = response['content']
                    if "{" in content and "}" in content:
                        start = content.find("{")
                        end = content.rfind("}") + 1
                        json_str = content[start:end]
                        architecture_data = json.loads(json_str)
                    else:
                        architecture_data = json.loads(content)
                else:
                    architecture_data = response
            
            self.architecture_design = architecture_data
            
            # Create workspace directory structure based on architecture
            await self._create_project_structure(architecture_data)
            
            # Save architecture design
            await self.write_file("architecture.json", json.dumps(architecture_data, indent=2))
            
            # Create architecture documentation
            arch_doc = self._create_architecture_doc(architecture_data)
            await self.write_file("ARCHITECTURE.md", arch_doc)
            
            self.report_progress(f"Architecture design completed with {len(architecture_data.get('components', []))} components")
            
            artifacts = ["architecture.json", "ARCHITECTURE.md"]
            await self.signal_step_success(step_info["step_name"], "Architecture design completed successfully", artifacts)
            
        except Exception as e:
            self.report_blocker(f"Failed to design architecture: {str(e)}")
            
    async def _create_project_structure(self, architecture_data: Dict[str, Any]):
        """Create the actual project directory structure"""
        directory_structure = architecture_data.get("directory_structure", {})
        
        for category, files in directory_structure.items():
            # Create category directory
            await self.create_directory(category)
            
            for file_path in files:
                if file_path.endswith("/"):
                    # It's a directory
                    await self.create_directory(f"{category}/{file_path}")
                else:
                    # For files, only create the parent directories
                    # Let the appropriate agents create the actual files with content
                    full_path = f"{category}/{file_path}"
                    if "/" in file_path:
                        dir_part = f"{category}/{'/'.join(file_path.split('/')[:-1])}"
                        await self.create_directory(dir_part)
                    
                    # Don't create empty placeholder files - let specialized agents handle file creation
                    self.logger.info(f"Directory structure ready for: {full_path}")
        
        self.logger.info(f"Created directory structure for {sum(len(files) for files in directory_structure.values())} planned files")
        
    def _create_architecture_doc(self, architecture_data: Dict[str, Any]) -> str:
        doc = "# System Architecture\n\n"
        
        if "system_overview" in architecture_data:
            doc += f"## System Overview\n{architecture_data['system_overview']}\n\n"
        
        if "components" in architecture_data:
            doc += "## System Components\n\n"
            for component in architecture_data["components"]:
                doc += f"### {component.get('name', 'Component')}\n"
                doc += f"- **Purpose**: {component.get('purpose', 'N/A')}\n"
                doc += f"- **Technology**: {component.get('technology', 'N/A')}\n"
                doc += f"- **Responsibilities**: {component.get('responsibilities', 'N/A')}\n\n"
        
        if "tech_stack" in architecture_data:
            doc += "## Technology Stack\n\n"
            for category, tech in architecture_data["tech_stack"].items():
                doc += f"- **{category.title()}**: {tech}\n"
            doc += "\n"
        
        if "api_design" in architecture_data:
            doc += "## API Design\n\n"
            for endpoint in architecture_data["api_design"].get("endpoints", []):
                doc += f"### {endpoint.get('method', 'GET')} {endpoint.get('path', '/')}\n"
                doc += f"- **Description**: {endpoint.get('description', 'N/A')}\n"
                doc += f"- **Request**: {endpoint.get('request', 'N/A')}\n"
                doc += f"- **Response**: {endpoint.get('response', 'N/A')}\n\n"
        
        return doc
        
    async def choose_tech_stack(self, step_info: Dict[str, Any]) -> None:
        self.signal_step_start(step_info["step_name"])
        
        tech_prompt = f"""
Choose an appropriate technology stack for the following requirements:

Step: {step_info.get('step_name', '')}
Description: {step_info.get('description', '')}
Requirements: {step_info.get('acceptance_criteria', [])}

Provide recommendations for:
1. Frontend framework and libraries
2. Backend framework and runtime
3. Database technology
4. Authentication system
5. Deployment platform
6. Development tools

Justify each choice with reasoning.
"""
        
        response = await self.claude_agent.a_generate_reply(
            messages=[{"role": "user", "content": tech_prompt}]
        )
        
        try:
            # Handle response format
            if isinstance(response, dict):
                tech_data = response
            elif isinstance(response, str):
                tech_data = json.loads(response)
            else:
                content = getattr(response, 'content', str(response))
                if isinstance(content, list) and len(content) > 0:
                    content = content[0].text if hasattr(content[0], 'text') else str(content[0])
                tech_data = json.loads(content)
            
            self.tech_stack = tech_data
            
            # Save tech stack
            tech_file = os.path.join(self.workspace_path, "tech_stack.json")
            with open(tech_file, 'w') as f:
                json.dump(tech_data, f, indent=2)
            
            self.report_progress("Technology stack selected and documented")
            
            artifacts = ["tech_stack.json"]
            self.signal_step_success(step_info["step_name"], "Technology stack selection completed", artifacts)
            
        except Exception as e:
            self.report_blocker(f"Failed to choose tech stack: {str(e)}")
            
    def get_architecture_summary(self) -> Dict[str, Any]:
        return {
            "architecture_design": self.architecture_design,
            "tech_stack": self.tech_stack,
            "components_count": len(self.architecture_design.get("components", [])),
            "apis_count": len(self.architecture_design.get("api_design", {}).get("endpoints", []))
        } 