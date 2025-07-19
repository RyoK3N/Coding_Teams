import asyncio
import os
import json
from typing import Dict, List, Any, Optional
from autogen import AssistantAgent
from src.agents.base_agent import BaseAgent, MessageTag

class FrontendEngineer(BaseAgent):
    def __init__(self, claude_config: Dict[str, Any], workspace_path: str = "./workspace", tools=None):
        super().__init__(
            name="frontend_engineer",
            role="Frontend Engineer (FE)",
            system_prompt="""
You are a Frontend Engineer for a multi-agent coding team. Your primary responsibilities are:

1. Create responsive and interactive user interfaces
2. Implement client-side logic and state management
3. Integrate with backend APIs
4. Ensure cross-browser compatibility
5. Optimize for performance and accessibility
6. Write frontend tests
7. Implement modern UI/UX patterns

When implementing frontend features:
- Use modern JavaScript frameworks and libraries
- Write clean, maintainable code
- Implement responsive design principles
- Follow accessibility guidelines
- Optimize for performance
- Handle errors gracefully
- Write comprehensive tests

Communication style:
- Focus on user experience and interface design
- Provide clear examples and demonstrations
- Consider mobile-first approaches
- Ensure accessibility compliance
""",
            tools=tools
        )
        
        self.claude_agent = AssistantAgent(
            name="frontend_engineer_claude",
            llm_config=claude_config,
            system_message=self.system_prompt,
            human_input_mode="NEVER"
        )
        
        self.workspace_path = workspace_path
        self.components = []
        self.pages = []
        
    def get_success_signal(self) -> str:
        return "FRONTEND_COMPLETE"
        
    def get_termination_signal(self) -> str:
        return "FE_EXIT"
        
    async def execute_step(self, step_info: Dict[str, Any]) -> None:
        step_name = step_info.get("step_name", "").lower()
        
        if "frontend" in step_name or "ui" in step_name or "interface" in step_name:
            await self.implement_frontend(step_info)
        elif "component" in step_name:
            await self.create_components(step_info)
        elif "style" in step_name or "css" in step_name:
            await self.implement_styling(step_info)
        else:
            await self.implement_frontend(step_info)
            
    async def implement_frontend(self, step_info: Dict[str, Any]) -> None:
        await self.signal_step_start(step_info["step_name"])
        
        step_name = step_info.get("step_name", "")
        step_description = step_info.get("description", "")
        deliverables = step_info.get("deliverables", [])
        
        self.logger.info(f"Implementing frontend for: {step_description}")
        
        # Generate appropriate frontend based on problem description
        frontend_code = self._generate_frontend_for_problem(step_description, step_name, deliverables)
        
        artifacts = []
        
        # Write HTML file
        if frontend_code["html"]:
            success = await self.write_file("frontend/index.html", frontend_code["html"])
            if success:
                artifacts.append("frontend/index.html")
                self.logger.info("Created index.html")
        
        # Write CSS file
        if frontend_code["css"]:
            success = await self.write_file("frontend/styles.css", frontend_code["css"])
            if success:
                artifacts.append("frontend/styles.css")
                self.logger.info("Created styles.css")
        
        # Write JavaScript file
        if frontend_code["javascript"]:
            success = await self.write_file("frontend/app.js", frontend_code["javascript"])
            if success:
                artifacts.append("frontend/app.js")
                self.logger.info("Created app.js")
        
        # Write package.json if needed
        if frontend_code.get("package_json"):
            success = await self.write_file("frontend/package.json", frontend_code["package_json"])
            if success:
                artifacts.append("frontend/package.json")
                self.logger.info("Created package.json")
        
        self.report_progress(f"Frontend implementation completed with {len(artifacts)} files generated")
        await self.signal_step_success(step_info["step_name"], "Frontend implementation completed successfully", artifacts)
    
    def _generate_frontend_for_problem(self, description: str, step_name: str, deliverables: List[str]) -> Dict[str, str]:
        """Generate frontend code based on problem description"""
        
        description_lower = description.lower()
        
        if "calculator" in description_lower:
            return self._generate_calculator_frontend()
        elif "cnn" in description_lower or "object detection" in description_lower or "ml model" in description_lower:
            return self._generate_ml_frontend()
        elif "blog" in description_lower:
            return self._generate_blog_frontend()
        elif "chat" in description_lower:
            return self._generate_chat_frontend()
        else:
            return self._generate_generic_frontend(description)
    
    def _generate_calculator_frontend(self) -> Dict[str, str]:
        """Generate frontend for calculator web app"""
        
        html = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Calculator Web App</title>
    <link rel="stylesheet" href="styles.css">
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600&display=swap" rel="stylesheet">
</head>
<body>
    <div class="container">
        <div class="calculator">
            <div class="calculator-header">
                <h1>Calculator</h1>
                <div class="theme-toggle">
                    <button id="theme-btn" class="theme-btn" title="Toggle Dark Mode">🌙</button>
                </div>
            </div>
            
            <div class="display-container">
                <div class="expression" id="expression"></div>
                <div class="result" id="result">0</div>
            </div>
            
            <div class="buttons">
                <button class="btn btn-clear" data-action="clear">C</button>
                <button class="btn btn-operator" data-action="delete">⌫</button>
                <button class="btn btn-operator" data-value="(">(</button>
                <button class="btn btn-operator" data-value=")">)</button>
                
                <button class="btn btn-number" data-value="7">7</button>
                <button class="btn btn-number" data-value="8">8</button>
                <button class="btn btn-number" data-value="9">9</button>
                <button class="btn btn-operator" data-value="/">÷</button>
                
                <button class="btn btn-number" data-value="4">4</button>
                <button class="btn btn-number" data-value="5">5</button>
                <button class="btn btn-number" data-value="6">6</button>
                <button class="btn btn-operator" data-value="*">×</button>
                
                <button class="btn btn-number" data-value="1">1</button>
                <button class="btn btn-number" data-value="2">2</button>
                <button class="btn btn-number" data-value="3">3</button>
                <button class="btn btn-operator" data-value="-">-</button>
                
                <button class="btn btn-number" data-value="0" id="zero">0</button>
                <button class="btn btn-number" data-value=".">.</button>
                <button class="btn btn-equals" data-action="calculate">=</button>
                <button class="btn btn-operator" data-value="+">+</button>
            </div>
            
            <div class="history-section">
                <h3>History</h3>
                <div class="history" id="history"></div>
                <button class="btn btn-clear-history" id="clear-history">Clear History</button>
            </div>
        </div>
        
        <div class="api-info">
            <h3>API Information</h3>
            <p>Backend API: <span id="api-status">Checking...</span></p>
            <button class="btn btn-test-api" id="test-api">Test API</button>
        </div>
    </div>
    
    <div class="error-modal" id="error-modal">
        <div class="modal-content">
            <span class="close" id="close-modal">&times;</span>
            <h3>Error</h3>
            <p id="error-message"></p>
        </div>
    </div>
    
    <script src="app.js"></script>
