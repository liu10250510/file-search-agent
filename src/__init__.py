"""File Search Agent - A tool for searching files locally and on Google Drive"""

from .searchers import LocalFileSearcher, BaseSearcher, SearchResult
from .config import Config
from .output_formatter import OutputFormatter

__version__ = "1.0.0"
__author__ = "File Search Agent"
__email__ = "contact@filesearchagent.com"

__all__ = [
    'LocalFileSearcher', 
    'BaseSearcher', 
    'SearchResult', 
    'Config', 
    'OutputFormatter'
]
