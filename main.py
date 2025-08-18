import os
import re
from http import HTTPStatus
from typing import Dict, List, Optional, Tuple
import base64
import mimetypes
import PyPDF2
import docx
import cv2
import numpy as np
from PIL import Image
import pytesseract
import requests
from urllib.parse import urlparse, urljoin
from bs4 import BeautifulSoup
import html2text
import json
import time
import webbrowser
import urllib.parse

import gradio as gr
import ollama
from tavily import TavilyClient
import tempfile

# Gradio supported languages for syntax highlighting
GRADIO_SUPPORTED_LANGUAGES = [
    "python", "c", "cpp", "markdown", "latex", "json", "html", "css", "javascript", "jinja2", "typescript", "yaml", "dockerfile", "shell", "r", "sql", "sql-msSQL", "sql-mySQL", "sql-mariaDB", "sql-sqlite", "sql-cassandra", "sql-plSQL", "sql-hive", "sql-pgSQL", "sql-gql", "sql-gpSQL", "sql-sparkSQL", "sql-esper", None
]

def get_gradio_language(language):
    return language if language in GRADIO_SUPPORTED_LANGUAGES else None

# Search/Replace Constants
SEARCH_START = "<<<<<<< SEARCH"
DIVIDER = "======="
REPLACE_END = ">>>>>>> REPLACE"

# Configuration
HTML_SYSTEM_PROMPT = """ONLY USE HTML, CSS AND JAVASCRIPT. If you want to use ICON make sure to import the library first. Try to create the best UI possible by using only HTML, CSS and JAVASCRIPT. MAKE IT RESPONSIVE USING MODERN CSS. Use as much as you can modern CSS for the styling, if you can't do something with modern CSS, then use custom CSS. Also, try to elaborate as much as you can, to create something unique. ALWAYS GIVE THE RESPONSE INTO A SINGLE HTML FILE

For website redesign tasks:
- Use the provided original HTML code as the starting point for redesign
- Preserve all original content, structure, and functionality
- Keep the same semantic HTML structure but enhance the styling
- Reuse all original images and their URLs from the HTML code
- Create a modern, responsive design with improved typography and spacing
- Use modern CSS frameworks and design patterns
- Ensure accessibility and mobile responsiveness
- Maintain the same navigation and user flow
- Enhance the visual design while keeping the original layout structure

If an image is provided, analyze it and use the visual information to better understand the user's requirements.

Always respond with code that can be executed or rendered directly.

Always output only the HTML code inside a ```html ... ``` code block, and do not include any explanations or extra text. Do NOT add the language name at the top of the code output."""

TRANSFORMERS_JS_SYSTEM_PROMPT = """You are an expert web developer creating a transformers.js application. You will generate THREE separate files: index.html, index.js, and style.css.

IMPORTANT: You MUST output ALL THREE files in the following format:

```html
<!-- index.html content here -->
```

```javascript
// index.js content here
```

```css
/* style.css content here */
```

Requirements:
1. Create a modern, responsive web application using transformers.js
2. Use the transformers.js library for AI/ML functionality
3. Create a clean, professional UI with good user experience
4. Make the application fully responsive for mobile devices
5. Use modern CSS practices and JavaScript ES6+ features
6. Include proper error handling and loading states
7. Follow accessibility best practices

The index.html should contain the basic HTML structure and link to the CSS and JS files.
The index.js should contain all the JavaScript logic including transformers.js integration.
The style.css should contain all the styling for the application.

Always output only the three code blocks as shown above, and do not include any explanations or extra text."""

SVELTE_SYSTEM_PROMPT = """You are an expert Svelte developer creating a modern Svelte application. You will generate ONLY the custom files that need user-specific content for the user's requested application.

IMPORTANT: You MUST output files in the following format. Generate ONLY the files needed for the user's specific request:

```svelte
<!-- src/App.svelte content here -->
```

```css
/* src/app.css content here */
```

If you need additional components for the user's specific app, add them like:
```svelte
<!-- src/lib/ComponentName.svelte content here -->
```

Requirements:
1. Create a modern, responsive Svelte application based on the user's specific request
2. Use TypeScript for better type safety
3. Create a clean, professional UI with good user experience
4. Make the application fully responsive for mobile devices
5. Use modern CSS practices and Svelte best practices
6. Include proper error handling and loading states
7. Follow accessibility best practices
8. Use Svelte's reactive features effectively
9. Include proper component structure and organization
10. Generate ONLY components that are actually needed for the user's requested application

Files you should generate:
- src/App.svelte: Main application component (ALWAYS required)
- src/app.css: Global styles (ALWAYS required)
- src/lib/[ComponentName].svelte: Additional components (ONLY if needed for the user's specific app)

The other files (index.html, package.json, vite.config.ts, tsconfig files, svelte.config.js, src/main.ts, src/vite-env.d.ts) are provided by the Svelte template and don't need to be generated.

Always output only the two code blocks as shown above, and do not include any explanations or extra text."""