</body>
</html>"""
        
        css = """/* Calculator Web App Styles */
:root {
    --primary-color: #667eea;
    --secondary-color: #764ba2;
    --background: #f8fafc;
    --card-background: #ffffff;
    --text-primary: #1a202c;
    --text-secondary: #718096;
    --border-color: #e2e8f0;
    --button-bg: #f7fafc;
    --button-hover: #edf2f7;
    --operator-bg: #667eea;
    --operator-hover: #5a67d8;
    --equals-bg: #48bb78;
    --equals-hover: #38a169;
    --clear-bg: #f56565;
    --clear-hover: #e53e3e;
    --shadow: 0 4px 6px rgba(0, 0, 0, 0.07);
    --shadow-lg: 0 10px 15px rgba(0, 0, 0, 0.1);
}

[data-theme="dark"] {
    --background: #1a202c;
    --card-background: #2d3748;
    --text-primary: #f7fafc;
    --text-secondary: #a0aec0;
    --border-color: #4a5568;
    --button-bg: #4a5568;
    --button-hover: #718096;
}

* {
    margin: 0;
    padding: 0;
    box-sizing: border-box;
}

body {
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    background: var(--background);
    color: var(--text-primary);
    line-height: 1.6;
    transition: all 0.3s ease;
}

.container {
    max-width: 1200px;
    margin: 0 auto;
    padding: 2rem;
    display: grid;
    grid-template-columns: 1fr auto;
    gap: 2rem;
    align-items: start;
}

.calculator {
    background: var(--card-background);
    border-radius: 20px;
    padding: 2rem;
    box-shadow: var(--shadow-lg);
    max-width: 400px;
    border: 1px solid var(--border-color);
}

.calculator-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 2rem;
}

.calculator-header h1 {
    color: var(--text-primary);
    font-size: 1.5rem;
    font-weight: 600;
}

.theme-btn {
    background: var(--button-bg);
    border: 1px solid var(--border-color);
    border-radius: 10px;
    padding: 0.5rem;
    cursor: pointer;
    font-size: 1.2rem;
    transition: all 0.3s ease;
}

.theme-btn:hover {
    background: var(--button-hover);
    transform: scale(1.05);
}

.display-container {
    background: var(--background);
    border-radius: 15px;
    padding: 1.5rem;
    margin-bottom: 2rem;
    text-align: right;
    border: 1px solid var(--border-color);
}

.expression {
    color: var(--text-secondary);
    font-size: 0.9rem;
    min-height: 1.2rem;
    margin-bottom: 0.5rem;
}

.result {
    color: var(--text-primary);
    font-size: 2rem;
    font-weight: 500;
    min-height: 2.5rem;
    overflow-wrap: break-word;
}

.buttons {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 0.75rem;
    margin-bottom: 2rem;
}

.btn {
    background: var(--button-bg);
    border: 1px solid var(--border-color);
    border-radius: 12px;
    padding: 1rem;
    font-size: 1.1rem;
    font-weight: 500;
    cursor: pointer;
    transition: all 0.2s ease;
    color: var(--text-primary);
    min-height: 60px;
    display: flex;
    align-items: center;
    justify-content: center;
}

.btn:hover {
    background: var(--button-hover);
    transform: translateY(-1px);
    box-shadow: var(--shadow);
}

.btn:active {
    transform: translateY(0);
}

.btn-operator {
    background: var(--operator-bg);
    color: white;
}

.btn-operator:hover {
    background: var(--operator-hover);
}

.btn-equals {
    background: var(--equals-bg);
    color: white;
}

