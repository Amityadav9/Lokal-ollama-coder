# 🚀 Lokal-ollama-coder

**Local AI-powered code generator with RAG document chat using Ollama models**

Generate HTML, CSS, JavaScript, Python, and more with privacy-focused local AI models. Now includes RAG functionality for document-based Q&A. No API keys required - everything runs on your machine!

![AnyCoder-Ollama Demo](https://img.shields.io/badge/AI-Code%20Generator-blue) ![Ollama](https://img.shields.io/badge/Ollama-Compatible-green) ![Privacy](https://img.shields.io/badge/Privacy-Local%20Only-yellow) ![RAG](https://img.shields.io/badge/RAG-Document%20Chat-orange)

## ✨ Features

### 🎯 Code Generation
- **Multi-language code generation** - HTML, CSS, JavaScript, Python, C++, and more
- **Image-to-code** - Convert UI designs to working code (with vision models)
- **Website redesign** - Extract and modernize existing websites
- **Smart modifications** - Edit existing code with natural language
- **Live preview** - See HTML results instantly

### 📄 RAG Document Chat
- **PDF & TXT support** - Upload documents for AI-powered Q&A
- **Local vector database** - Using FAISS for document embeddings
- **Conversation memory** - Maintains chat history during document discussions
- **Real-time processing** - Documents processed locally with visual feedback

### 🔍 Additional Features
- **File processing** - Extract text from PDFs, DOCX, images (OCR)
- **Web search** - Enhanced with real-time information (optional)
- **Multi-modal** - Vision models for image analysis
- **🔒 100% Private** - All processing happens locally

## 🎬 Quick Demo

```bash
# Example: Generate a modern dashboard
"Create a responsive admin dashboard with sidebar navigation and dark mode toggle"

# Example: Convert image to code
Upload a UI mockup → Get working HTML/CSS

# Example: RAG document chat
Upload PDF → Ask "What are the main conclusions?" → Get AI answers

# Example: Redesign website
Enter URL → Get modernized responsive version
```

## 🛠️ Setup & Run

### Prerequisites

1) **Install Ollama**

```bash
# macOS / Linux
curl -fsSL https://ollama.ai/install.sh | sh

# Windows: download the installer from https://ollama.ai
```

2) **Download models** (choose based on your needs)

```bash
# For code generation
ollama pull codellama:7b
ollama pull llama3.1:8b

# For vision tasks (image-to-code)
ollama pull llava:7b

# For RAG (recommended models)
ollama pull gemma3:12b
ollama pull qwen2.5:7b
```

3) **Start Ollama server**

```bash
ollama serve
```

### Installation

1) **Clone and setup**

```bash
git clone <repository-url>
cd Lokal-ollama-coder
```

2) **Install Python dependencies**

```bash
pip install -r requirements.txt
```

3) **Configure environment** (create `.env` file)

```bash
# .env file (optional but recommended)
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_DEFAULT_MODEL=gemma3:12b
TAVILY_API_KEY=your_tavily_api_key  # optional for web search

# RAG-specific configuration
OLLAMA_HOST=http://localhost:11434
MODEL_NAME=gemma3:12b
EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2
```

4) **Run the application**

```bash
python main.py
```

## 📋 Requirements

The `requirements.txt` includes dependencies for both code generation and RAG:

```txt
# Core dependencies
gradio
ollama
python-dotenv
requests
beautifulsoup4
html2text

# Optional features
tavily-python          # Web search
PyPDF2                 # PDF processing
python-docx            # DOCX processing  
pytesseract            # OCR
Pillow
opencv-python

# RAG / LangChain dependencies
langchain
langchain-community
langchain-huggingface
langchain-ollama
faiss-cpu
sentence-transformers
torch
transformers
```

## 🎯 Supported Languages & Features

### Code Generation Languages
| Language | Use Case | Example |
|----------|----------|---------|
| **HTML** | Web pages, UI components | Landing pages, forms |
| **CSS** | Styling, animations | Responsive designs |
| **JavaScript** | Interactive features | Todo apps, calculators |
| **Python** | Scripts, automation | Data processing |
| **React** | Modern web apps | Component libraries |
| **Svelte** | Fast web apps | Performance-focused UIs |
| **C/C++** | System programming | Algorithms |

