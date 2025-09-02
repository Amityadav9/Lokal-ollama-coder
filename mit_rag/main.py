import os
import re
from typing import Dict, List, Tuple, Optional
import requests
import subprocess
import ollama
from tavily import TavilyClient
import gradio as gr
from src.rag import (
    process_and_initialize,
    user_query_typing_effect,
    test_ollama_connection,
)

try:
    from PIL import Image as PILImage
    import pytesseract

    OCR_AVAILABLE = True
except Exception:
    PILImage = None
    pytesseract = None
    OCR_AVAILABLE = False

# Gradio supported languages for syntax highlighting
GRADIO_SUPPORTED_LANGUAGES = [
    "python",
    "c",
    "cpp",
    "markdown",
    "latex",
    "json",
    "html",
    "css",
    "javascript",
    "jinja2",
    "typescript",
    "yaml",
    "dockerfile",
    "shell",
    "r",
    "sql",
    "sql-msSQL",
    "sql-mySQL",
    "sql-mariaDB",
    "sql-sqlite",
    "sql-cassandra",
    "sql-plSQL",
    "sql-hive",
    "sql-pgSQL",
    "sql-gql",
    "sql-gpSQL",
    "sql-sparkSQL",
    "sql-esper",
    None,
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
        "supports_vision": False,
    },
    {
        "name": "CodeLlama 13B",
        "id": "codellama:13b",
        "description": "Code Llama 13B model for advanced code generation",
        "supports_vision": False,
    },
    {
        "name": "DeepSeek Coder 6.7B",
        "id": "deepseek-coder:6.7b",
        "description": "DeepSeek Coder 6.7B model specialized for code generation",
        "supports_vision": False,
    },
    {
        "name": "Llama 3.1 8B",
        "id": "llama3.1:8b",
        "description": "Llama 3.1 8B model for general tasks and code generation",
        "supports_vision": False,
    },
    {
        "name": "Llava 7B",
        "id": "llava:7b",
        "description": "Llava 7B multimodal model with vision support",
        "supports_vision": True,
    },
    {
        "name": "Llava 13B",
        "id": "llava:13b",
        "description": "Llava 13B multimodal model with advanced vision support",
        "supports_vision": True,
    },
    {
        "name": "Mistral 7B",
        "id": "mistral:7b",
        "description": "Mistral 7B model for general tasks",
        "supports_vision": False,
    },
    {
        "name": "Qwen2 7B",
        "id": "qwen2:7b",
        "description": "Qwen2 7B model for general tasks and code generation",
        "supports_vision": False,
    },
    {
        "name": "CodeGemma 7B",
        "id": "codegemma:7b",
        "description": "CodeGemma 7B model for code generation",
        "supports_vision": False,
    },
]

# Will be set to a sensible default model id at startup
# Allow explicit override via environment variable OLLAMA_DEFAULT_MODEL
DEFAULT_MODEL_ID: Optional[str] = os.getenv("OLLAMA_DEFAULT_MODEL")

DEMO_LIST = [
    {
        "title": "Todo App",
        "description": "Create a simple todo application with add, delete, and mark as complete functionality",
    },
    {
        "title": "Calculator",
        "description": "Build a basic calculator with addition, subtraction, multiplication, and division",
    },
    {
        "title": "Chat Interface",
        "description": "Build a chat interface with message history and user input",
    },
    {
        "title": "E-commerce Product Card",
        "description": "Create a product card component for an e-commerce website",
    },
    {
        "title": "Login Form",
        "description": "Build a responsive login form with validation",
    },
    {
        "title": "Dashboard Layout",
        "description": "Create a dashboard layout with sidebar navigation and main content area",
    },
    {
        "title": "Data Table",
        "description": "Build a data table with sorting and filtering capabilities",
    },
    {
        "title": "Image Gallery",
        "description": "Create an image gallery with lightbox functionality and responsive grid layout",
    },
    {
        "title": "UI from Image",
        "description": "Upload an image of a UI design and I'll generate the HTML/CSS code for it",
    },
    {
        "title": "Extract Text from Image",
        "description": "Upload an image containing text and I'll extract and process the text content",
    },
    {
        "title": "Website Redesign",
        "description": "Enter a website URL to extract its content and redesign it with a modern, responsive layout",
    },
    {
        "title": "Modify HTML",
        "description": "After generating HTML, ask me to modify it with specific changes using search/replace format",
    },
    {
        "title": "Search/Replace Example",
        "description": "Generate HTML first, then ask: 'Change the title to My New Title' or 'Add a blue background to the body'",
    },
    {
        "title": "Transformers.js App",
        "description": "Create a transformers.js application with AI/ML functionality using the transformers.js library",
    },
    {
        "title": "Svelte App",
        "description": "Create a modern Svelte application with TypeScript, Vite, and responsive design",
    },
]

