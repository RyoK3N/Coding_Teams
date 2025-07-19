import asyncio
import json
from typing import Dict, List, Any, Optional
from autogen import AssistantAgent
from src.agents.base_agent import BaseAgent, MessageTag

class SmartCodingAgent(BaseAgent):
    def __init__(self, name: str, role: str, specialization: str, claude_config: Dict[str, Any], workspace_path: str = "./workspace", tools=None):
        super().__init__(
            name=name,
            role=role,
            system_prompt=f"""
You are a {role} specializing in {specialization}. Your responsibilities:

1. EXECUTE WORK PACKAGES: Implement exactly what's specified in work packages
2. DYNAMIC CODE GENERATION: Generate code based on specifications, not templates
3. FUNCTION-LEVEL IMPLEMENTATION: Create exact functions with specified signatures
4. QUALITY FOCUS: Write production-ready, clean, testable code
5. SPECIFICATION COMPLIANCE: Follow work package requirements precisely

Your approach:
- Read work package specifications carefully
- Implement ONLY what's requested
- Use appropriate patterns for the problem domain
- Write clean, maintainable code
- Add proper error handling and validation
- Include necessary imports and dependencies

Specialization: {specialization}
- Focus on {specialization}-specific best practices
- Use appropriate libraries and frameworks
- Follow domain-specific conventions
- Optimize for {specialization} requirements

Communication style:
- Report progress clearly
- Ask for clarification when specifications are unclear
- Focus on implementation details
- Provide concise status updates
""",
            tools=tools
        )
        
        self.specialization = specialization
        self.claude_agent = AssistantAgent(
            name=f"{name}_claude",
            llm_config=claude_config,
            system_message=self.system_prompt,
            human_input_mode="NEVER"
        )
        
        self.workspace_path = workspace_path
        self.completed_packages: List[str] = []
        
    def get_success_signal(self) -> str:
        return f"{self.name.upper()}_COMPLETE"
        
    def get_termination_signal(self) -> str:
        return f"{self.name.upper()}_EXIT"
        
    async def execute_step(self, step_info: Dict[str, Any]) -> None:
        if "work_package" in step_info:
            await self.execute_work_package(step_info["work_package"])
        else:
            # Fallback to generic step execution
            await self.signal_step_start(step_info.get("step_name", "Generic Task"))
            self.report_progress("No specific work package provided")
            await self.signal_step_success(step_info.get("step_name", "Generic Task"), "Task completed generically", [])
            
    async def execute_work_package(self, work_package: Dict[str, Any]) -> None:
        """Execute a specific work package"""
        package_id = work_package.get("package_id", "UNKNOWN")
        title = work_package.get("title", "Work Package")
        
        await self.signal_step_start(f"WP: {title}")
        
        try:
            files_to_create = work_package.get("files_to_create", [])
            created_files = []
            
            for file_spec in files_to_create:
                file_path = file_spec.get("file_path")
                content_spec = file_spec.get("content_specification", {})
                
                if file_path:
                    # Generate file content based on specification
                    file_content = await self.generate_file_content(file_path, content_spec, work_package)
                    
                    if file_content:
                        success = await self.write_file(file_path, file_content)
                        if success:
                            created_files.append(file_path)
                            self.logger.info(f"Created file: {file_path}")
                        else:
                            self.logger.error(f"Failed to create file: {file_path}")
                    else:
                        self.logger.warning(f"No content generated for file: {file_path}")
            
            # Mark package as completed
            self.completed_packages.append(package_id)
            
            self.report_progress(f"Work package {package_id} completed: {len(created_files)} files created")
            await self.signal_step_success(f"WP: {title}", f"Work package {package_id} completed successfully", created_files)
            
        except Exception as e:
            self.report_blocker(f"Failed to execute work package {package_id}: {str(e)}")
            await self.fail_current_step(str(e))
            
    async def generate_file_content(self, file_path: str, content_spec: Dict[str, Any], work_package: Dict[str, Any]) -> Optional[str]:
        """Generate file content based on specifications"""
        
        # Determine file type from extension
        file_type = self._determine_file_type(file_path)
        
        if file_type == "python":
            return await self.generate_python_content(file_path, content_spec, work_package)
        elif file_type == "javascript":
            return await self.generate_javascript_content(file_path, content_spec, work_package)
        elif file_type == "html":
            return await self.generate_html_content(file_path, content_spec, work_package)
        elif file_type == "css":
            return await self.generate_css_content(file_path, content_spec, work_package)
        elif file_type == "markdown":
            return await self.generate_markdown_content(file_path, content_spec, work_package)
        elif file_type == "json":
            return await self.generate_json_content(file_path, content_spec, work_package)
        else:
            return await self.generate_generic_content(file_path, content_spec, work_package)
            
    async def generate_python_content(self, file_path: str, content_spec: Dict[str, Any], work_package: Dict[str, Any]) -> str:
        """Generate Python file content"""
        
        generation_prompt = f"""
Generate Python code for file: {file_path}

WORK PACKAGE CONTEXT:
{json.dumps(work_package, indent=2)}

CONTENT SPECIFICATION:
{json.dumps(content_spec, indent=2)}

Create Python code that:
1. Implements all specified functions with exact signatures
2. Includes all specified classes with required methods
3. Adds necessary imports
4. Includes proper error handling
5. Follows Python best practices
6. Is production-ready and well-structured

Generate ONLY the Python code, no explanations or markdown formatting.
Focus on {self.specialization} best practices.
"""
        
        response = await self.claude_agent.a_generate_reply(
            messages=[{"role": "user", "content": generation_prompt}]
        )
        
        return self._extract_code_from_response(response)
        
    async def generate_javascript_content(self, file_path: str, content_spec: Dict[str, Any], work_package: Dict[str, Any]) -> str:
        """Generate JavaScript file content"""
        
        generation_prompt = f"""
Generate JavaScript code for file: {file_path}

WORK PACKAGE CONTEXT:
{json.dumps(work_package, indent=2)}

CONTENT SPECIFICATION:
{json.dumps(content_spec, indent=2)}

Create JavaScript code that:
1. Implements all specified functions
2. Includes all specified classes
3. Adds necessary imports/requires
4. Includes proper error handling
5. Follows JavaScript best practices
6. Is production-ready and well-structured

Generate ONLY the JavaScript code, no explanations or markdown formatting.
Focus on {self.specialization} best practices.
"""
        
        response = await self.claude_agent.a_generate_reply(
            messages=[{"role": "user", "content": generation_prompt}]
        )
        
        return self._extract_code_from_response(response)
        
    async def generate_html_content(self, file_path: str, content_spec: Dict[str, Any], work_package: Dict[str, Any]) -> str:
        """Generate HTML file content"""
        
        generation_prompt = f"""
Generate HTML code for file: {file_path}

WORK PACKAGE CONTEXT:
{json.dumps(work_package, indent=2)}

CONTENT SPECIFICATION:
{json.dumps(content_spec, indent=2)}

Create HTML that:
1. Implements the specified UI components
2. Includes proper semantic structure
3. Is responsive and accessible
4. Follows modern HTML5 standards
5. Includes necessary meta tags and links

Generate ONLY the HTML code, no explanations or markdown formatting.
Focus on {self.specialization} best practices.
"""
        
        response = await self.claude_agent.a_generate_reply(
            messages=[{"role": "user", "content": generation_prompt}]
        )
        
        return self._extract_code_from_response(response)
        
    async def generate_css_content(self, file_path: str, content_spec: Dict[str, Any], work_package: Dict[str, Any]) -> str:
        """Generate CSS file content"""
        
        generation_prompt = f"""
Generate CSS code for file: {file_path}

WORK PACKAGE CONTEXT:
{json.dumps(work_package, indent=2)}

CONTENT SPECIFICATION:
{json.dumps(content_spec, indent=2)}

Create CSS that:
1. Implements specified styles and layout
2. Is responsive and mobile-friendly
3. Uses modern CSS features appropriately
4. Follows BEM or similar methodology
5. Is well-organized and maintainable

Generate ONLY the CSS code, no explanations or markdown formatting.
Focus on {self.specialization} best practices.
"""
        
        response = await self.claude_agent.a_generate_reply(
            messages=[{"role": "user", "content": generation_prompt}]
        )
        
        return self._extract_code_from_response(response)
        
    async def generate_markdown_content(self, file_path: str, content_spec: Dict[str, Any], work_package: Dict[str, Any]) -> str:
        """Generate Markdown file content"""
        
        generation_prompt = f"""
Generate Markdown documentation for file: {file_path}

WORK PACKAGE CONTEXT:
{json.dumps(work_package, indent=2)}

CONTENT SPECIFICATION:
{json.dumps(content_spec, indent=2)}

Create documentation that:
1. Clearly explains the project/component
2. Includes usage instructions
3. Provides examples where appropriate
4. Is well-structured with proper headings
5. Follows documentation best practices

Generate ONLY the Markdown content, no explanations or code blocks around it.
Focus on clear, concise documentation.
"""
        
        response = await self.claude_agent.a_generate_reply(
            messages=[{"role": "user", "content": generation_prompt}]
        )
        
        return self._extract_code_from_response(response)
        
    async def generate_json_content(self, file_path: str, content_spec: Dict[str, Any], work_package: Dict[str, Any]) -> str:
        """Generate JSON file content"""
        
        generation_prompt = f"""
Generate JSON configuration for file: {file_path}

WORK PACKAGE CONTEXT:
{json.dumps(work_package, indent=2)}

CONTENT SPECIFICATION:
{json.dumps(content_spec, indent=2)}

Create JSON that:
1. Includes all specified configuration
2. Follows proper JSON structure
3. Uses appropriate data types
4. Is well-formatted and readable

Generate ONLY the JSON content, no explanations or markdown formatting.
"""
        
        response = await self.claude_agent.a_generate_reply(
            messages=[{"role": "user", "content": generation_prompt}]
        )
        
        return self._extract_code_from_response(response)
        
    async def generate_generic_content(self, file_path: str, content_spec: Dict[str, Any], work_package: Dict[str, Any]) -> str:
        """Generate generic file content"""
        
        generation_prompt = f"""
Generate appropriate content for file: {file_path}

WORK PACKAGE CONTEXT:
{json.dumps(work_package, indent=2)}

CONTENT SPECIFICATION:
{json.dumps(content_spec, indent=2)}

Create content that:
1. Matches the file type and purpose
2. Implements specified requirements
3. Follows appropriate conventions
4. Is production-ready

Generate ONLY the file content, no explanations or markdown formatting.
"""
        
        response = await self.claude_agent.a_generate_reply(
            messages=[{"role": "user", "content": generation_prompt}]
        )
        
        return self._extract_code_from_response(response)
        
    def _determine_file_type(self, file_path: str) -> str:
        """Determine file type from file extension"""
        extension = file_path.split('.')[-1].lower()
        
        type_mapping = {
            'py': 'python',
            'js': 'javascript',
            'ts': 'javascript',
            'html': 'html',
            'htm': 'html',
            'css': 'css',
            'scss': 'css',
            'sass': 'css',
            'md': 'markdown',
            'rst': 'markdown',
            'json': 'json',
            'yaml': 'yaml',
            'yml': 'yaml',
            'xml': 'xml',
            'txt': 'text'
        }
        
        return type_mapping.get(extension, 'generic')
        
    def _extract_code_from_response(self, response) -> str:
        """Extract code content from Claude response, removing markdown formatting"""
        
        if isinstance(response, dict):
            content = response.get('content', str(response))
        else:
            content = str(response)
            
        # Remove code block formatting if present
        if '```' in content:
            # Find first and last code block markers
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
        
    def get_completion_status(self) -> Dict[str, Any]:
        """Get completion status for this agent"""
        return {
            "agent": self.name,
            "specialization": self.specialization,
            "completed_packages": self.completed_packages,
            "total_completed": len(self.completed_packages)
        } 