.btn-equals:hover {
    background: var(--equals-hover);
}

.btn-clear {
    background: var(--clear-bg);
    color: white;
}

.btn-clear:hover {
    background: var(--clear-hover);
}

#zero {
    grid-column: span 1;
}

.history-section {
    border-top: 1px solid var(--border-color);
    padding-top: 1.5rem;
}

.history-section h3 {
    margin-bottom: 1rem;
    color: var(--text-primary);
    font-size: 1rem;
    font-weight: 600;
}

.history {
    max-height: 150px;
    overflow-y: auto;
    margin-bottom: 1rem;
}

.history-item {
    padding: 0.5rem;
    background: var(--background);
    border-radius: 8px;
    margin-bottom: 0.5rem;
    cursor: pointer;
    transition: all 0.2s ease;
    border: 1px solid var(--border-color);
}

.history-item:hover {
    background: var(--button-hover);
    transform: translateX(4px);
}

.btn-clear-history {
    width: 100%;
    background: var(--text-secondary);
    color: white;
    padding: 0.75rem;
}

.btn-clear-history:hover {
    background: var(--text-primary);
}

.api-info {
    background: var(--card-background);
    border-radius: 15px;
    padding: 1.5rem;
    box-shadow: var(--shadow);
    border: 1px solid var(--border-color);
    min-width: 250px;
}

.api-info h3 {
    margin-bottom: 1rem;
    color: var(--text-primary);
}

.btn-test-api {
    width: 100%;
    margin-top: 1rem;
}

.error-modal {
    display: none;
    position: fixed;
    z-index: 1000;
    left: 0;
    top: 0;
    width: 100%;
    height: 100%;
    background-color: rgba(0, 0, 0, 0.5);
}

.modal-content {
    background-color: var(--card-background);
    margin: 15% auto;
    padding: 2rem;
    border-radius: 15px;
    width: 90%;
    max-width: 400px;
    box-shadow: var(--shadow-lg);
}

.close {
    color: var(--text-secondary);
    float: right;
    font-size: 2rem;
    font-weight: bold;
    cursor: pointer;
    line-height: 1;
}

.close:hover {
    color: var(--text-primary);
}

@media (max-width: 768px) {
    .container {
        grid-template-columns: 1fr;
        padding: 1rem;
    }
    
    .calculator {
        max-width: 100%;
    }
    
    .buttons {
        gap: 0.5rem;
    }
    
    .btn {
        min-height: 50px;
        font-size: 1rem;
    }
}

/* Animations */
@keyframes fadeIn {
    from { opacity: 0; transform: translateY(20px); }
    to { opacity: 1; transform: translateY(0); }
}

.calculator {
    animation: fadeIn 0.5s ease-out;
}

.history-item {
    animation: fadeIn 0.3s ease-out;
}

/* Loading state */
.loading {
    opacity: 0.6;
    pointer-events: none;
}

/* Success/Error states */
.success {
    border-color: var(--equals-bg) !important;
    box-shadow: 0 0 0 3px rgba(72, 187, 120, 0.1);
}

.error {
    border-color: var(--clear-bg) !important;
    box-shadow: 0 0 0 3px rgba(245, 101, 101, 0.1);
}"""
        
        javascript = """// Calculator Web App JavaScript
class Calculator {
    constructor() {
        this.expression = '';
        this.result = '0';
        this.history = JSON.parse(localStorage.getItem('calculator-history')) || [];
        this.apiBaseUrl = 'http://localhost:8000';
        
        this.init();
    }
    
    init() {
        this.bindEvents();
        this.updateDisplay();
        this.updateHistory();
        this.checkApiStatus();
        this.loadTheme();
    }
    
    bindEvents() {
        // Button clicks
        document.querySelectorAll('.btn').forEach(btn => {
            btn.addEventListener('click', this.handleButtonClick.bind(this));
        });
        
        // Keyboard support
        document.addEventListener('keydown', this.handleKeyDown.bind(this));
        
        // Theme toggle
        document.getElementById('theme-btn').addEventListener('click', this.toggleTheme.bind(this));
        
        // API test
        document.getElementById('test-api').addEventListener('click', this.testApi.bind(this));
        
        // Clear history
        document.getElementById('clear-history').addEventListener('click', this.clearHistory.bind(this));
        
        // Modal close
        document.getElementById('close-modal').addEventListener('click', this.closeModal.bind(this));
        
        // History item clicks
        document.getElementById('history').addEventListener('click', this.handleHistoryClick.bind(this));
    }
    
    handleButtonClick(e) {
        const btn = e.target;
        const value = btn.dataset.value;
        const action = btn.dataset.action;
        
        if (action) {
            this.handleAction(action);
        } else if (value) {
            this.addToExpression(value);
        }
    }
    
    handleKeyDown(e) {
        const key = e.key;
        
        if (/[0-9]/.test(key)) {
            this.addToExpression(key);
        } else if (['+', '-', '*', '/', '(', ')', '.'].includes(key)) {
            this.addToExpression(key);
        } else if (key === 'Enter' || key === '=') {
            e.preventDefault();
            this.calculate();
        } else if (key === 'Escape' || key === 'c' || key === 'C') {
            this.clear();
        } else if (key === 'Backspace') {
            this.delete();
        }
    }
    
