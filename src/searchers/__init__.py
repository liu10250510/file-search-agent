from .base_searcher import BaseSearcher, SearchResult
from .local_searcher import LocalFileSearcher

# Try to import AI searcher, but make it optional
try:
    from .ai_searcher import AIFileSearcher
    AI_SEARCHER_AVAILABLE = True
except ImportError:
    AIFileSearcher = None
    AI_SEARCHER_AVAILABLE = False

__all__ = ['BaseSearcher', 'SearchResult', 'LocalFileSearcher']

if AI_SEARCHER_AVAILABLE:
    __all__.append('AIFileSearcher')