### RAG Document Types
| Format | Description | Processing |
|--------|-------------|-----------|
| **PDF** | Research papers, reports | Text extraction + chunking |
| **TXT** | Plain text documents | Direct processing |
| **DOCX** | Word documents | Content extraction |
| **Images** | OCR text extraction | Tesseract integration |

## 🖼️ Vision Models (Image-to-Code)

With vision-enabled models like Llava:

1. **Upload UI mockup** → Get HTML/CSS
2. **Sketch wireframe** → Get responsive layout  
3. **Screenshot design** → Get working code

```bash
# Download vision models
ollama pull llava:13b  # Better quality
ollama pull llava:7b   # Faster
```

## 📚 RAG Usage Examples

### Document Upload & Chat
```
1. Click "Upload Documents" → Select PDF/TXT files
2. Click "Process Documents" → Wait for "Database created!"
3. Type question: "What are the key findings?"
4. Get AI-powered answers based on your documents
```

### Advanced RAG Features
- **Conversation memory** - Follow-up questions remember context
- **Source attribution** - Answers reference document sections
- **Multi-document** - Upload multiple files for comprehensive analysis
- **Real-time processing** - See progress as documents are processed

## 🌐 Web Search Integration (Optional)

For enhanced results with real-time information:

```bash
export TAVILY_API_KEY="your-api-key"
# Get free key at: https://tavily.com
```

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

### Model Configuration
The system automatically detects installed Ollama models. Configure preferences via environment variables:

```bash
# Preferred model order (comma-separated)
export MODEL_PREFERENCE="gemma3:12b,llama3.1:8b,codellama:7b"

# Custom Ollama host
export OLLAMA_BASE_URL="http://your-host:11434"

# RAG-specific model
export MODEL_NAME="gemma3:12b"
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
- **CodeLlama 13B** - Best code quality
- **DeepSeek Coder 6.7B** - Specialized for coding
- **CodeLlama 7B** - Good balance of speed/quality

### For RAG & Document Chat:
- **Gemma3 12B** - Excellent reasoning and context
- **Qwen2.5 7B** - Good for document analysis
- **Llama 3.1 8B** - Strong general capabilities

## 🚨 Troubleshooting

### Ollama Connection Issues
```bash
# Check if Ollama is running
curl http://localhost:11434/api/tags

# Restart Ollama
ollama serve
```

### RAG Processing Errors
```bash
# Check if model supports your documents
ollama list | grep -E "(gemma|llama|qwen)"

# Verify dependencies
pip install langchain faiss-cpu sentence-transformers
```

### Model Selection Issues
If you see: `Value: gemma3:12b is not in the list of choices`

1. Check installed models: `ollama list`
2. Update environment variable to match installed model
3. Or remove `OLLAMA_DEFAULT_MODEL` to auto-select

### Memory Issues
```bash
# For large documents, reduce chunk size in src/config.py
# For large models, ensure sufficient RAM/VRAM
```

## 📁 Project Structure

```
lokal-ollama-coder/
├── main.py              # Main application entry point
├── src/
│   ├── __init__.py      # Package initialization  
│   ├── rag.py           # RAG functionality
│   └── config.py        # Configuration management
├── requirements.txt     # All dependencies
├── .env                 # Environment configuration (create this)
└── README.md           # This file
```

## 🤝 Contributing

1. Fork the repository
2. Create feature branch: `git checkout -b feature-name`
3. Commit changes: `git commit -m 'Add feature'`
4. Push to branch: `git push origin feature-name`
5. Submit pull request

## 📄 License

MIT License - see LICENSE file for details.

## 🙏 Acknowledgments

- **Ollama** - Local AI model hosting
- **Gradio** - Web interface framework
- **LangChain** - RAG framework and document processing
- **FAISS** - Vector similarity search
- **CodeLlama** - Meta's code generation model
- **Llava** - Vision-language model

## � Links

- [Ollama Documentation](https://ollama.ai)
- [LangChain Documentation](https://python.langchain.com/)
- [CodeLlama Model](https://ollama.ai/library/codellama)
- [Llava Vision Model](https://ollama.ai/library/llava)
- [Gradio Documentation](https://gradio.app)

---

**⭐ Star this repo if you find it useful!**

Made with ❤️ for the open-source community - Now with RAG superpowers! 🚀📚
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