# Ollama Configuration
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")


def get_ollama_client():
    """Return an Ollama client if the Ollama HTTP API is reachable, else None."""
    try:
        # Test if Ollama HTTP API is reachable
        response = requests.get(f"{OLLAMA_BASE_URL}/api/tags", timeout=5)
        if response.status_code == 200:
            return ollama.Client(host=OLLAMA_BASE_URL)
        return None
    except Exception as e:
        print(f"Ollama connection error: {e}")
        return None


def get_available_ollama_models():
    """Get list of available Ollama models using the Python client or fallback to the `ollama` CLI."""
    models_list = []
    try:
        client = get_ollama_client()
        if client:
            models_resp = client.list()
            # support dict with 'models' key, list, or iterable
            if isinstance(models_resp, dict) and "models" in models_resp:
                models = models_resp["models"]
            elif isinstance(models_resp, list):
                models = models_resp
            else:
                try:
                    models = list(models_resp)
                except Exception:
                    models = []

            for m in models:
                if isinstance(m, str):
                    models_list.append(m)
                elif isinstance(m, dict):
                    for key in ("name", "id", "tag"):
                        if key in m:
                            models_list.append(m[key])
                            break
            if models_list:
                return models_list
    except Exception as e:
        print(f"Error getting Ollama models via client: {e}")

    # Fallback to CLI
    try:
        res = subprocess.run(
            ["ollama", "list"], capture_output=True, text=True, timeout=5
        )
        if res.returncode == 0 and res.stdout:
            lines = [line.strip() for line in res.stdout.splitlines() if line.strip()]
            for line in lines:
                parts = line.split()
                if parts:
                    models_list.append(parts[0])
            if models_list:
                return models_list
    except Exception:
        pass

    return models_list


def get_default_model_id(installed_models: List[str]) -> Optional[str]:
    """Choose a sensible default model id from installed models."""
    # Prefer gemma3:12b, then gemma2, then llama3.2, qwen2.5, llama3.1, mistral
    priority = [
        "gemma3:12b",
        "gemma2:9b",
        "gemma2:latest",
        "llama3.2:3b",
        "qwen2.5:7b",
        "llama3.1:latest",
        "mistral:latest",
        "mistral:7b",
    ]
    for p in priority:
        if p in installed_models:
            return p
    # Fallback: return first installed model
    return installed_models[0] if installed_models else None


