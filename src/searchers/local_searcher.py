import os
import fnmatch
import mimetypes
from pathlib import Path
from typing import List, Dict, Any, Generator, Optional
import logging

from .base_searcher import SearchResult

class LocalFileSearcher:
    """Handles searching for files on the local file system"""
    
    def __init__(self, 
                 include_hidden: bool = False,
                 max_depth: int = None,
                 include_patterns: List[str] = None,
                 exclude_patterns: List[str] = None,
                 exclude_paths: List[str] = None):
        self.include_hidden = include_hidden
        self.max_depth = max_depth
        self.include_patterns = include_patterns or []
        self.exclude_patterns = exclude_patterns or [
            '*.pyc', '__pycache__', '.git', '.svn', 
            'node_modules', '.DS_Store', 'Thumbs.db'
        ]
        # New: Support for excluding specific file paths or path patterns
        self.exclude_paths = exclude_paths or [
            '*/.git/*', '*/__pycache__/*', '*/node_modules/*',
            '*/.vscode/*', '*/.idea/*', '*/build/*', '*/dist/*',
            '*/.pytest_cache/*', '*/.coverage/*', '*/venv/*', '*/env/*',
            '/Users/lucy/Library', '**/venv/**', '**/.venv/**'
        ]
        self.logger = logging.getLogger(__name__)
        self._visited_dirs = set()  # Track visited directories to prevent infinite loops
    
    def search_by_name(self, 
                      search_path: str, 
                      pattern: str, 
                      case_sensitive: bool = False) -> Generator[SearchResult, None, None]:
        """Search files by filename pattern"""
        search_path = Path(search_path).expanduser().resolve()
        
        if not search_path.exists():
            raise FileNotFoundError(f"Search path does not exist: {search_path}")
        
        if not case_sensitive:
            pattern = pattern.lower()
        
        # Reset visited directories for each new search
        self._visited_dirs.clear()
        
        for file_path in self._walk_directory(search_path):
            file_name = file_path.name
            if not case_sensitive:
                file_name = file_name.lower()
            
            if fnmatch.fnmatch(file_name, pattern):
                try:
                    stat = file_path.stat()
                    yield SearchResult(
                        path=str(file_path),
                        name=file_path.name,
                        size=stat.st_size,
                        modified_time=stat.st_mtime,
                        file_type=self._get_file_type(file_path)
                    )
                except (OSError, IOError) as e:
                    self.logger.warning(f"Could not access file {file_path}: {e}")
                    continue
    
    def search_by_content(self, 
                         search_path: str, 
                         pattern: str,
                         file_patterns: List[str] = None,
                         case_sensitive: bool = False,
                         max_file_size: int = 10 * 1024 * 1024) -> Generator[SearchResult, None, None]:  # 10MB default limit
        """Search files by content with performance optimizations"""
        search_path = Path(search_path).expanduser().resolve()
        
        if not search_path.exists():
            raise FileNotFoundError(f"Search path does not exist: {search_path}")
        
        file_patterns = file_patterns or ['*.txt', '*.py', '*.js', '*.html', '*.css', '*.md', '*.json', '*.xml', '*.yml', '*.yaml']
        
        # Reset visited directories for each new search
        self._visited_dirs.clear()
        
        # Prepare search pattern
        search_pattern = pattern.lower() if not case_sensitive else pattern
        
        for file_path in self._walk_directory(search_path):
            # Check if file matches any of the file patterns
            if not any(fnmatch.fnmatch(file_path.name, fp) for fp in file_patterns):
                continue
            
            try:
                # Get file stats first to check size
                stat = file_path.stat()
                
                # Skip very large files to improve performance
                if stat.st_size > max_file_size:
                    self.logger.debug(f"Skipping large file {file_path} ({stat.st_size} bytes)")
                    continue
                
                # Skip empty files
                if stat.st_size == 0:
                    continue
                
                # Try to read the file as text with size limit
                try:
                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                        # Read in chunks for better memory management
                        chunk_size = 8192  # 8KB chunks
                        content_found = False
                        matches = []
                        line_number = 1
                        current_line = ""
                        
                        while True:
                            chunk = f.read(chunk_size)
                            if not chunk:
                                break
                            
                            # Process the chunk line by line
                            lines = (current_line + chunk).split('\n')
                            current_line = lines[-1]  # Save incomplete line for next iteration
                            
                            for line in lines[:-1]:  # Process complete lines
                                line_to_search = line.lower() if not case_sensitive else line
                                if search_pattern in line_to_search:
                                    content_found = True
                                    if len(matches) < 10:  # Limit matches for performance
                                        matches.append(f"Line {line_number}: {line.strip()}")
                                line_number += 1
                            
                            # Early exit if we found matches and don't need more
                            if content_found and len(matches) >= 10:
                                break
                        
                        # Check the last line if there's any remaining content
                        if current_line and not content_found:
                            line_to_search = current_line.lower() if not case_sensitive else current_line
                            if search_pattern in line_to_search:
                                content_found = True
                                if len(matches) < 10:
                                    matches.append(f"Line {line_number}: {current_line.strip()}")
                        
                        if content_found:
                            yield SearchResult(
                                path=str(file_path),
                                name=file_path.name,
                                size=stat.st_size,
                                modified_time=stat.st_mtime,
                                file_type=self._get_file_type(file_path),
                                matches=matches
                            )
                
                except UnicodeDecodeError:
                    # File is likely binary, skip it
                    self.logger.debug(f"Skipping binary file {file_path}")
                    continue
                    
            except (OSError, IOError) as e:
                self.logger.debug(f"Could not read file {file_path}: {e}")
                continue
    
    def search_by_size(self, 
                      search_path: str, 
                      min_size: int = None, 
                      max_size: int = None) -> Generator[SearchResult, None, None]:
        """Search files by size"""
        search_path = Path(search_path).expanduser().resolve()
        
        if not search_path.exists():
            raise FileNotFoundError(f"Search path does not exist: {search_path}")
        
        # Reset visited directories for each new search
        self._visited_dirs.clear()
        
        for file_path in self._walk_directory(search_path):
            try:
                stat = file_path.stat()
                size = stat.st_size
                
                if min_size is not None and size < min_size:
                    continue
                if max_size is not None and size > max_size:
                    continue
                
                yield SearchResult(
                    path=str(file_path),
                    name=file_path.name,
                    size=size,
                    modified_time=stat.st_mtime,
                    file_type=self._get_file_type(file_path)
                )
            except (OSError, IOError) as e:
                self.logger.warning(f"Could not access file {file_path}: {e}")
                continue
    
    def _walk_directory(self, path: Path, current_depth: int = 0) -> Generator[Path, None, None]:
        """Walk through directory tree with protection against infinite loops"""
        if self.max_depth is not None and current_depth > self.max_depth:
            return
        
        # Resolve the path to handle symlinks and get canonical path
        try:
            canonical_path = path.resolve()
        except (OSError, RuntimeError) as e:
            self.logger.warning(f"Could not resolve path {path}: {e}")
            return
        
        # Check if we've already visited this directory (prevents infinite loops from symlinks)
        canonical_str = str(canonical_path)
        if canonical_str in self._visited_dirs:
            return
        
        # Mark this directory as visited
        self._visited_dirs.add(canonical_str)
        
        try:
            for item in path.iterdir():
                # Skip hidden files if not included
                if not self.include_hidden and item.name.startswith('.'):
                    continue
                
                # Check exclude patterns (filename only)
                if any(fnmatch.fnmatch(item.name, pattern) for pattern in self.exclude_patterns):
                    continue
                
                # Check exclude path patterns (full path)
                if self._should_exclude_path(item):
                    continue
                
                if item.is_file():
                    # Check include patterns
                    if self.include_patterns and not any(fnmatch.fnmatch(item.name, pattern) for pattern in self.include_patterns):
                        continue
                    yield item
                elif item.is_dir():
                    # Recursively walk subdirectories
                    yield from self._walk_directory(item, current_depth + 1)
        except (OSError, IOError) as e:
            self.logger.warning(f"Could not access directory {path}: {e}")
        finally:
            # Remove from visited set when we're done with this branch
            # This allows revisiting the same directory from different paths if needed
            self._visited_dirs.discard(canonical_str)
    
    def _get_file_type(self, file_path: Path) -> str:
        """Get file type based on extension"""
        mime_type, _ = mimetypes.guess_type(str(file_path))
        if mime_type:
            return mime_type
        
        suffix = file_path.suffix.lower()
        if suffix:
            return f"file/{suffix[1:]}"  # Remove the dot
        
        return "unknown"
    
    def _should_exclude_path(self, file_path: Path) -> bool:
        """Check if a file path should be excluded based on path patterns"""
        path_str = str(file_path)
        
        # Check against exclude path patterns
        for exclude_pattern in self.exclude_paths:
            if fnmatch.fnmatch(path_str, exclude_pattern):
                return True
        
        return False