SVELTE_SYSTEM_PROMPT_WITH_SEARCH = """You are an expert Svelte developer creating a modern Svelte application. You have access to real-time web search. When needed, use web search to find the latest information, best practices, or specific Svelte technologies.

You will generate ONLY the custom files that need user-specific content.

IMPORTANT: You MUST output ONLY the custom files in the following format:

```svelte
<!-- src/App.svelte content here -->
```

```css
/* src/app.css content here -->
```

Requirements:
1. Create a modern, responsive Svelte application
2. Use TypeScript for better type safety
3. Create a clean, professional UI with good user experience
4. Make the application fully responsive for mobile devices
5. Use modern CSS practices and Svelte best practices
6. Include proper error handling and loading states
7. Follow accessibility best practices
8. Use Svelte's reactive features effectively
9. Include proper component structure and organization
10. Use web search to find the latest Svelte patterns, libraries, and best practices

The files you generate are:
- src/App.svelte: Main application component (your custom app logic)
- src/app.css: Global styles (your custom styling)

The other files (index.html, package.json, vite.config.ts, tsconfig files, svelte.config.js, src/main.ts, src/vite-env.d.ts) are provided by the Svelte template and don't need to be generated.

Always output only the two code blocks as shown above, and do not include any explanations or extra text."""

TRANSFORMERS_JS_SYSTEM_PROMPT_WITH_SEARCH = """You are an expert web developer creating a transformers.js application. You have access to real-time web search. When needed, use web search to find the latest information, best practices, or specific technologies for transformers.js.

You will generate THREE separate files: index.html, index.js, and style.css.

IMPORTANT: You MUST output ALL THREE files in the following format:

```html
<!-- index.html content here -->
```

```javascript
// index.js content here
```

```css
/* style.css content here */
```

Requirements:
1. Create a modern, responsive web application using transformers.js
2. Use the transformers.js library for AI/ML functionality
3. Use web search to find current best practices and latest transformers.js features
4. Create a clean, professional UI with good user experience
5. Make the application fully responsive for mobile devices
6. Use modern CSS practices and JavaScript ES6+ features
7. Include proper error handling and loading states
8. Follow accessibility best practices

The index.html should contain the basic HTML structure and link to the CSS and JS files.
The index.js should contain all the JavaScript logic including transformers.js integration.
The style.css should contain all the styling for the application.

Always output only the three code blocks as shown above, and do not include any explanations or extra text."""

GENERIC_SYSTEM_PROMPT = """You are an expert {language} developer. Write clean, idiomatic, and runnable {language} code for the user's request. If possible, include comments and best practices. Output ONLY the code inside a ``` code block, and do not include any explanations or extra text. If the user provides a file or other context, use it as a reference. If the code is for a script or app, make it as self-contained as possible. Do NOT add the language name at the top of the code output."""

# System prompt with search capability
HTML_SYSTEM_PROMPT_WITH_SEARCH = """ONLY USE HTML, CSS AND JAVASCRIPT. If you want to use ICON make sure to import the library first. Try to create the best UI possible by using only HTML, CSS and JAVASCRIPT. MAKE IT RESPONSIVE USING MODERN CSS. Use as much as you can modern CSS for the styling, if you can't do something with modern CSS, then use custom CSS. Also, try to elaborate as much as you can, to create something unique. ALWAYS GIVE THE RESPONSE INTO A SINGLE HTML FILE

You have access to real-time web search. When needed, use web search to find the latest information, best practices, or specific technologies.

For website redesign tasks:
- Use the provided original HTML code as the starting point for redesign
- Preserve all original content, structure, and functionality
- Keep the same semantic HTML structure but enhance the styling
- Reuse all original images and their URLs from the HTML code
- Use web search to find current design trends and best practices for the specific type of website
- Create a modern, responsive design with improved typography and spacing
- Use modern CSS frameworks and design patterns
- Ensure accessibility and mobile responsiveness
- Maintain the same navigation and user flow
- Enhance the visual design while keeping the original layout structure

If an image is provided, analyze it and use the visual information to better understand the user's requirements.

Always respond with code that can be executed or rendered directly.

Always output only the HTML code inside a ```html ... ``` code block, and do not include any explanations or extra text. Do NOT add the language name at the top of the code output."""