# Update available models with actual Ollama models
def update_available_models():
    """Update the available models list with actually installed Ollama models"""
    global DEFAULT_MODEL_ID, AVAILABLE_MODELS
    try:
        ollama_models = get_available_ollama_models()
        if not ollama_models:
            print("No Ollama models detected via Python client or `ollama list` CLI.")
            return

        print(f"🔍 Detected Ollama models: {ollama_models}")

        # Keep only models that are actually installed
        AVAILABLE_MODELS = [m for m in AVAILABLE_MODELS if m.get("id") in ollama_models]

        # If no predefined models matched, create entries for installed models
        if not AVAILABLE_MODELS:
            AVAILABLE_MODELS = []
            for model_name in ollama_models:
                supports_vision = (
                    "llava" in model_name.lower() or "vision" in model_name.lower()
                )
                AVAILABLE_MODELS.append(
                    {
                        "name": model_name.replace(":", " ").title(),
                        "id": model_name,
                        "description": f"{model_name} model",
                        "supports_vision": supports_vision,
                    }
                )

        # Also add any installed models not in the predefined list
        installed_ids = [m.get("id") for m in AVAILABLE_MODELS]
        for model_name in ollama_models:
            if model_name not in installed_ids:
                supports_vision = (
                    "llava" in model_name.lower() or "vision" in model_name.lower()
                )
                AVAILABLE_MODELS.append(
                    {
                        "name": model_name.replace(":", " ").title(),
                        "id": model_name,
                        "description": f"{model_name} model",
                        "supports_vision": supports_vision,
                    }
                )

        print(
            f"📋 Available models for dropdown: {[m['id'] for m in AVAILABLE_MODELS]}"
        )

        # Validate env override if provided
        if DEFAULT_MODEL_ID:
            if DEFAULT_MODEL_ID not in ollama_models:
                print(
                    f"Warning: OLLAMA_DEFAULT_MODEL={DEFAULT_MODEL_ID} not found in installed models"
                )
                DEFAULT_MODEL_ID = None

        # Choose default if none set
        if not DEFAULT_MODEL_ID:
            DEFAULT_MODEL_ID = get_default_model_id(ollama_models)

        if DEFAULT_MODEL_ID:
            print(f"Default Ollama model set to: {DEFAULT_MODEL_ID}")
    except Exception as e:
        print(f"Error updating available models: {e}")


# Update models on startup
update_available_models()

# Type definitions
History = List[Tuple[str, str]]
Messages = List[Dict[str, str]]

# Tavily Search Client
TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")
tavily_client = None
if TAVILY_API_KEY:
    try:
        tavily_client = TavilyClient(api_key=TAVILY_API_KEY)
    except Exception as e:
        print(f"Failed to initialize Tavily client: {e}")
        tavily_client = None


def history_to_messages(history: History, system: str) -> Messages:
    messages = [{"role": "system", "content": system}]
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

        messages.append({"role": "user", "content": user_content})
        messages.append({"role": "assistant", "content": h[1]})
    return messages


def messages_to_history(messages: Messages) -> Tuple[str, History]:
    assert messages[0]["role"] == "system"
    history = []
    for q, r in zip(messages[1::2], messages[2::2]):
        # Extract text content from multimodal messages for history
        user_content = q["content"]
        if isinstance(user_content, list):
            text_content = ""
            for item in user_content:
                if isinstance(item, dict) and item.get("type") == "text":
                    text_content += item.get("text", "")
            user_content = text_content if text_content else str(user_content)

        history.append([user_content, r["content"]])
    return history


def history_to_chatbot_messages(history: History) -> List[Dict[str, str]]:
    """Convert history tuples to chatbot message format"""
    messages = []
    print(f"🔍 DEBUG: Converting history to messages. History type: {type(history)}, Length: {len(history) if hasattr(history, '__len__') else 'unknown'}")
    
    for i, item in enumerate(history):
        print(f"🔍 DEBUG: History item {i}: {type(item)} = {item}")
        
        # Handle different history formats
        if isinstance(item, (list, tuple)) and len(item) >= 2:
            user_msg, assistant_msg = item[0], item[1]
        elif isinstance(item, dict) and 'role' in item and 'content' in item:
            # Already in correct format, just append
            messages.append(item)
            continue
        else:
            print(f"⚠️ WARNING: Skipping unknown history item format: {item}")
            continue
            
        # Normalize user message to a plain string
        if isinstance(user_msg, list):
            text_content = ""
            for subitem in user_msg:
                if isinstance(subitem, dict) and subitem.get("type") == "text":
                    text_content += subitem.get("text", "")
            user_text = text_content if text_content else str(user_msg)
        else:
            user_text = str(user_msg) if user_msg is not None else ""

        # Normalize assistant message to a plain string
        if isinstance(assistant_msg, list):
            text_content = ""
            for subitem in assistant_msg:
                if isinstance(subitem, dict) and subitem.get("type") == "text":
                    text_content += subitem.get("text", "")
            assistant_text = text_content if text_content else str(assistant_msg)
        else:
            assistant_text = str(assistant_msg) if assistant_msg is not None else ""

        # Append as message dicts (Gradio messages format)
        messages.append({"role": "user", "content": user_text})
        messages.append({"role": "assistant", "content": assistant_text})

    print(f"🔍 DEBUG: Final messages: {messages}")
    return messages