    handleAction(action) {
        switch (action) {
            case 'clear':
                this.clear();
                break;
            case 'delete':
                this.delete();
                break;
            case 'calculate':
                this.calculate();
                break;
        }
    }
    
    addToExpression(value) {
        // Convert display symbols back to mathematical operators
        const convertedValue = value === '×' ? '*' : value === '÷' ? '/' : value;
        
        this.expression += convertedValue;
        this.updateDisplay();
    }
    
    clear() {
        this.expression = '';
        this.result = '0';
        this.updateDisplay();
    }
    
    delete() {
        this.expression = this.expression.slice(0, -1);
        this.updateDisplay();
    }
    
    async calculate() {
        if (!this.expression.trim()) return;
        
        try {
            this.setLoading(true);
            
            const response = await fetch(`${this.apiBaseUrl}/calculate`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ expression: this.expression })
            });
            
            const data = await response.json();
            
            if (response.ok) {
                this.result = data.result.toString();
                this.addToHistory(this.expression, this.result);
                this.expression = '';
                this.showSuccess();
            } else {
                this.showError(data.detail || 'Calculation error');
            }
        } catch (error) {
            console.error('API Error:', error);
            
            // Fallback to local calculation
            try {
                const localResult = this.calculateLocally(this.expression);
                this.result = localResult.toString();
                this.addToHistory(this.expression, this.result);
                this.expression = '';
                this.showSuccess();
            } catch (localError) {
                this.showError('Invalid expression');
            }
        } finally {
            this.setLoading(false);
            this.updateDisplay();
        }
    }
    
    calculateLocally(expression) {
        // Basic local calculation as fallback
        // Remove spaces and validate
        const cleaned = expression.replace(/\\s/g, '');
        
        // Basic validation
        if (!/^[0-9+\\-*/.()]+$/.test(cleaned)) {
            throw new Error('Invalid characters');
        }
        
        // Evaluate safely (basic implementation)
        return Function('"use strict"; return (' + cleaned + ')')();
    }
    
    updateDisplay() {
        document.getElementById('expression').textContent = this.formatExpression(this.expression);
        document.getElementById('result').textContent = this.formatNumber(this.result);
    }
    
    formatExpression(expr) {
        return expr.replace(/\\*/g, '×').replace(/\\//g, '÷') || '';
    }
    
    formatNumber(num) {
        if (num === '0' || num === '') return '0';
        
        const parsed = parseFloat(num);
        if (isNaN(parsed)) return num;
        
        // Format large numbers with commas
        return parsed.toLocaleString('en-US', {
            maximumFractionDigits: 10
        });
    }
    
    addToHistory(expression, result) {
        const historyItem = {
            expression: this.formatExpression(expression),
            result: this.formatNumber(result),
            timestamp: new Date().toLocaleTimeString()
        };
        
        this.history.unshift(historyItem);
        
        // Limit history to 50 items
        if (this.history.length > 50) {
            this.history = this.history.slice(0, 50);
        }
        
        this.saveHistory();
        this.updateHistory();
    }
    
    updateHistory() {
        const historyContainer = document.getElementById('history');
        
        if (this.history.length === 0) {
            historyContainer.innerHTML = '<p style="color: var(--text-secondary); font-style: italic;">No calculations yet</p>';
            return;
        }
        
        historyContainer.innerHTML = this.history.map(item => `
            <div class="history-item" data-expression="${item.expression.replace(/×/g, '*').replace(/÷/g, '/')}">
                <div style="font-weight: 500;">${item.expression} = ${item.result}</div>
                <div style="font-size: 0.8rem; color: var(--text-secondary);">${item.timestamp}</div>
            </div>
        `).join('');
    }
    
    handleHistoryClick(e) {
        const historyItem = e.target.closest('.history-item');
        if (historyItem) {
            const expression = historyItem.dataset.expression;
            this.expression = expression;
            this.updateDisplay();
        }
    }
    
    clearHistory() {
        this.history = [];
        this.saveHistory();
        this.updateHistory();
    }
    
    saveHistory() {
        localStorage.setItem('calculator-history', JSON.stringify(this.history));
    }
    
    async checkApiStatus() {
        try {
            const response = await fetch(`${this.apiBaseUrl}/health`);
            const status = response.ok ? 'Online ✅' : 'Offline ❌';
            document.getElementById('api-status').textContent = status;
        } catch (error) {
            document.getElementById('api-status').textContent = 'Offline ❌';
        }
    }
    
    async testApi() {
        try {
            this.setLoading(true);
            const response = await fetch(`${this.apiBaseUrl}/calculate`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ expression: '2 + 2' })
            });
            
            const data = await response.json();
            
            if (response.ok && data.result === 4) {
                alert('API test successful! ✅');
                this.checkApiStatus();
            } else {
                alert('API test failed ❌');
            }
        } catch (error) {
            alert('API test failed: ' + error.message);
        } finally {
            this.setLoading(false);
        }
    }
    
    toggleTheme() {
        const currentTheme = document.documentElement.getAttribute('data-theme');
        const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
        
        document.documentElement.setAttribute('data-theme', newTheme);
        localStorage.setItem('calculator-theme', newTheme);
        
        // Update theme button
        const themeBtn = document.getElementById('theme-btn');
        themeBtn.textContent = newTheme === 'dark' ? '☀️' : '🌙';
    }
    
    loadTheme() {
        const savedTheme = localStorage.getItem('calculator-theme') || 'light';
        document.documentElement.setAttribute('data-theme', savedTheme);
        
        const themeBtn = document.getElementById('theme-btn');
        themeBtn.textContent = savedTheme === 'dark' ? '☀️' : '🌙';
    }
    
    showError(message) {
        document.getElementById('error-message').textContent = message;
        document.getElementById('error-modal').style.display = 'block';
        
        // Auto-close after 3 seconds
        setTimeout(() => {
            this.closeModal();
        }, 3000);
    }
    
    closeModal() {
        document.getElementById('error-modal').style.display = 'none';
    }
    
    showSuccess() {
        const calculator = document.querySelector('.calculator');
        calculator.classList.add('success');
        
        setTimeout(() => {
            calculator.classList.remove('success');
        }, 1000);
    }
    
    setLoading(loading) {
        const calculator = document.querySelector('.calculator');
        if (loading) {
            calculator.classList.add('loading');
        } else {
            calculator.classList.remove('loading');
        }
    }
}

