# File Search Agent

A powerful tool for searching files on your local machine with plans to extend to Google Drive. Built with Python, this tool provides fast and flexible file searching capabilities with multiple search criteria. Available as both a command-line interface and a web-based Streamlit application.

## Features

### Current Features (Local Search)
- **🤖 AI-Powered Search**: Natural language search using LLMs (OpenAI/Anthropic) with intelligent query interpretation
- **Name-based search**: Find files by filename patterns with wildcard support
- **Content search**: Search inside text files for specific content
- **Size-based search**: Find files within specific size ranges
- **Flexible filtering**: Include/exclude patterns, hidden files, and depth control
- **Multiple output formats**: Table, JSON, and CSV output
- **Rich console output**: Beautiful, colored terminal output with progress indicators (CLI)
- **Web-based UI**: Interactive Streamlit interface with charts and visualizations
- **Configurable**: Customizable search preferences and defaults
- **Export capabilities**: Download results as CSV or JSON

### Planned Features (Cloud Storage Integration)
- **Google Drive search**: Search files in Google Drive (architecture in place, implementation pending)
- **iCloud integration**: Search files in iCloud Drive (future consideration)
- Cached search results for better performance
- Unified search across local and cloud storage
- Advanced authentication and permission handling
- Cross-platform cloud storage support

## Current Implementation Status

### ✅ Fully Implemented
- **Local file search**: Complete implementation with all search types
- **Command-line interface**: Full CLI with all features
- **Streamlit web interface**: Interactive web app with visualizations
- **Performance optimizations**: Chunked reading, file size limits, binary detection
- **Configuration management**: JSON-based settings with CLI configuration
- **Multiple output formats**: Table, JSON, CSV export

### 🚧 In Development
- **Google Drive integration**: Architecture in place, API implementation pending
- **Search performance**: Continuous optimization for large directories

### 📋 Planned
- **iCloud Drive support**: Research phase for API availability
- **Advanced search syntax**: Boolean operators, regex patterns
- **Search indexing**: For faster repeated searches
- **Additional cloud providers**: OneDrive, Dropbox integration


## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd file_search_agent
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Make the script executable (optional):
```bash
chmod +x streamlit_app.py
chmod +x main.py
```

## Usage

### Streamlit Web Interface (Recommended)

Launch the web-based interface:
```bash
python streamlit_app.py --launch
# OR
streamlit run streamlit_app.py
# OR just run directly
python streamlit_app.py
```

The web interface provides:
- **Interactive search forms** with real-time configuration
- **Visual results** with tables, charts, and statistics
- **Advanced filtering** and sorting capabilities
- **Export functionality** for CSV and JSON formats
- **Search history** tracking
- **File type distribution** and size analysis charts
- **Content match highlighting** for text searches

#### Web Interface Features:
- 🔍 **Search Types**: Name patterns, content search, size-based filtering, and AI-powered natural language search
- 📂 **Search Path Input**: Simple text field to specify search directory (e.g., ~/Downloads, ~/Documents, .)
- ⚙️ **Configuration Panel**: Adjust search depth, include/exclude patterns, and more
- 📊 **Visualizations**: File type pie charts, size histograms, and timeline views
- 💾 **Export Options**: Download results in CSV or JSON format
- 📜 **Search History**: Track and review previous searches
- 🔧 **Advanced Filters**: Filter results by file type, size range, and filename

### 🤖 AI-Powered Search

The File Search Agent now includes AI-powered search capabilities that let you search using natural language queries.

#### Setup AI Search

1. **Install AI dependencies** (if not already installed):
```bash
pip install pydantic-ai openai anthropic
```