def remove_code_block(text):
    # Try to match code blocks with language markers
    patterns = [
        r"```(?:html|HTML)\n([\s\S]+?)\n```",  # Match ```html or ```HTML
        r"```\n([\s\S]+?)\n```",  # Match code blocks without language markers
        r"```([\s\S]+?)```",  # Match code blocks without line breaks
    ]
    for pattern in patterns:
        match = re.search(pattern, text, re.DOTALL)
        if match:
            extracted = match.group(1).strip()
            # Remove a leading language marker line (e.g., 'python') if present
            if extracted.split("\n", 1)[0].strip().lower() in [
                "python",
                "html",
                "css",
                "javascript",
                "json",
                "c",
                "cpp",
                "markdown",
                "latex",
                "jinja2",
                "typescript",
                "yaml",
                "dockerfile",
                "shell",
                "r",
                "sql",
                "sql-mssql",
                "sql-mysql",
                "sql-mariadb",
                "sql-sqlite",
                "sql-cassandra",
                "sql-plSQL",
                "sql-hive",
                "sql-pgsql",
                "sql-gql",
                "sql-gpsql",
                "sql-sparksql",
                "sql-esper",
            ]:
                return extracted.split("\n", 1)[1] if "\n" in extracted else ""
            return extracted
    # If no code block is found, check if the entire text is HTML
    if (
        text.strip().startswith("<!DOCTYPE html>")
        or text.strip().startswith("<html")
        or text.strip().startswith("<")
    ):
        return text.strip()
    # Special handling for python: remove python marker
    if text.strip().startswith("```python"):
        return text.strip()[9:-3].strip()
    # Remove a leading language marker line if present (fallback)
    lines = text.strip().split("\n", 1)
    if lines[0].strip().lower() in [
        "python",
        "html",
        "css",
        "javascript",
        "json",
        "c",
        "cpp",
        "markdown",
        "latex",
        "jinja2",
        "typescript",
        "yaml",
        "dockerfile",
        "shell",
        "r",
        "sql",
        "sql-mssql",
        "sql-mysql",
        "sql-mariadb",
        "sql-sqlite",
        "sql-cassandra",
        "sql-plSQL",
        "sql-hive",
        "sql-pgsql",
        "sql-gql",
        "sql-gpsql",
        "sql-sparksql",
        "sql-esper",
    ]:
        return lines[1] if len(lines) > 1 else ""
    return text.strip()


def parse_transformers_js_output(text):
    """Parse transformers.js output and extract the three files (index.html, index.js, style.css)"""
    files = {"index.html": "", "index.js": "", "style.css": ""}

    # Patterns to match the three code blocks
    html_pattern = r"```html\s*\n([\s\S]+?)\n```"
    js_pattern = r"```javascript\s*\n([\s\S]+?)\n```"
    css_pattern = r"```css\s*\n([\s\S]+?)\n```"

    # Extract HTML content
    html_match = re.search(html_pattern, text, re.IGNORECASE)
    if html_match:
        files["index.html"] = html_match.group(1).strip()

    # Extract JavaScript content
    js_match = re.search(js_pattern, text, re.IGNORECASE)
    if js_match:
        files["index.js"] = js_match.group(1).strip()

    # Extract CSS content
    css_match = re.search(css_pattern, text, re.IGNORECASE)
    if css_match:
        files["style.css"] = css_match.group(1).strip()

    # Fallback: support === index.html === format if any file is missing
    if not (files["index.html"] and files["index.js"] and files["style.css"]):
        # Use regex to extract sections
        html_fallback = re.search(
            r"===\s*index\.html\s*===\n([\s\S]+?)(?=\n===|$)", text, re.IGNORECASE
        )
        js_fallback = re.search(
            r"===\s*index\.js\s*===\n([\s\S]+?)(?=\n===|$)", text, re.IGNORECASE
        )
        css_fallback = re.search(
            r"===\s*style\.css\s*===\n([\s\S]+?)(?=\n===|$)", text, re.IGNORECASE
        )
        if html_fallback:
            files["index.html"] = html_fallback.group(1).strip()
        if js_fallback:
            files["index.js"] = js_fallback.group(1).strip()
        if css_fallback:
            files["style.css"] = css_fallback.group(1).strip()

    return files