// Initialize calculator when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    new Calculator();
});

// Service Worker for offline functionality (optional)
if ('serviceWorker' in navigator) {
    window.addEventListener('load', () => {
        navigator.serviceWorker.register('/sw.js')
            .then(registration => {
                console.log('SW registered: ', registration);
            })
            .catch(registrationError => {
                console.log('SW registration failed: ', registrationError);
            });
    });
}"""
        
        package_json = """{
  "name": "calculator-web-app",
  "version": "1.0.0",
  "description": "A modern calculator web application",
  "main": "index.html",
  "scripts": {
    "start": "npx http-server . -p 3000",
    "dev": "npx live-server --port=3000",
    "build": "echo 'Static app - no build needed'",
    "test": "echo 'No tests specified'"
  },
  "keywords": ["calculator", "webapp", "javascript"],
  "author": "Auto-Gen Team",
  "license": "MIT",
  "devDependencies": {
    "http-server": "^14.1.1",
    "live-server": "^1.2.2"
  }
}"""
        
        return {
            "html": html,
            "css": css,
            "javascript": javascript,
            "package_json": package_json
        }
    
    def _generate_ml_frontend(self) -> Dict[str, str]:
        """Generate frontend for ML/image upload applications"""
        
        html = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>ML Object Detection</title>
    <link rel="stylesheet" href="styles.css">
</head>
<body>
    <div class="container">
        <h1>Object Detection System</h1>
        
        <div class="upload-section">
            <div class="upload-area" id="upload-area">
                <div class="upload-content">
                    <div class="upload-icon">📸</div>
                    <h3>Upload Image for Detection</h3>
                    <p>Drag and drop an image here or click to select</p>
                    <input type="file" id="file-input" accept="image/*" hidden>
                    <button class="upload-btn">Choose Image</button>
                </div>
            </div>
        </div>
        
        <div class="preview-section" id="preview-section" style="display: none;">
            <div class="image-container">
                <img id="preview-image" alt="Preview">
                <canvas id="detection-canvas"></canvas>
            </div>
            <div class="results">
                <h3>Detection Results</h3>
                <div id="results-list"></div>
                <button class="btn btn-secondary" id="clear-btn">Clear & Upload New</button>
            </div>
        </div>
        
        <div class="loading" id="loading" style="display: none;">
            <div class="spinner"></div>
            <p>Processing image...</p>
        </div>
    </div>
    
    <script src="app.js"></script>
</body>
</html>"""
        
        css = """/* ML Frontend Styles */
* {
    margin: 0;
    padding: 0;
    box-sizing: border-box;
}

body {
    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    min-height: 100vh;
    color: #333;
}

.container {
    max-width: 1200px;
    margin: 0 auto;
    padding: 2rem;
}

h1 {
    text-align: center;
    color: white;
    margin-bottom: 2rem;
    font-size: 2.5rem;
    text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
}

.upload-section {
    margin-bottom: 2rem;
}

.upload-area {
    background: white;
    border: 3px dashed #ddd;
    border-radius: 15px;
    padding: 3rem;
    text-align: center;
    transition: all 0.3s ease;
    cursor: pointer;
}

.upload-area:hover,
.upload-area.dragover {
    border-color: #667eea;
    background: #f8f9ff;
    transform: translateY(-2px);
}

.upload-icon {
    font-size: 4rem;
    margin-bottom: 1rem;
}

.upload-btn {
    background: #667eea;
    color: white;
    border: none;
    padding: 1rem 2rem;
    border-radius: 8px;
    font-size: 1.1rem;
    cursor: pointer;
    margin-top: 1rem;
    transition: all 0.3s ease;
}

.upload-btn:hover {
    background: #5a67d8;
    transform: translateY(-2px);
}

.preview-section {
    display: grid;
    grid-template-columns: 2fr 1fr;
    gap: 2rem;
    background: white;
    border-radius: 15px;
    padding: 2rem;
    box-shadow: 0 10px 30px rgba(0,0,0,0.2);
}

.image-container {
    position: relative;
}

#preview-image {
    max-width: 100%;
    border-radius: 10px;
    box-shadow: 0 5px 15px rgba(0,0,0,0.3);
}

#detection-canvas {
    position: absolute;
    top: 0;
    left: 0;
    pointer-events: none;
}

.results h3 {
    margin-bottom: 1rem;
    color: #333;
}

.result-item {
    background: #f8f9ff;
    padding: 1rem;
    margin-bottom: 0.5rem;
    border-radius: 8px;
    border-left: 4px solid #667eea;
}

.confidence {
    font-weight: bold;
    color: #667eea;
}

.loading {
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background: rgba(0,0,0,0.8);
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    color: white;
    z-index: 1000;
}

.spinner {
    width: 50px;
    height: 50px;
    border: 5px solid #f3f3f3;
    border-top: 5px solid #667eea;
    border-radius: 50%;
    animation: spin 1s linear infinite;
    margin-bottom: 1rem;
}

@keyframes spin {
    0% { transform: rotate(0deg); }
    100% { transform: rotate(360deg); }
}

.btn {
    padding: 0.75rem 1.5rem;
    border: none;
    border-radius: 8px;
    cursor: pointer;
    font-size: 1rem;
    transition: all 0.3s ease;
}

.btn-secondary {
    background: #718096;
    color: white;
}

.btn-secondary:hover {
    background: #4a5568;
}

@media (max-width: 768px) {
    .preview-section {
        grid-template-columns: 1fr;
    }
    
    .container {
        padding: 1rem;
    }
    
    h1 {
        font-size: 2rem;
    }
}"""
        
        javascript = """// ML Frontend JavaScript
class MLDetectionApp {
    constructor() {
        this.apiUrl = 'http://localhost:8000';
        this.init();
    }
    
    init() {
        this.bindEvents();
    }
    
    bindEvents() {
        const uploadArea = document.getElementById('upload-area');
        const fileInput = document.getElementById('file-input');
        const clearBtn = document.getElementById('clear-btn');
        
        uploadArea.addEventListener('click', () => fileInput.click());
        uploadArea.addEventListener('dragover', this.handleDragOver.bind(this));
        uploadArea.addEventListener('drop', this.handleDrop.bind(this));
        fileInput.addEventListener('change', this.handleFileSelect.bind(this));
        clearBtn.addEventListener('click', this.clearResults.bind(this));
    }
    
    handleDragOver(e) {
        e.preventDefault();
        e.target.classList.add('dragover');
    }
    
    handleDrop(e) {
        e.preventDefault();
        e.target.classList.remove('dragover');
        
        const files = e.dataTransfer.files;
        if (files.length > 0) {
            this.processFile(files[0]);
        }
    }
    
    handleFileSelect(e) {
        const file = e.target.files[0];
        if (file) {
            this.processFile(file);
        }
    }
    
    async processFile(file) {
        if (!file.type.startsWith('image/')) {
            alert('Please select an image file');
            return;
        }
        
        this.showLoading();
        
        try {
            // Show preview
            const imageUrl = URL.createObjectURL(file);
            await this.showPreview(imageUrl);
            
            // Send to API
            const formData = new FormData();
            formData.append('file', file);
            
            const response = await fetch(`${this.apiUrl}/predict`, {
                method: 'POST',
                body: formData
            });
            
            const result = await response.json();
            
            if (response.ok) {
                this.displayResults(result);
                this.drawDetections(result.objects_detected || []);
            } else {
                throw new Error(result.detail || 'Detection failed');
            }
        } catch (error) {
            console.error('Error:', error);
            alert('Error processing image: ' + error.message);
        } finally {
            this.hideLoading();
        }
    }
    
    async showPreview(imageUrl) {
        const previewSection = document.getElementById('preview-section');
        const previewImage = document.getElementById('preview-image');
        
        previewImage.src = imageUrl;
        previewSection.style.display = 'grid';
        
        // Wait for image to load
        return new Promise((resolve) => {
            previewImage.onload = resolve;
        });
    }
    
    displayResults(results) {
        const resultsList = document.getElementById('results-list');
        
        if (!results.objects_detected || results.objects_detected.length === 0) {
            resultsList.innerHTML = '<p>No objects detected</p>';
            return;
        }
        
        const html = results.objects_detected.map(obj => `
            <div class="result-item">
                <div><strong>${obj.class || obj.class_name}</strong></div>
                <div class="confidence">Confidence: ${(obj.confidence * 100).toFixed(1)}%</div>
            </div>
        `).join('');
        
        resultsList.innerHTML = html;
    }
    
    drawDetections(detections) {
        const canvas = document.getElementById('detection-canvas');
        const image = document.getElementById('preview-image');
        const ctx = canvas.getContext('2d');
        
        // Set canvas size to match image
        canvas.width = image.offsetWidth;
        canvas.height = image.offsetHeight;
        
        // Clear canvas
        ctx.clearRect(0, 0, canvas.width, canvas.height);
        
        // Draw bounding boxes
        detections.forEach((detection, index) => {
            const bbox = detection.bbox;
            if (!bbox || bbox.length < 4) return;
            
            const [x, y, width, height] = bbox;
            const scaleX = canvas.width / image.naturalWidth;
            const scaleY = canvas.height / image.naturalHeight;
            
            const scaledX = x * scaleX;
            const scaledY = y * scaleY;
            const scaledWidth = width * scaleX;
            const scaledHeight = height * scaleY;
            
            // Draw rectangle
            ctx.strokeStyle = `hsl(${index * 60}, 70%, 50%)`;
            ctx.lineWidth = 3;
            ctx.strokeRect(scaledX, scaledY, scaledWidth, scaledHeight);
            
            // Draw label
            const label = `${detection.class || detection.class_name} (${(detection.confidence * 100).toFixed(1)}%)`;
            ctx.fillStyle = ctx.strokeStyle;
            ctx.font = '14px Arial';
            ctx.fillText(label, scaledX, scaledY - 5);
        });
    }
    
    clearResults() {
        document.getElementById('preview-section').style.display = 'none';
        document.getElementById('file-input').value = '';
    }
    
    showLoading() {
        document.getElementById('loading').style.display = 'flex';
    }
    
    hideLoading() {
        document.getElementById('loading').style.display = 'none';
    }
}

// Initialize app when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    new MLDetectionApp();
});"""
        
        return {
            "html": html,
            "css": css,
            "javascript": javascript,
            "package_json": ""
        }
    
    def _generate_generic_frontend(self, description: str) -> Dict[str, str]:
        """Generate generic frontend"""
        
        html = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Web Application</title>
    <link rel="stylesheet" href="styles.css">
