# 🚀 Lokal-ollama-coder

**Local AI-powered code generator using Ollama models**

Generate HTML, CSS, JavaScript, Python, and more with privacy-focused local AI models. No API keys required - everything runs on your machine!

![AnyCoder-Ollama Demo](https://img.shields.io/badge/AI-Code%20Generator-blue) ![Ollama](https://img.shields.io/badge/Ollama-Compatible-green) ![Privacy](https://img.shields.io/badge/Privacy-Local%20Only-yellow)

## ✨ Features

- 🎯 **Multi-language code generation** - HTML, CSS, JavaScript, Python, C++, and more
- 🖼️ **Image-to-code** - Convert UI designs to working code (with vision models)
- 🌐 **Website redesign** - Extract and modernize existing websites
- 📄 **File processing** - Extract text from PDFs, DOCX, images
- 🔄 **Smart modifications** - Edit existing code with natural language
- 📱 **Live preview** - See HTML results instantly
- 🔍 **Web search** - Enhanced with real-time information (optional)
- 🔒 **100% Private** - All processing happens locally

## 🎬 Quick Demo

```bash
# Example: Generate a modern dashboard
"Create a responsive admin dashboard with sidebar navigation and dark mode toggle"

# Example: Convert image to code
Upload a UI mockup → Get working HTML/CSS

# Example: Redesign website
Enter URL → Get modernized responsive version
```

## 🛠️ Setup & Run (updated)

Follow these steps to prepare and run the app locally. The app entrypoint is now `main.py`.

1) Install Ollama

```bash
# macOS / Linux
curl -fsSL https://ollama.ai/install.sh | sh

# Windows: download the installer from https://ollama.ai
```

2) Download models (example)

```bash
ollama pull codellama:7b
ollama pull llava:7b
ollama pull llama3.1:8b
```

3) Start Ollama server

```bash
ollama serve
```

4) Install Python dependencies

```bash
pip install -r requirements.txt
# Optional: install python-dotenv to load a .env file automatically
pip install python-dotenv
```

5) Configure environment variables (recommended: use a `.env` file)

Create a file named `.env` at the repository root (same folder as `main.py`):

```
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_DEFAULT_MODEL=gemma3:12b   # optional, must match an installed model id
TAVILY_API_KEY=your_tavily_api_key # optional, leave blank to disable web search
```

Note: `.env` is not loaded automatically by Python — either export the variables in your shell or install `python-dotenv` and add `from dotenv import load_dotenv; load_dotenv()` near the top of `main.py`.

6) Run the app

WSL / bash:
```bash
export TAVILY_API_KEY="..."        # optional
export OLLAMA_DEFAULT_MODEL="gemma3:12b"  # optional
python main.py
```

Windows CMD (temporary for this session):
```cmd
set TAVILY_API_KEY=...
set OLLAMA_DEFAULT_MODEL=gemma3:12b
python main.py
```

Windows persistent (new shells will see it):
```cmd
setx OLLAMA_DEFAULT_MODEL "gemma3:12b"
```

Open the printed local URL (usually `http://0.0.0.0:7860` or `http://localhost:7860`).

## 📋 Requirements

Add the following to `requirements.txt` (or install with pip):

```txt
gradio
ollama
tavily-python
python-dotenv  # optional, recommended for .env support
PyPDF2
python-docx
pytesseract
Pillow
opencv-python
requests
beautifulsoup4
html2text
```

## 🎯 Supported Languages

| Language | Use Case | Example |
|----------|----------|---------|
| **HTML** | Web pages, UI components | Landing pages, forms |
| **CSS** | Styling, animations | Responsive designs |
| **JavaScript** | Interactive features | Todo apps, calculators |
| **Python** | Scripts, automation | Data processing |
| **React** | Modern web apps | Component libraries |
| **Svelte** | Fast web apps | Performance-focused UIs |
| **C/C++** | System programming | Algorithms |

## 🖼️ Vision Models (Image-to-Code)

With vision-enabled models like Llava:

1. **Upload UI mockup** → Get HTML/CSS
2. **Sketch wireframe** → Get responsive layout
3. **Screenshot design** → Get working code

```bash
# Download vision model
ollama pull llava:13b  # Better quality
# or
ollama pull llava:7b   # Faster
```

## 🌐 Web Search Integration (Optional)

For enhanced results with real-time information:

```bash
export TAVILY_API_KEY="your-api-key"
# Get free key at: https://tavily.com
```

## 🎨 Usage Examples

### Basic Code Generation
```
Prompt: "Create a responsive pricing table with 3 tiers"
Output: Complete HTML/CSS with modern styling
```

### Website Redesign
```
1. Enter URL: https://old-website.com
2. App extracts content automatically
3. Get modernized responsive version
```

### Code Modification
```
1. Generate initial code
2. Ask: "Add dark mode toggle"
3. Get updated code with changes
```

### Multi-file Projects
```
Language: "transformers.js"
Output: index.html + index.js + style.css
```

## ⚙️ Configuration

### Custom Ollama Host
```bash
export OLLAMA_BASE_URL="http://your-host:11434"
```

### OCR Setup (for text extraction from images)
```bash
# Ubuntu/Debian
sudo apt-get install tesseract-ocr

# macOS
brew install tesseract

# Windows: Download from GitHub
```

## 🔧 Model Recommendations

### For Code Generation:
- **CodeLlama 13B** - Best quality
- **DeepSeek Coder 6.7B** - Specialized for coding
- **CodeLlama 7B** - Good balance

### For Vision Tasks:
- **Llava 13B** - Best image understanding
- **Llava 7B** - Faster processing

### For General Use:
- **Llama 3.1 8B** - Excellent all-around
- **Mistral 7B** - Fast and reliable

## 🚨 Troubleshooting

### Ollama Not Connected
```bash
# Check if Ollama is running
curl http://localhost:11434/api/tags

# Restart Ollama
ollama serve
```

### No Models Available
```bash
# List downloaded models
ollama list

# Download a model
ollama pull codellama:7b
```

### Dropdown default / model mismatch
If you see an error like:

```
Value: gemma3:12b is not in the list of choices: ['llama3.1:8b']
```

It means `OLLAMA_DEFAULT_MODEL` (or your chosen default) doesn't match the models that the app discovered at runtime. Fixes:
- Make sure the model id in `.env` (or the environment) exactly matches one listed by `ollama list`.
- Remove or unset `OLLAMA_DEFAULT_MODEL` to let the app pick the first installed model automatically.
- You can also edit `main.py` to force the app to show all installed models rather than a predefined subset.

### Port Already in Use
```bash
# Run on different port
python app.py --server-port 7861
```

## 🤝 Contributing

1. Fork the repository
2. Create feature branch: `git checkout -b feature-name`
3. Commit changes: `git commit -m 'Add feature'`
4. Push to branch: `git push origin feature-name`
5. Submit pull request

## 📄 License

MIT License - see [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **Ollama** - Local AI model hosting
- **Gradio** - Web interface framework
- **CodeLlama** - Meta's code generation model
- **Llava** - Vision-language model

## 🔗 Links

- [Ollama Documentation](https://ollama.ai)
- [CodeLlama Model](https://ollama.ai/library/codellama)
- [Llava Vision Model](https://ollama.ai/library/llava)
- [Gradio Documentation](https://gradio.app)

---

**⭐ Star this repo if you find it useful!**

Made with ❤️ for the open-source community
