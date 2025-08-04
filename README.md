# File Search Agent 🔍

A powerful file search tool with both traditional pattern matching and AI-powered natural language search capabilities. Built with Python, featuring both a command-line interface and an interactive web application.

## ✨ Features

### 🔍 **Search Types**
- **🤖 AI Search**: Natural language queries powered by OpenAI/Anthropic models
- **Name Search**: Find files by filename patterns (wildcards supported)
- **Content Search**: Search inside file contents with pattern matching
- **Size Search**: Filter files by size ranges

### 🎯 **Key Capabilities**
- **Case-insensitive search** (always enabled for better user experience)
- **Recursive directory traversal** with depth control
- **Multiple output formats** (table, JSON, CSV)
- **Web interface** with interactive charts and visualizations
- **Command-line interface** for scripting and automation
- **Smart file filtering** with include/exclude patterns
- **Export capabilities** for results

## 🚀 Quick Start

### Installation

1. **Clone the repository:**
   ```bash
   git clone <repository-url>
   cd file-search-agent
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables (optional, for AI search):**
   ```bash
   cp .env.example .env
   # Edit .env and add your API keys
   ```

### Web Interface (Recommended)

```bash
streamlit run streamlit_app.py
```

Open your browser to `http://localhost:8501` for an interactive interface with:
- Easy search path selection
- Visual charts and analytics
- Export capabilities
- Real-time search results

### Command Line Usage

```bash
# Search by filename
python main.py name "*.py" /path/to/search

# Search file contents
python main.py content "function.*search" /path/to/search

# Search by file size
python main.py size --min-size 1MB --max-size 100MB /path/to/search

# AI-powered natural language search (requires API key)
python main.py ai "Find all PDF files" ~/Downloads
```

## 🤖 AI-Powered Search

The File Search Agent includes AI-powered search capabilities for natural language queries.

### Setup AI Search

1. **Get an API key**:
   - **OpenAI**: Get an API key from [OpenAI Platform](https://platform.openai.com/api-keys)
   - **Anthropic**: Get an API key from [Anthropic Console](https://console.anthropic.com/)

2. **Configure environment variables**:
   ```bash
   # Copy the example file
   cp .env.example .env
   
   # Edit .env and add your API key:
   OPENAI_API_KEY=your_openai_api_key_here
   # OR
   ANTHROPIC_API_KEY=your_anthropic_api_key_here
   ```

3. **Use in web interface**:
   - Select "AI Search" from the search type dropdown
   - Choose your AI provider and model in the sidebar
   - Enter natural language queries

### AI Search Examples

Use natural language instead of patterns:

```
"Find my Python scripts for data analysis"
"Show me configuration files"
"Look for PDF documents about machine learning"
"Find test files or unit tests"
"Show me README files and documentation"
"Find JavaScript files for user authentication"
"Look for log files from last week"
"Find images in my project folders"
```

### How AI Search Works

1. **Query Interpretation**: AI analyzes your natural language query
2. **Strategy Generation**: Creates optimized search patterns and keywords
3. **Multi-Modal Search**: Combines filename, content, and metadata searches
4. **Intelligent Fallback**: Uses keyword-based search if AI is unavailable

## 📖 Usage Examples

### Command Line Interface

#### Name Search
```bash
# Find Python files
python main.py name "*.py" .

# Find configuration files
python main.py name "*config*" /path/to/search

# Find files with specific patterns
python main.py name "*test*" /path/to/tests
```

#### Content Search
```bash
# Find files containing specific text
python main.py content "TODO" .

# Search in specific file types
python main.py content "import pandas" . --file-pattern "*.py"
```

#### Size Search
```bash
# Find large files (>10MB)
python main.py size --min-size 10MB /path/to/search

# Find files in size range
python main.py size --min-size 1KB --max-size 1MB .
```

#### AI Search
```bash
# Natural language queries
python main.py ai "Find all PDF files" ~/Downloads
python main.py ai "Show me Python scripts" ~/projects
python main.py ai "Find configuration files" .
```

### CLI Options

```bash
# Global options
--max-depth N          # Maximum directory depth
--include-hidden       # Include hidden files
--max-results N        # Limit number of results
--format FORMAT        # Output format: table, json, csv

# Size search specific
--min-size SIZE        # Minimum file size (e.g., 1KB, 1MB, 1GB)
--max-size SIZE        # Maximum file size
```

## ⚙️ Configuration

### Environment Variables

Create a `.env` file (copy from `.env.example`):

```bash
# OpenAI API Key (for AI search)
OPENAI_API_KEY=your_openai_api_key_here

# Anthropic API Key (for AI search)
ANTHROPIC_API_KEY=your_anthropic_api_key_here

# Optional: Default AI settings
DEFAULT_AI_PROVIDER=openai
DEFAULT_AI_MODEL=gpt-4o-mini
```

### Output Formats

- **Table** (default): Formatted console output
- **JSON**: Machine-readable format
- **CSV**: Spreadsheet-compatible format

## 🏗️ Project Structure

```
file-search-agent/
├── main.py                    # CLI entry point
├── streamlit_app.py          # Web UI application
├── requirements.txt          # Python dependencies
├── .env.example             # Environment variables template
└── src/                     # Source code
    ├── cli.py               # CLI implementation
    ├── config.py            # Configuration management
    ├── output_formatter.py  # Output formatting
    └── searchers/           # Search implementations
        ├── base_searcher.py      # Base search interface
        ├── local_searcher.py     # Local file search
        ├── ai_searcher.py        # AI-powered search
        └── google_drive_searcher.py # Google Drive (future)
```

## 🤖 AI Models Supported

### OpenAI Models
- GPT-4o (latest)
- GPT-4o-mini (fast, cost-effective)
- GPT-4 Turbo
- GPT-3.5 Turbo

### Anthropic Models
- Claude 3.5 Sonnet
- Claude 3.5 Haiku (fast, cost-effective)
- Claude 3 Opus

## 🔧 Development

### Adding New Search Types

Create a new searcher class inheriting from `BaseSearcher`:

```python
from src.searchers.base_searcher import BaseSearcher

class CustomSearcher(BaseSearcher):
    def search_by_name(self, search_path: str, pattern: str, **kwargs):
        # Implementation here
        pass
```

## 📝 License

[Add your license information here]

## 🤝 Contributing

[Add contribution guidelines here]

---

**Built with ❤️ using Python, Streamlit, and AI**