</head>
<body>
    <div class="container">
        <header>
            <h1>Web Application</h1>
        </header>
        
        <main>
            <section class="hero">
                <h2>Welcome to our application</h2>
                <p>This is a modern web application built with clean HTML, CSS, and JavaScript.</p>
                <button class="btn btn-primary" id="get-started">Get Started</button>
            </section>
            
            <section class="features">
                <div class="feature">
                    <h3>Feature 1</h3>
                    <p>Description of the first feature</p>
                </div>
                <div class="feature">
                    <h3>Feature 2</h3>
                    <p>Description of the second feature</p>
                </div>
                <div class="feature">
                    <h3>Feature 3</h3>
                    <p>Description of the third feature</p>
                </div>
            </section>
        </main>
        
        <footer>
            <p>&copy; 2024 Web Application. All rights reserved.</p>
        </footer>
    </div>
    
    <script src="app.js"></script>
</body>
</html>"""
        
        css = """/* Generic Frontend Styles */
* {
    margin: 0;
    padding: 0;
    box-sizing: border-box;
}

body {
    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    line-height: 1.6;
    color: #333;
}

.container {
    max-width: 1200px;
    margin: 0 auto;
    padding: 0 1rem;
}

header {
    background: #333;
    color: white;
    text-align: center;
    padding: 2rem 0;
}