def format_transformers_js_output(files):
    """Format the three files into a single display string"""
    output = []
    output.append("=== index.html ===")
    output.append(files["index.html"])
    output.append("\n=== index.js ===")
    output.append(files["index.js"])
    output.append("\n=== style.css ===")
    output.append(files["style.css"])
    return "\n".join(output)


def parse_svelte_output(text):
    """Parse Svelte output to extract individual files"""
    files = {"src/App.svelte": "", "src/app.css": ""}

    import re

    # First try to extract using code block patterns
    svelte_pattern = r"```svelte\s*\n([\s\S]+?)\n```"
    css_pattern = r"```css\s*\n([\s\S]+?)\n```"

    # Extract svelte block for App.svelte
    svelte_match = re.search(svelte_pattern, text, re.IGNORECASE)
    css_match = re.search(css_pattern, text, re.IGNORECASE)

    if svelte_match:
        files["src/App.svelte"] = svelte_match.group(1).strip()
    if css_match:
        files["src/app.css"] = css_match.group(1).strip()

    # Fallback: support === filename === format if any file is missing
    if not (files["src/App.svelte"] and files["src/app.css"]):
        # Use regex to extract sections
        app_svelte_fallback = re.search(
            r"===\s*src/App\.svelte\s*===\n([\s\S]+?)(?=\n===|$)", text, re.IGNORECASE
        )
        if app_svelte_fallback:
            files["src/App.svelte"] = app_svelte_fallback.group(1).strip()
        app_css_fallback = re.search(
            r"===\s*src/app\.css\s*===\n([\s\S]+?)(?=\n===|$)", text, re.IGNORECASE
        )
        if app_css_fallback:
            files["src/app.css"] = app_css_fallback.group(1).strip()

    return files


def format_svelte_output(files: Dict[str, str]) -> str:
    """Format Svelte files into a display string"""
    output = []
    output.append("=== src/App.svelte ===")
    output.append(files.get("src/App.svelte", ""))
    output.append("\n=== src/app.css ===")
    output.append(files.get("src/app.css", ""))
    return "\n".join(output)


def perform_web_search(query: str) -> Optional[str]:
    """Perform web search using Tavily (if available) and return formatted results."""
    if not tavily_client:
        return None
    try:
        results = tavily_client.search(query, max_results=5)
        formatted_results = []
        for r in results.get("results", []):
            formatted_results.append(
                f"Title: {r.get('title', 'N/A')}\nURL: {r.get('url', 'N/A')}\nContent: {r.get('content', 'N/A')}\n"
            )
        return "\n".join(formatted_results)
    except Exception as e:
        print(f"Search error: {e}")
        return None


def chat_with_model(
    message: str,
    history: History,
    model_id: str,
    temperature: float,
    system_prompt: str,
    enable_search: bool,
):
    """Main chat function with Ollama"""
    client = get_ollama_client()
    if not client:
        return "Error: Ollama is not running. Please start Ollama first.", history

    # Add search results to message if enabled
    if enable_search and tavily_client:
        search_results = perform_web_search(message)
        if search_results:
            message = f"{message}\n\nWeb Search Results:\n{search_results}"

    # Build messages
    messages = history_to_messages(history, system_prompt)
    messages.append({"role": "user", "content": message})

    try:
        # Non-streaming chat for simplicity
        response = client.chat(
            model=model_id,
            messages=messages,
            options={"temperature": temperature},
            stream=False,
        )

        # Response shape may vary depending on client version
        assistant_message = None
        if isinstance(response, dict):
            # Try common keys
            assistant_message = (
                (response.get("message") or {}).get("content")
                or response.get("output")
                or response.get("text")
            )
        elif isinstance(response, str):
            assistant_message = response

        assistant_message = assistant_message or ""

        history.append([message, assistant_message])
        return assistant_message, history

    except Exception as e:
        error_msg = f"Error: {str(e)}"
        history.append([message, error_msg])
        return error_msg, history