GENERIC_SYSTEM_PROMPT_WITH_SEARCH = """You are an expert {language} developer. You have access to real-time web search. When needed, use web search to find the latest information, best practices, or specific technologies for {language}.

Write clean, idiomatic, and runnable {language} code for the user's request. If possible, include comments and best practices. Output ONLY the code inside a ``` code block, and do not include any explanations or extra text. If the user provides a file or other context, use it as a reference. If the code is for a script or app, make it as self-contained as possible. Do NOT add the language name at the top of the code output."""

# Follow-up system prompt for modifying existing HTML files
FollowUpSystemPrompt = f"""You are an expert web developer modifying an existing HTML file.
The user wants to apply changes based on their request.
You MUST output ONLY the changes required using the following SEARCH/REPLACE block format. Do NOT output the entire file.
Explain the changes briefly *before* the blocks if necessary, but the code changes THEMSELVES MUST be within the blocks.
Format Rules:
1. Start with {SEARCH_START}
2. Provide the exact lines from the current code that need to be replaced.
3. Use {DIVIDER} to separate the search block from the replacement.
4. Provide the new lines that should replace the original lines.
5. End with {REPLACE_END}
6. You can use multiple SEARCH/REPLACE blocks if changes are needed in different parts of the file.
7. To insert code, use an empty SEARCH block (only {SEARCH_START} and {DIVIDER} on their lines) if inserting at the very beginning, otherwise provide the line *before* the insertion point in the SEARCH block and include that line plus the new lines in the REPLACE block.
8. To delete code, provide the lines to delete in the SEARCH block and leave the REPLACE block empty (only {DIVIDER} and {REPLACE_END} on their lines).
9. IMPORTANT: The SEARCH block must *exactly* match the current code, including indentation and whitespace.
Example Modifying Code:
```
Some explanation...
{SEARCH_START}
    <h1>Old Title</h1>
{DIVIDER}
    <h1>New Title</h1>
{REPLACE_END}
{SEARCH_START}
  </body>
{DIVIDER}
    <script>console.log("Added script");</script>
  </body>
{REPLACE_END}
```
Example Deleting Code:
```
Removing the paragraph...
{SEARCH_START}
  <p>This paragraph will be deleted.</p>
{DIVIDER}
{REPLACE_END}
```"""

# Follow-up system prompt for modifying existing transformers.js applications
TransformersJSFollowUpSystemPrompt = f"""You are an expert web developer modifying an existing transformers.js application.
The user wants to apply changes based on their request.
You MUST output ONLY the changes required using the following SEARCH/REPLACE block format. Do NOT output the entire file.
Explain the changes briefly *before* the blocks if necessary, but the code changes THEMSELVES MUST be within the blocks.

The transformers.js application consists of three files: index.html, index.js, and style.css.
When making changes, specify which file you're modifying by starting your search/replace blocks with the file name.

Format Rules:
1. Start with {SEARCH_START}
2. Provide the exact lines from the current code that need to be replaced.
3. Use {DIVIDER} to separate the search block from the replacement.
4. Provide the new lines that should replace the original lines.
5. End with {REPLACE_END}
6. You can use multiple SEARCH/REPLACE blocks if changes are needed in different parts of the file.
7. To insert code, use an empty SEARCH block (only {SEARCH_START} and {DIVIDER} on their lines) if inserting at the very beginning, otherwise provide the line *before* the insertion point in the SEARCH block and include that line plus the new lines in the REPLACE block.
8. To delete code, provide the lines to delete in the SEARCH block and leave the REPLACE block empty (only {DIVIDER} and {REPLACE_END} on their lines).
9. IMPORTANT: The SEARCH block must *exactly* match the current code, including indentation and whitespace.

Example Modifying HTML:
```
Changing the title in index.html...
{SEARCH_START}
    <title>Old Title</title>
{DIVIDER}
    <title>New Title</title>
{REPLACE_END}
```

Example Modifying JavaScript:
```
Adding a new function to index.js...
{SEARCH_START}
// Existing code
{DIVIDER}
// Existing code

function newFunction() {{
    console.log("New function added");
}}
{REPLACE_END}
```

Example Modifying CSS:
```
Changing background color in style.css...
{SEARCH_START}
body {{
    background-color: white;
}}
{DIVIDER}
body {{
    background-color: #f0f0f0;
}}
{REPLACE_END}
```"""