.hero {
    text-align: center;
    padding: 4rem 0;
    background: linear-gradient(135deg, #667eea, #764ba2);
    color: white;
    margin-bottom: 3rem;
}

.hero h2 {
    font-size: 2.5rem;
    margin-bottom: 1rem;
}

.btn {
    display: inline-block;
    padding: 0.75rem 1.5rem;
    text-decoration: none;
    border-radius: 5px;
    transition: all 0.3s ease;
    border: none;
    cursor: pointer;
    font-size: 1rem;
}

.btn-primary {
    background: #007bff;
    color: white;
}

.btn-primary:hover {
    background: #0056b3;
    transform: translateY(-2px);
}

.features {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
    gap: 2rem;
    margin-bottom: 3rem;
}

.feature {
    background: white;
    padding: 2rem;
    border-radius: 8px;
    box-shadow: 0 2px 10px rgba(0,0,0,0.1);
    transition: transform 0.3s ease;
}

.feature:hover {
    transform: translateY(-5px);
}

footer {
    background: #333;
    color: white;
    text-align: center;
    padding: 2rem 0;
    margin-top: 3rem;
}

@media (max-width: 768px) {
    .hero h2 {
        font-size: 2rem;
    }
    
    .features {
        grid-template-columns: 1fr;
    }
}"""
        
        javascript = """// Generic Frontend JavaScript
class WebApp {
    constructor() {
        this.init();
    }
    
    init() {
        this.bindEvents();
        console.log('Web application initialized');
    }
    
    bindEvents() {
        const getStartedBtn = document.getElementById('get-started');
        if (getStartedBtn) {
            getStartedBtn.addEventListener('click', this.handleGetStarted.bind(this));
        }
    }
    
    handleGetStarted() {
        alert('Welcome to the application!');
    }
}

// Initialize app when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    new WebApp();
});"""
        
        return {
            "html": html,
            "css": css,
            "javascript": javascript,
            "package_json": ""
        }
    
    def _generate_blog_frontend(self) -> Dict[str, str]:
        return self._generate_generic_frontend("blog application")
    
    def _generate_chat_frontend(self) -> Dict[str, str]:
        return self._generate_generic_frontend("chat application")
    
    async def create_components(self, step_info: Dict[str, Any]) -> None:
        await self.signal_step_start(step_info["step_name"])
        
        # Create reusable components
        components_js = """// Reusable Components
class UIComponents {
    static createButton(text, className = '', onClick = null) {
        const button = document.createElement('button');
        button.textContent = text;
        button.className = `btn ${className}`;
        if (onClick) button.addEventListener('click', onClick);
        return button;
    }
    