def process_code_output(code_output: str, output_type: str) -> str:
    """Process code output based on type"""
    print(f"🔍 DEBUG: Processing code output. Type: {output_type}")
    print(f"🔍 DEBUG: Raw output (first 200 chars): {code_output[:200]}...")
    
    if output_type == "HTML":
        result = remove_code_block(code_output)
    elif output_type == "Transformers.js":
        files = parse_transformers_js_output(code_output)
        result = format_transformers_js_output(files)
    elif output_type == "Svelte":
        files = parse_svelte_output(code_output)
        result = format_svelte_output(files)
    else:
        result = remove_code_block(code_output)
    
    print(f"🔍 DEBUG: Processed result (first 200 chars): {result[:200]}...")
    return result


# Gradio Interface


def create_interface():
    with gr.Blocks(title="Local Code Assistant", theme=gr.themes.Soft()) as demo:
        gr.Markdown("# 🚀 Local Code Assistant with Ollama")
        gr.Markdown(
            "Generate code using local LLMs. Supports HTML, Transformers.js, Svelte, and more!"
        )

        with gr.Row():
            with gr.Column(scale=1):
                # Model selection (safe default: only use DEFAULT_MODEL_ID if present in choices)
                model_choices = [m["id"] for m in AVAILABLE_MODELS]
                default_model = (
                    DEFAULT_MODEL_ID
                    if DEFAULT_MODEL_ID in model_choices
                    else (model_choices[0] if model_choices else None)
                )
                model_dropdown = gr.Dropdown(
                    choices=model_choices,
                    value=default_model,
                    label="Select Model",
                    interactive=True,
                )

                temperature = gr.Slider(
                    minimum=0,
                    maximum=2,
                    value=0.7,
                    step=0.1,
                    label="Temperature",
                )

                output_type = gr.Radio(
                    choices=[
                        "HTML",
                        "Transformers.js",
                        "Svelte",
                        "Python",
                        "JavaScript",
                        "Other",
                    ],
                    value="HTML",
                    label="Output Type",
                )

                # Only enable the web-search checkbox when Tavily is configured
                enable_search = gr.Checkbox(
                    label="Enable Web Search",
                    value=False if not tavily_client else True,
                    interactive=False if not tavily_client else True,
                    visible=bool(tavily_client),
                )

                # Demo examples
                gr.Markdown("### Quick Examples")
                example_buttons = []
                for example in DEMO_LIST[:5]:
                    btn = gr.Button(example["title"], size="sm")
                    example_buttons.append((btn, example["description"]))

                # RAG panel
                gr.Markdown("### RAG: Ask your documents")
                rag_files = gr.Files(
                    label="Upload Documents (PDF/TXT)",
                    file_types=[".pdf", ".txt"],
                    type="filepath",
                )
                rag_process_btn = gr.Button("Process Documents")
                rag_status = gr.Textbox(label="RAG Status", interactive=False)
                rag_query = gr.Textbox(
                    label="Ask documents",
                    placeholder="Ask a question about the uploaded docs...",
                    lines=2,
                )
                rag_ask_btn = gr.Button("Ask")

                # Image upload for vision flows
                gr.Markdown("### Image (UI / OCR)")
                image_input = gr.Image(
                    type="pil", label="Upload UI screenshot or mockup"
                )
                extract_text_btn = gr.Button("Extract Text from Image")
                gen_from_image_btn = gr.Button("Generate from Image")

            with gr.Column(scale=3):
                chatbot = gr.Chatbot(type="messages", height=400, elem_id="chatbot")

                with gr.Row():
                    msg = gr.Textbox(
                        placeholder="Describe what you want to create...",
                        label="Message",
                        lines=3,
                        scale=4,
                    )
                    submit_btn = gr.Button("Generate", variant="primary", scale=1)

                with gr.Row():
                    clear_btn = gr.Button("Clear Chat")
                    gr.Button("Copy Last Code")

                # Code output
                code_output = gr.Code(
                    label="Generated Code",
                    language="html",
                    lines=20,
                )

                # HTML Preview (only shown for HTML output)
                html_preview = gr.HTML(label="Preview", visible=False)

                # State
                history = gr.State([])
                last_code = gr.State("")
                rag_db = gr.State(None)
                rag_qa = gr.State(None)

        def update_interface(output_type_value):
            """Update interface based on output type"""
            if output_type_value == "HTML":
                return gr.update(visible=True), gr.update(language="html")
            elif output_type_value == "Transformers.js":
                return gr.update(visible=False), gr.update(language="javascript")
            elif output_type_value == "Svelte":
                return gr.update(visible=False), gr.update(language="javascript")
            elif output_type_value == "Python":
                return gr.update(visible=False), gr.update(language="python")
            else:
                return gr.update(visible=False), gr.update(language=None)

        def get_system_prompt(output_type_value, enable_search_value):
            """Get appropriate system prompt"""
            if output_type_value == "HTML":
                return (
                    HTML_SYSTEM_PROMPT_WITH_SEARCH
                    if enable_search_value
                    else HTML_SYSTEM_PROMPT
                )
            elif output_type_value == "Transformers.js":
                return (
                    TRANSFORMERS_JS_SYSTEM_PROMPT_WITH_SEARCH
                    if enable_search_value
                    else TRANSFORMERS_JS_SYSTEM_PROMPT
                )
            elif output_type_value == "Svelte":
                return (
                    SVELTE_SYSTEM_PROMPT_WITH_SEARCH
                    if enable_search_value
                    else SVELTE_SYSTEM_PROMPT
                )
            else:
                prompt = (
                    GENERIC_SYSTEM_PROMPT_WITH_SEARCH
                    if enable_search_value
                    else GENERIC_SYSTEM_PROMPT
                )
                return prompt.format(language=output_type_value.lower())

        def chat_and_update(
            message, history_state, model, temp, output_type_value, enable_search_value
        ):
            """Handle chat and update all outputs"""
            if not message:
                return history_state, history_state, "", "", gr.update(visible=False)

            system_prompt = get_system_prompt(output_type_value, enable_search_value)

            # Get response
            response, new_history = chat_with_model(
                message, history_state, model, temp, system_prompt, enable_search_value
            )

            # Process code
            processed_code = process_code_output(response, output_type_value)

            # Update preview if HTML
            preview_update = gr.update(visible=False)
            if output_type_value == "HTML" and processed_code:
                preview_update = gr.update(value=processed_code, visible=True)

            # Convert history to chatbot format
            chatbot_messages = history_to_chatbot_messages(new_history)

            return (
                chatbot_messages,
                new_history,
                processed_code,
                processed_code,
                preview_update,
            )

        def clear_chat():
            return [], [], "", "", gr.update(visible=False)

        def copy_to_clipboard(code):
            return gr.update(value="Copied to clipboard!")

        # Event handlers
        output_type.change(
            update_interface,
            inputs=[output_type],
            outputs=[html_preview, code_output],
        )

        submit_btn.click(
            chat_and_update,
            inputs=[
                msg,
                history,
                model_dropdown,
                temperature,
                output_type,
                enable_search,
            ],
            outputs=[chatbot, history, code_output, last_code, html_preview],
        ).then(lambda: "", outputs=[msg])

        # OCR helper: return extracted text or an error message
        def ocr_from_image(image):
            if not OCR_AVAILABLE:
                return "Error: pytesseract or Pillow not installed on the server. Install pytesseract and pillow."
            if image is None:
                return ""
            try:
                # image is a PIL Image
                text = pytesseract.image_to_string(image).strip()
                return text
            except Exception as e:
                return f"OCR error: {e}"

        # Button handlers for image flows
        def handle_extract_text(image):
            text = ocr_from_image(image)
            # Place extracted text into the message box so user can review
            return text

        def handle_generate_from_image(
            image, history_state, model, temp, output_type_value, enable_search_value
        ):
            # Extract text first
            extracted = ocr_from_image(image)
            if extracted.startswith("Error"):
                # propagate error into chat
                assistant = extracted
                history_state.append(["(image)", assistant])
                return (
                    history_to_chatbot_messages(history_state),
                    history_state,
                    assistant,
                    assistant,
                    gr.update(visible=False),
                )

            # Build a prompt that asks the model to synthesize HTML/CSS from OCR + inferred layout
            prompt = (
                f"You are an expert frontend developer. Based on the text and visual cues below (extracted from an image), generate a single-file responsive HTML + CSS. "
                f"Use semantic HTML, modern CSS, and include a mobile-friendly hamburger menu if necessary.\n\nExtracted text and labels:\n{extracted}\n\nIf layout hints are absent, infer a sensible layout. Return only the HTML inside a code block."
            )

            response, new_history = chat_with_model(
                prompt,
                history_state,
                model,
                temp,
                get_system_prompt(output_type_value, enable_search_value),
                enable_search_value,
            )

            processed_code = process_code_output(response, output_type_value)
            preview_update = gr.update(visible=False)
            if output_type_value == "HTML" and processed_code:
                preview_update = gr.update(value=processed_code, visible=True)

            chatbot_messages = history_to_chatbot_messages(new_history)
            return (
                chatbot_messages,
                new_history,
                processed_code,
                processed_code,
                preview_update,
            )

        extract_text_btn.click(handle_extract_text, inputs=[image_input], outputs=[msg])
        gen_from_image_btn.click(
            handle_generate_from_image,
            inputs=[
                image_input,
                history,
                model_dropdown,
                temperature,
                output_type,
                enable_search,
            ],
            outputs=[chatbot, history, code_output, last_code, html_preview],
        )

        # RAG event wiring
        def _store_rag(db, qa, status_text):
            # gr.State objects are set via returning to the state outputs
            return db, qa, status_text

        rag_process_btn.click(
            fn=process_and_initialize,
            inputs=[rag_files],
            outputs=[rag_db, rag_qa, rag_status],
            show_progress=True,
        )

        def rag_ask_handler(query, qa_chain, chat_state):
            if not qa_chain:
                return chat_state, ""
            # user_query_typing_effect is a generator; we need to yield from it
            for history, status in user_query_typing_effect(
                query, qa_chain, chat_state
            ):
                yield history, status

        rag_ask_btn.click(
            fn=rag_ask_handler,
            inputs=[rag_query, rag_qa, chatbot],
            outputs=[chatbot, rag_status],
        )

        msg.submit(
            chat_and_update,
            inputs=[
                msg,
                history,
                model_dropdown,
                temperature,
                output_type,
                enable_search,
            ],
            outputs=[chatbot, history, code_output, last_code, html_preview],
        ).then(lambda: "", outputs=[msg])

        clear_btn.click(
            clear_chat, outputs=[chatbot, history, code_output, last_code, html_preview]
        )

        # Example buttons
        for btn, example_text in example_buttons:
            btn.click(lambda x: x, inputs=[gr.State(example_text)], outputs=[msg])

    return demo


if __name__ == "__main__":
    # Check if Ollama is running
    if not get_ollama_client():
        print("⚠️  Warning: Ollama is not running!")
        print("Please start Ollama with: ollama serve")
        print("")

    if not AVAILABLE_MODELS:
        print("❌ No Ollama models found!")
        print("Please install at least one model:")
        print("  ollama pull llama3.1:8b")
        print("  ollama pull mistral:7b")
        exit(1)

    print(f"✅ Found {len(AVAILABLE_MODELS)} Ollama models")
    print(f"📍 Default model: {DEFAULT_MODEL_ID}")

    if not tavily_client:
        print("ℹ️  Web search disabled (no TAVILY_API_KEY)")
    else:
        print("✅ Web search enabled")

    # Create and launch interface
    demo = create_interface()
    demo.launch(
        server_name="0.0.0.0",
        server_port=7860,
        share=False,
        inbrowser=True,
    )