# Available Ollama models - Update this list with your downloaded models
AVAILABLE_MODELS = [
    {
        "name": "CodeLlama 7B",
        "id": "codellama:7b",
        "description": "Code Llama 7B model for code generation",
        "supports_vision": False
    },
    {
        "name": "CodeLlama 13B",
        "id": "codellama:13b",
        "description": "Code Llama 13B model for advanced code generation",
        "supports_vision": False
    },
    {
        "name": "DeepSeek Coder 6.7B",
        "id": "deepseek-coder:6.7b",
        "description": "DeepSeek Coder 6.7B model specialized for code generation",
        "supports_vision": False
    },
    {
        "name": "Llama 3.1 8B",
        "id": "llama3.1:8b",
        "description": "Llama 3.1 8B model for general tasks and code generation",
        "supports_vision": False
    },
    {
        "name": "Llava 7B",
        "id": "llava:7b",
        "description": "Llava 7B multimodal model with vision support",
        "supports_vision": True
    },
    {
        "name": "Llava 13B",
        "id": "llava:13b",
        "description": "Llava 13B multimodal model with advanced vision support",
        "supports_vision": True
    },
    {
        "name": "Mistral 7B",
        "id": "mistral:7b",
        "description": "Mistral 7B model for general tasks",
        "supports_vision": False
    },
    {
        "name": "Qwen2 7B",
        "id": "qwen2:7b",
        "description": "Qwen2 7B model for general tasks and code generation",
        "supports_vision": False
    },
    {
        "name": "CodeGemma 7B",
        "id": "codegemma:7b",
        "description": "CodeGemma 7B model for code generation",
        "supports_vision": False
    }
]

DEMO_LIST = [
    {
        "title": "Todo App",
        "description": "Create a simple todo application with add, delete, and mark as complete functionality"
    },
    {
        "title": "Calculator",
        "description": "Build a basic calculator with addition, subtraction, multiplication, and division"
    },
    {
        "title": "Chat Interface",
        "description": "Build a chat interface with message history and user input"
    },
    {
        "title": "E-commerce Product Card",
        "description": "Create a product card component for an e-commerce website"
    },
    {
        "title": "Login Form",
        "description": "Build a responsive login form with validation"
    },
    {
        "title": "Dashboard Layout",
        "description": "Create a dashboard layout with sidebar navigation and main content area"
    },
    {
        "title": "Data Table",
        "description": "Build a data table with sorting and filtering capabilities"
    },
    {
        "title": "Image Gallery",
        "description": "Create an image gallery with lightbox functionality and responsive grid layout"
    },
    {
        "title": "UI from Image",
        "description": "Upload an image of a UI design and I'll generate the HTML/CSS code for it"
    },
    {
        "title": "Extract Text from Image",
        "description": "Upload an image containing text and I'll extract and process the text content"
    },
    {
        "title": "Website Redesign",
        "description": "Enter a website URL to extract its content and redesign it with a modern, responsive layout"
    },
    {
        "title": "Modify HTML",
        "description": "After generating HTML, ask me to modify it with specific changes using search/replace format"
    },
    {
        "title": "Search/Replace Example",
        "description": "Generate HTML first, then ask: 'Change the title to My New Title' or 'Add a blue background to the body'"
    },
    {
        "title": "Transformers.js App",
        "description": "Create a transformers.js application with AI/ML functionality using the transformers.js library"
    },
    {
        "title": "Svelte App",
        "description": "Create a modern Svelte application with TypeScript, Vite, and responsive design"
    }
]

# Ollama Configuration
OLLAMA_BASE_URL = os.getenv('OLLAMA_BASE_URL', 'http://localhost:11434')

def get_ollama_client():
    """Return Ollama client"""
    try:
        # Test if Ollama is running
        response = requests.get(f"{OLLAMA_BASE_URL}/api/tags", timeout=5)
        if response.status_code == 200:
            return ollama.Client(host=OLLAMA_BASE_URL)
        else:
            return None
    except Exception as e:
        print(f"Ollama connection error: {e}")
        return None

