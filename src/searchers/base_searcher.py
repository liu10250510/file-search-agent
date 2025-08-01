from abc import ABC, abstractmethod
from typing import Generator, List, Dict, Any
from dataclasses import dataclass

@dataclass
class SearchResult:
    """Base search result class"""
    path: str
    name: str
    size: int
    modified_time: float
    file_type: str
    matches: List[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'path': self.path,
            'name': self.name,
            'size': self.size,
            'modified_time': self.modified_time,
            'file_type': self.file_type,
            'matches': self.matches or []
        }

class BaseSearcher(ABC):
    """Abstract base class for all searchers"""
    
    @abstractmethod
    def search_by_name(self, search_path: str, pattern: str, **kwargs) -> Generator[SearchResult, None, None]:
        """Search by filename pattern"""
        pass
    
    @abstractmethod
    def search_by_content(self, search_path: str, pattern: str, **kwargs) -> Generator[SearchResult, None, None]:
        """Search by file content"""
        pass
    
    @abstractmethod
    def search_by_size(self, search_path: str, min_size: int = None, max_size: int = None, **kwargs) -> Generator[SearchResult, None, None]:
        """Search by file size"""
        pass