    static createModal(title, content) {
        const modal = document.createElement('div');
        modal.className = 'modal';
        modal.innerHTML = `
            <div class="modal-content">
                <span class="close">&times;</span>
                <h3>${title}</h3>
                <div class="modal-body">${content}</div>
            </div>
        `;
        
        modal.querySelector('.close').addEventListener('click', () => {
            modal.style.display = 'none';
        });
        
        return modal;
    }
    
    static createCard(title, content, imageUrl = null) {
        const card = document.createElement('div');
        card.className = 'card';
        
        const imageHtml = imageUrl ? `<img src="${imageUrl}" alt="${title}" class="card-image">` : '';
        
        card.innerHTML = `
            ${imageHtml}
            <div class="card-content">
                <h3 class="card-title">${title}</h3>
                <p class="card-text">${content}</p>
            </div>
        `;
        
        return card;
    }
}

export default UIComponents;"""
        
        artifacts = []
        success = await self.write_file("frontend/components.js", components_js)
        if success:
            artifacts.append("frontend/components.js")
            
        self.report_progress(f"UI components created: {len(artifacts)} files")
        await self.signal_step_success(step_info["step_name"], "Components creation completed", artifacts)
    
    async def implement_styling(self, step_info: Dict[str, Any]) -> None:
        await self.signal_step_start(step_info["step_name"])
        
        # Create additional styling
        variables_css = """:root {
    /* Colors */
    --primary-color: #667eea;
    --secondary-color: #764ba2;
    --success-color: #48bb78;
    --warning-color: #ed8936;
    --error-color: #f56565;
    --info-color: #4299e1;
    
    /* Backgrounds */
    --bg-primary: #ffffff;
    --bg-secondary: #f7fafc;
    --bg-dark: #1a202c;
    
    /* Text */
    --text-primary: #1a202c;
    --text-secondary: #718096;
    --text-light: #ffffff;
    
    /* Spacing */
    --spacing-xs: 0.25rem;
    --spacing-sm: 0.5rem;
    --spacing-md: 1rem;
    --spacing-lg: 1.5rem;
    --spacing-xl: 2rem;
    
    /* Typography */
    --font-size-sm: 0.875rem;
    --font-size-base: 1rem;
    --font-size-lg: 1.125rem;
    --font-size-xl: 1.25rem;
    --font-size-2xl: 1.5rem;
    --font-size-3xl: 1.875rem;
    
    /* Borders */
    --border-radius-sm: 0.25rem;
    --border-radius-md: 0.5rem;
    --border-radius-lg: 0.75rem;
    --border-radius-xl: 1rem;
    
    /* Shadows */
    --shadow-sm: 0 1px 2px rgba(0, 0, 0, 0.05);
    --shadow-md: 0 4px 6px rgba(0, 0, 0, 0.07);
    --shadow-lg: 0 10px 15px rgba(0, 0, 0, 0.1);
    --shadow-xl: 0 20px 25px rgba(0, 0, 0, 0.1);
}

/* Utility Classes */
.text-center { text-align: center; }
.text-left { text-align: left; }
.text-right { text-align: right; }

.mt-1 { margin-top: var(--spacing-xs); }
.mt-2 { margin-top: var(--spacing-sm); }
.mt-3 { margin-top: var(--spacing-md); }
.mt-4 { margin-top: var(--spacing-lg); }
.mt-5 { margin-top: var(--spacing-xl); }

.mb-1 { margin-bottom: var(--spacing-xs); }
.mb-2 { margin-bottom: var(--spacing-sm); }
.mb-3 { margin-bottom: var(--spacing-md); }
.mb-4 { margin-bottom: var(--spacing-lg); }
.mb-5 { margin-bottom: var(--spacing-xl); }

.p-1 { padding: var(--spacing-xs); }
.p-2 { padding: var(--spacing-sm); }
.p-3 { padding: var(--spacing-md); }
.p-4 { padding: var(--spacing-lg); }
.p-5 { padding: var(--spacing-xl); }

.rounded-sm { border-radius: var(--border-radius-sm); }
.rounded-md { border-radius: var(--border-radius-md); }
.rounded-lg { border-radius: var(--border-radius-lg); }
.rounded-xl { border-radius: var(--border-radius-xl); }

.shadow-sm { box-shadow: var(--shadow-sm); }
.shadow-md { box-shadow: var(--shadow-md); }
.shadow-lg { box-shadow: var(--shadow-lg); }
.shadow-xl { box-shadow: var(--shadow-xl); }

.d-none { display: none; }
.d-block { display: block; }
.d-flex { display: flex; }
.d-grid { display: grid; }

.flex-center {
    display: flex;
    align-items: center;
    justify-content: center;
}

.flex-between {
    display: flex;
    align-items: center;
    justify-content: space-between;
}

.grid-auto {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
    gap: var(--spacing-md);
}"""
        
        artifacts = []
        success = await self.write_file("frontend/variables.css", variables_css)
        if success:
            artifacts.append("frontend/variables.css")
            
        self.report_progress(f"Styling completed: {len(artifacts)} files")
        await self.signal_step_success(step_info["step_name"], "Styling implementation completed", artifacts)
    
    def get_frontend_summary(self) -> Dict[str, Any]:
        return {
            "components": len(self.components),
            "pages": len(self.pages),
            "implementation_status": "completed" if self.components or self.pages else "in_progress"
        } 