def get_available_ollama_models():
    """Get list of available Ollama models"""
    try:
        client = get_ollama_client()
        if client:
            models = client.list()
            return [model['name'] for model in models['models']]
        return []
    except Exception as e:
        print(f"Error getting Ollama models: {e}")
        return []

# Update available models with actual Ollama models
def update_available_models():
    """Update the available models list with actually installed Ollama models"""
    try:
        ollama_models = get_available_ollama_models()
        if ollama_models:
            # Filter AVAILABLE_MODELS to only include models that are actually installed
            global AVAILABLE_MODELS
            AVAILABLE_MODELS = [model for model in AVAILABLE_MODELS if model["id"] in ollama_models]
            
            # If no predefined models are available, create entries for all installed models
            if not AVAILABLE_MODELS:
                AVAILABLE_MODELS = []
                for model_name in ollama_models:
                    supports_vision = 'llava' in model_name.lower() or 'vision' in model_name.lower()
                    AVAILABLE_MODELS.append({
                        "name": model_name.replace(":", " ").title(),
                        "id": model_name,
                        "description": f"{model_name} model",
                        "supports_vision": supports_vision
                    })
    except Exception as e:
        print(f"Error updating available models: {e}")

# Update models on startup
update_available_models()

# Type definitions
History = List[Tuple[str, str]]
Messages = List[Dict[str, str]]

# Tavily Search Client
TAVILY_API_KEY = os.getenv('TAVILY_API_KEY')
tavily_client = None
if TAVILY_API_KEY:
    try:
        tavily_client = TavilyClient(api_key=TAVILY_API_KEY)
    except Exception as e:
        print(f"Failed to initialize Tavily client: {e}")
        tavily_client = None

def history_to_messages(history: History, system: str) -> Messages:
    messages = [{'role': 'system', 'content': system}]
    for h in history:
        # Handle multimodal content in history
        user_content = h[0]
        if isinstance(user_content, list):
            # Extract text from multimodal content
            text_content = ""
            for item in user_content:
                if isinstance(item, dict) and item.get("type") == "text":
                    text_content += item.get("text", "")
            user_content = text_content if text_content else str(user_content)
        
        messages.append({'role': 'user', 'content': user_content})
        messages.append({'role': 'assistant', 'content': h[1]})
    return messages

def messages_to_history(messages: Messages) -> Tuple[str, History]:
    assert messages[0]['role'] == 'system'
    history = []
    for q, r in zip(messages[1::2], messages[2::2]):
        # Extract text content from multimodal messages for history
        user_content = q['content']
        if isinstance(user_content, list):
            text_content = ""
            for item in user_content:
                if isinstance(item, dict) and item.get("type") == "text":
                    text_content += item.get("text", "")
            user_content = text_content if text_content else str(user_content)
        
        history.append([user_content, r['content']])
    return history

def history_to_chatbot_messages(history: History) -> List[Dict[str, str]]:
    """Convert history tuples to chatbot message format"""
    messages = []
    for user_msg, assistant_msg in history:
        # Handle multimodal content
        if isinstance(user_msg, list):
            text_content = ""
            for item in user_msg:
                if isinstance(item, dict) and item.get("type") == "text":
                    text_content += item.get("text", "")
            user_msg = text_content if text_content else str(user_msg)
        
        messages.append({"role": "user", "content": user_msg})
        messages.append({"role": "assistant", "content": assistant_msg})
    return messages

def remove_code_block(text):
    # Try to match code blocks with language markers
    patterns = [
        r'```(?:html|HTML)\n([\s\S]+?)\n```',  # Match ```html or ```HTML
        r'```\n([\s\S]+?)\n```',               # Match code blocks without language markers
        r'```([\s\S]+?)```'                      # Match code blocks without line breaks
    ]
    for pattern in patterns:
        match = re.search(pattern, text, re.DOTALL)
        if match:
            extracted = match.group(1).strip()
            # Remove a leading language marker line (e.g., 'python') if present
            if extracted.split('\n', 1)[0].strip().lower() in ['python', 'html', 'css', 'javascript', 'json', 'c', 'cpp', 'markdown', 'latex', 'jinja2', 'typescript', 'yaml', 'dockerfile', 'shell', 'r', 'sql', 'sql-mssql', 'sql-mysql', 'sql-mariadb', 'sql-sqlite', 'sql-cassandra', 'sql-plSQL', 'sql-hive', 'sql-pgsql', 'sql-gql', 'sql-gpsql', 'sql-sparksql', 'sql-esper']:
                return extracted.split('\n', 1)[1] if '\n' in extracted else ''
            return extracted
    # If no code block is found, check if the entire text is HTML
    if text.strip().startswith('<!DOCTYPE html>') or text.strip().startswith('<html') or text.strip().startswith('<'):
        return text.strip()
    # Special handling for python: remove python marker
    if text.strip().startswith('```python'):
        return text.strip()[9:-3].strip()
    # Remove a leading language marker line if present (fallback)
    lines = text.strip().split('\n', 1)
    if lines[0].strip().lower() in ['python', 'html', 'css', 'javascript', 'json', 'c', 'cpp', 'markdown', 'latex', 'jinja2', 'typescript', 'yaml', 'dockerfile', 'shell', 'r', 'sql', 'sql-mssql', 'sql-mysql', 'sql-mariadb', 'sql-sqlite', 'sql-cassandra', 'sql-plSQL', 'sql-hive', 'sql-pgsql', 'sql-gql', 'sql-gpsql', 'sql-sparksql', 'sql-esper']:
        return lines[1] if len(lines) > 1 else ''
    return text.strip()

