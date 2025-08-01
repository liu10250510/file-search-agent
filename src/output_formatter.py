import sys
from typing import List, Iterator
from datetime import datetime
import json
import csv

from .searchers import SearchResult

class OutputFormatter:
    """Simple output formatter for search results"""
    
    def __init__(self):
        pass
    
    def format_results(self, 
                      results: Iterator[SearchResult], 
                      format_type: str = 'table',
                      max_results: int = 100,
                      show_size: bool = True,
                      show_modified_time: bool = True,
                      show_file_type: bool = True) -> None:
        """Format and display search results"""
        
        # Convert iterator to list for counting
        results_list = list(results)
        
        if not results_list:
            print("No files found matching the search criteria.")
            return
        
        # Limit results
        if len(results_list) > max_results:
            print(f"Showing first {max_results} of {len(results_list)} results")
            results_list = results_list[:max_results]
        
        if format_type == 'table':
            self._format_table(results_list, show_size, show_modified_time, show_file_type)
        elif format_type == 'json':
            self._format_json(results_list)
        elif format_type == 'csv':
            self._format_csv(results_list, show_size, show_modified_time, show_file_type)
        else:
            raise ValueError(f"Unsupported format type: {format_type}")
    
    def _format_table(self, 
                     results: List[SearchResult], 
                     show_size: bool,
                     show_modified_time: bool,
                     show_file_type: bool) -> None:
        """Format results as a simple text table"""
        # Print header
        headers = ["Name", "Path"]
        if show_size:
            headers.append("Size")
        if show_modified_time:
            headers.append("Modified")
        if show_file_type:
            headers.append("Type")
        
        print(" | ".join(headers))
        print("-" * (sum(len(h) for h in headers) + len(headers) * 3))
        
        for result in results:
            row = [result.name, result.path]
            
            if show_size:
                row.append(self._format_size(result.size))
            if show_modified_time:
                row.append(self._format_time(result.modified_time))
            if show_file_type:
                row.append(result.file_type)
            
            print(" | ".join(row))
            
            # Show content matches if available
            if result.matches:
                matches_text = "\n".join(result.matches[:3])  # Show first 3 matches
                if len(result.matches) > 3:
                    matches_text += f"\n... and {len(result.matches) - 3} more"
                print(f"  Matches:\n{matches_text}")
        
        print(f"\nTotal: {len(results)} files")
    
    def _format_json(self, results: List[SearchResult]) -> None:
        """Format results as JSON"""
        json_data = {
            'total': len(results),
            'results': [result.to_dict() for result in results]
        }
        print(json.dumps(json_data, indent=2))
    
    def _format_csv(self, 
                   results: List[SearchResult],
                   show_size: bool,
                   show_modified_time: bool,
                   show_file_type: bool) -> None:
        """Format results as CSV"""
        import io
        
        output = io.StringIO()
        writer = csv.writer(output)
        
        # Header
        header = ['Name', 'Path']
        if show_size:
            header.append('Size')
        if show_modified_time:
            header.append('Modified')
        if show_file_type:
            header.append('Type')
        header.append('Matches')
        
        writer.writerow(header)
        
        # Data rows
        for result in results:
            row = [result.name, result.path]
            
            if show_size:
                row.append(result.size)
            if show_modified_time:
                row.append(datetime.fromtimestamp(result.modified_time).isoformat())
            if show_file_type:
                row.append(result.file_type)
            
            row.append('; '.join(result.matches) if result.matches else '')
            
            writer.writerow(row)
        
        print(output.getvalue())
    
    def _format_size(self, size: int) -> str:
        """Format file size in human readable format"""
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if size < 1024.0:
                return f"{size:.1f} {unit}"
            size /= 1024.0
        return f"{size:.1f} PB"
    
    def _format_time(self, timestamp: float) -> str:
        """Format timestamp in human readable format"""
        dt = datetime.fromtimestamp(timestamp)
        return dt.strftime("%Y-%m-%d %H:%M")
    
    def show_progress(self, description: str = "Searching..."):
        """Show a simple progress message"""
        return SimpleProgressContext(description)
    
    def print_error(self, message: str) -> None:
        """Print an error message"""
        print(f"Error: {message}")
    
    def print_warning(self, message: str) -> None:
        """Print a warning message"""
        print(f"Warning: {message}")
    
    def print_info(self, message: str) -> None:
        """Print an info message"""
        print(f"Info: {message}")

class SimpleProgressContext:
    """Simple progress context manager"""
    
    def __init__(self, description: str):
        self.description = description
    
    def __enter__(self):
        print(self.description)
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        pass