2. **Get an API key**:
   - For OpenAI: Get an API key from [OpenAI Platform](https://platform.openai.com/api-keys)
   - For Anthropic: Get an API key from [Anthropic Console](https://console.anthropic.com/)

3. **Configure in the web interface**:
   - Select "AI Search" from the search type dropdown
   - Choose your preferred AI provider (OpenAI or Anthropic)
   - Select the model (e.g., gpt-4o-mini, claude-3-5-haiku)
   - Enter your API key in the sidebar

#### AI Search Examples

Instead of traditional patterns, use natural language queries:

```
"Find my Python scripts for data analysis"
"Show me configuration files for my web server"
"Look for documents about machine learning"
"Find test files or unit tests"
"Show me README files and documentation"
"Find JavaScript files that handle user authentication"
"Look for log files from the last week"
"Find images and photos in my project folders"
```

#### How AI Search Works

1. **Query Interpretation**: The AI analyzes your natural language query to understand what you're looking for
2. **Search Strategy**: It generates multiple search strategies including:
   - Relevant file patterns (e.g., *.py, *.config, *.md)
   - Content keywords and synonyms
   - Alternative naming conventions
3. **Multi-Modal Search**: Combines filename, content, and metadata searches
4. **Intelligent Ranking**: Results are ranked by relevance with AI confidence scores

#### AI Search Features

- **Natural Language Processing**: Understands context and intent
- **Smart Pattern Generation**: Creates effective search patterns automatically
- **Synonym Recognition**: Finds files using related terms
- **Multi-Strategy Search**: Combines multiple search approaches
- **Confidence Scoring**: Shows how confident the AI is about results
- **Fallback Handling**: Gracefully handles API errors with traditional search

## Quick Start Examples

### Using the Web Interface
1. **Launch the app**: `python streamlit_app.py --launch`
2. **Open your browser** to the displayed URL (usually http://localhost:8501)
3. **Choose search type** from the sidebar (AI Search, Name, Content, or Size)
4. **Enter search path** (e.g., ~/Downloads, ~/Documents, . for current directory)
5. **Enter your search query** in the appropriate format:
   - **AI Search**: Natural language (e.g., "Find Lucy's resume files")
   - **Name Search**: File patterns (e.g., "*.pdf", "*resume*")
   - **Content Search**: Text to find inside files
   - **Size Search**: Specify minimum/maximum file sizes
6. **Click "🔍 Search"** to see results with visualizations
7. **Export results** using the Export tab

### Command Line Interface

### Basic Commands

#### Search by filename
```bash
python main.py name "*.py" /path/to/search
python main.py name "config*" .
python main.py name "*.txt" ~ --include-hidden
```

#### Search by file content
```bash
python main.py content "function main" /path/to/search
python main.py content "TODO" . --file-pattern "*.py" --file-pattern "*.js"
python main.py content "import numpy" .
```

#### Search by file size
```bash
python main.py size . --min-size 1MB --max-size 100MB
python main.py size /path/to/search --min-size 500KB
python main.py size . --max-size 10MB --format json
```

### Advanced Options

#### Output Formats
- `--format table` (default): Rich table format
- `--format json`: JSON output for programmatic use
- `--format csv`: CSV format for spreadsheet import

#### Filtering Options
- `--include-hidden`: Include hidden files (starting with .)
- `--max-depth N`: Limit search depth
- `--include "*.pattern"`: Include only files matching patterns
- `--exclude "*.pattern"`: Exclude files matching patterns

#### Examples
```bash
# Search for Python files containing "class" with detailed output
python main.py content "class" . --file-pattern "*.py" --format table --max-results 50

# Find large log files, excluding temporary files
python main.py size /var/log --min-size 10MB --exclude "*.tmp" --exclude "*.swp"

# Search for configuration files by name
python main.py name "*config*" /etc --include "*.conf" --include "*.cfg" --include "*.ini"
```

### Configuration

The tool uses a configuration file located at `~/.file_search_agent/config.json`. You can view and modify settings:

```bash
# Show current configuration
python main.py config-show

# Set configuration values
python main.py config-set search.include_hidden true
python main.py config-set output.max_results 200
python main.py config-set output.format json
```

### Default Configuration

```json
{
  "search": {
    "include_hidden": false,
    "max_depth": null,
    "exclude_patterns": [
      "*.pyc", "__pycache__", ".git", ".svn", 
      "node_modules", ".DS_Store", "Thumbs.db", "*.log", "*.tmp"
    ],
    "include_patterns": [],
    "content_search_patterns": [
      "*.txt", "*.py", "*.js", "*.html", "*.css", 
      "*.md", "*.json", "*.xml", "*.yaml", "*.yml"
    ]
  },
  "output": {
    "format": "table",
    "max_results": 100,
    "show_size": true,
    "show_modified_time": true,
    "show_file_type": true
  },
  "cloud_storage": {
    "google_drive": {
      "enabled": false,
      "credentials_path": null,
      "cache_enabled": true,
      "cache_duration": 3600
    },
    "icloud": {
      "enabled": false,
      "local_sync_path": "~/Library/Mobile Documents/com~apple~CloudDocs",
      "search_synced_only": true
    }
  }
}
```

## Project Structure

```
file_search_agent/
├── src/
│   ├── __init__.py
│   ├── cli.py                 # Command-line interface
│   ├── config.py              # Configuration management
│   ├── output_formatter.py    # Output formatting and display
│   └── searchers/
│       ├── __init__.py
│       ├── base_searcher.py        # Abstract base class
│       ├── local_searcher.py       # Local file system searcher
│       └── google_drive_searcher.py # Google Drive searcher (future)
├── main.py                    # Entry point
├── requirements.txt           # Python dependencies
├── README.md                  # This file
└── tests/                     # Test files (future)
```

## Architecture

The project is designed with a modular architecture:

- **Base Searcher**: Abstract interface for all search implementations
- **Local Searcher**: Implements local file system search
- **Google Drive Searcher**: Placeholder for future cloud search functionality
- **Config Manager**: Handles configuration persistence and defaults
- **Output Formatter**: Provides multiple output formats with rich console display
- **CLI**: Command-line interface built with Click

## Development

### Adding New Search Types

To add a new search type, create a new searcher class that inherits from `BaseSearcher`:

```python
from src.searchers.base_searcher import BaseSearcher, SearchResult

class CustomSearcher(BaseSearcher):
    def search_by_name(self, search_path: str, pattern: str, **kwargs):
        # Implementation here
        pass
    
    def search_by_content(self, search_path: str, pattern: str, **kwargs):
        # Implementation here
        pass
    
    def search_by_size(self, search_path: str, min_size: int = None, max_size: int = None, **kwargs):
        # Implementation here
        pass
```

### Extending Output Formats

Add new output formats by extending the `OutputFormatter` class:

```python
def _format_custom(self, results: List[SearchResult]) -> None:
    # Custom formatting implementation
    pass
```

## Future Enhancements

### Cloud Storage Integration
- **Google Drive**: OAuth2 authentication, Drive API integration, cached search results
- **iCloud Drive**: Potential integration with iCloud storage (research needed for API availability)
- **Other Cloud Providers**: OneDrive, Dropbox, etc.
- Unified local + cloud search interface
- File download and preview capabilities
- Sync status awareness

### Additional Features
- Search history and bookmarks
- Advanced query syntax (regex, boolean operators)
- Parallel search processing for better performance
- Integration with popular editors and IDEs
- Enhanced web interface with file preview
- Search result filtering and sorting
- Full-text indexing for faster content search
- AI-powered search suggestions