def parse_transformers_js_output(text):
    """Parse transformers.js output and extract the three files (index.html, index.js, style.css)"""
    files = {
        'index.html': '',
        'index.js': '',
        'style.css': ''
    }
    
    # Patterns to match the three code blocks
    html_pattern = r'```html\s*\n([\s\S]+?)\n```'
    js_pattern = r'```javascript\s*\n([\s\S]+?)\n```'
    css_pattern = r'```css\s*\n([\s\S]+?)\n```'
    
    # Extract HTML content
    html_match = re.search(html_pattern, text, re.IGNORECASE)
    if html_match:
        files['index.html'] = html_match.group(1).strip()
    
    # Extract JavaScript content
    js_match = re.search(js_pattern, text, re.IGNORECASE)
    if js_match:
        files['index.js'] = js_match.group(1).strip()
    
    # Extract CSS content
    css_match = re.search(css_pattern, text, re.IGNORECASE)
    if css_match:
        files['style.css'] = css_match.group(1).strip()
    
    # Fallback: support === index.html === format if any file is missing
    if not (files['index.html'] and files['index.js'] and files['style.css']):
        # Use regex to extract sections
        html_fallback = re.search(r'===\s*index\.html\s*===\n([\s\S]+?)(?=\n===|$)', text, re.IGNORECASE)
        js_fallback = re.search(r'===\s*index\.js\s*===\n([\s\S]+?)(?=\n===|$)', text, re.IGNORECASE)
        css_fallback = re.search(r'===\s*style\.css\s*===\n([\s\S]+?)(?=\n===|$)', text, re.IGNORECASE)
        if html_fallback:
            files['index.html'] = html_fallback.group(1).strip()
        if js_fallback:
            files['index.js'] = js_fallback.group(1).strip()
        if css_fallback:
            files['style.css'] = css_fallback.group(1).strip()
    
    return files

def format_transformers_js_output(files):
    """Format the three files into a single display string"""
    output = []
    output.append("=== index.html ===")
    output.append(files['index.html'])
    output.append("\n=== index.js ===")
    output.append(files['index.js'])
    output.append("\n=== style.css ===")
    output.append(files['style.css'])
    return '\n'.join(output)

def parse_svelte_output(text):
    """Parse Svelte output to extract individual files"""
    files = {
        'src/App.svelte': '',
        'src/app.css': ''
    }
    
    import re
    
    # First try to extract using code block patterns
    svelte_pattern = r'```svelte\s*\n([\s\S]+?)\n```'
    css_pattern = r'```css\s*\n([\s\S]+?)\n```'
    
    # Extract svelte block for App.svelte
    svelte_match = re.search(svelte_pattern, text, re.IGNORECASE)
    css_match = re.search(css_pattern, text, re.IGNORECASE)
    
    if svelte_match:
        files['src/App.svelte'] = svelte_match.group(1).strip()
    if css_match:
        files['src/app.css'] = css_match.group(1).strip()
    
    # Fallback: support === filename === format if any file is missing
    if not (files['src/App.svelte'] and files['src/app.css']):
        # Use regex to extract sections
        app_svelte_fallback = re.search(r'===\s*src/App\.svelte\s*===\n([\s\S]+?)(?=\n===|$)', text, re.IGNORECASE)
        app_css_fallback = re.search(r'===\s*src/app\.css\s*===\n([\s\S]+?)(?=\
