import asyncio
import os
import json
from typing import Dict, List, Any, Optional
from autogen import AssistantAgent
from src.agents.base_agent import BaseAgent, MessageTag

class BackendEngineer(BaseAgent):
    def __init__(self, claude_config: Dict[str, Any], workspace_path: str = "./workspace", tools=None):
        super().__init__(
            name="backend_engineer",
            role="Backend Engineer (BE)",
            system_prompt="""
You are a Backend Engineer for a multi-agent coding team. Your primary responsibilities are:

1. Implement server-side logic and business rules based on work package specifications
2. Create RESTful APIs and endpoints as specified
3. Design and implement data models according to requirements
4. Write comprehensive unit tests for backend functionality
5. Implement authentication and authorization when required
6. Handle data validation and error handling appropriately
7. Follow specifications precisely without adding unnecessary features

When implementing backend features:
- Follow work package specifications exactly
- Implement only what is requested
- Use appropriate technologies for the problem domain
- Write clean, maintainable, production-ready code
- Include proper error handling and validation
- Add comprehensive tests for functionality
- Follow security best practices
- Document code appropriately

Communication style:
- Focus on implementation details
- Report progress clearly
- Ask for clarification when specifications are unclear
- Provide concise status updates
""",
            tools=tools
        )
        
        self.claude_agent = AssistantAgent(
            name="backend_engineer_claude",
            llm_config=claude_config,
            system_message=self.system_prompt,
            human_input_mode="NEVER"
        )
        
        self.workspace_path = workspace_path
        
    def get_success_signal(self) -> str:
        return "BACKEND_COMPLETE"
        
    def get_termination_signal(self) -> str:
        return "BE_EXIT"
        
    async def execute_step(self, step_info: Dict[str, Any]) -> None:
        if "work_package" in step_info:
            await self.execute_work_package(step_info["work_package"])
        else:
            # Legacy support for old step format
            await self.legacy_execute_step(step_info)
            
    async def execute_work_package(self, work_package: Dict[str, Any]) -> None:
        """Execute a work package with dynamic code generation"""
        package_id = work_package.get("package_id", "UNKNOWN")
        title = work_package.get("title", "Backend Work Package")
        
        await self.signal_step_start(f"Backend: {title}")
        
        try:
            files_to_create = work_package.get("files_to_create", [])
            created_files = []
            
            for file_spec in files_to_create:
                file_path = file_spec.get("file_path")
                content_spec = file_spec.get("content_specification", {})
                
                if file_path and self._is_backend_file(file_path):
                    # Generate file content based on specification
                    file_content = await self.generate_backend_file_content(file_path, content_spec, work_package)
                    
                    if file_content:
                        success = await self.write_file(file_path, file_content)
                        if success:
                            created_files.append(file_path)
                            self.logger.info(f"Created backend file: {file_path}")
                        else:
                            self.logger.error(f"Failed to create file: {file_path}")
                    else:
                        self.logger.warning(f"No content generated for file: {file_path}")
            
            self.report_progress(f"Backend work package {package_id} completed: {len(created_files)} files created")
            await self.signal_step_success(f"Backend: {title}", f"Backend work package completed successfully", created_files)
            
        except Exception as e:
            self.report_blocker(f"Failed to execute backend work package {package_id}: {str(e)}")
            await self.fail_current_step(str(e))
            
    def _is_backend_file(self, file_path: str) -> bool:
        """Check if this file should be handled by backend engineer"""
        backend_patterns = [
            "backend/", "api/", "server/", 
            ".py", "requirements.txt", "Dockerfile",
            "models/", "routes/", "services/",
            "test_", "_test.py", "tests/"
        ]
        
        file_lower = file_path.lower()
        return any(pattern in file_lower for pattern in backend_patterns)
        
    async def generate_backend_file_content(self, file_path: str, content_spec: Dict[str, Any], work_package: Dict[str, Any]) -> Optional[str]:
        """Generate backend file content based on specifications"""
        
        generation_prompt = f"""
Generate backend code for file: {file_path}

WORK PACKAGE CONTEXT:
{json.dumps(work_package, indent=2)}

CONTENT SPECIFICATION:
{json.dumps(content_spec, indent=2)}

Create backend code that:
1. Implements all specified functions with exact signatures
2. Includes all specified classes with required methods
3. Adds necessary imports for the specific problem domain
4. Includes proper error handling and validation
5. Follows backend engineering best practices
6. Is production-ready and well-structured
7. Implements ONLY what is specified - no extra features

Important:
- Analyze the work package description to understand the problem domain
- Choose appropriate libraries and frameworks for the specific use case
- Generate code that solves the actual problem, not generic templates
- Include proper HTTP status codes, request/response handling if it's an API
- Add authentication/authorization only if specified
- Include database operations only if specified

Generate ONLY the code content, no explanations or markdown formatting.
"""
        
        response = await self.claude_agent.a_generate_reply(
            messages=[{"role": "user", "content": generation_prompt}]
        )
        
        return self._extract_code_from_response(response)
        
    def _extract_code_from_response(self, response) -> str:
        """Extract code content from Claude response, removing markdown formatting"""
        
        if isinstance(response, dict):
            content = response.get('content', str(response))
        else:
            content = str(response)
            
        # Remove code block formatting if present
        if '```' in content:
            lines = content.split('\n')
            start_idx = None
            end_idx = None
            
            for i, line in enumerate(lines):
                if line.strip().startswith('```') and start_idx is None:
                    start_idx = i + 1
                elif line.strip().startswith('```') and start_idx is not None:
                    end_idx = i
                    break
                    
            if start_idx is not None and end_idx is not None:
                content = '\n'.join(lines[start_idx:end_idx])
            elif start_idx is not None:
                content = '\n'.join(lines[start_idx:])
                
        return content.strip()
        
    async def legacy_execute_step(self, step_info: Dict[str, Any]) -> None:
        """Legacy support for old step format"""
        step_name = step_info.get("step_name", "Backend Task")
        
        await self.signal_step_start(step_name)
        
        # Simple implementation for backward compatibility
        self.report_progress("Legacy backend step executed")
        await self.signal_step_success(step_name, "Legacy backend step completed", []) 