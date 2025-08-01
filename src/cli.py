#!/usr/bin/env python3
"""
File Search Agent CLI
A command-line tool for searching files on local machine and Google Drive
"""

import click
import logging
import sys
from pathlib import Path

from .searchers import LocalFileSearcher
from .config import Config
from .output_formatter import OutputFormatter

# Set up logging
logging.basicConfig(
    level=logging.WARNING,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

@click.group()
@click.option('--verbose', '-v', is_flag=True, help='Enable verbose output')
@click.option('--config', '-c', type=click.Path(), help='Path to config file')
@click.pass_context
def cli(ctx, verbose, config):
    """File Search Agent - Search files on local machine and Google Drive"""
    if verbose:
        logging.getLogger().setLevel(logging.INFO)
    
    # Initialize context
    ctx.ensure_object(dict)
    ctx.obj['config'] = Config(config)
    ctx.obj['formatter'] = OutputFormatter()

@cli.command()
@click.argument('pattern')
@click.argument('search_path', default='.')
@click.option('--case-sensitive', is_flag=True, help='Case sensitive search')
@click.option('--include-hidden', is_flag=True, help='Include hidden files')
@click.option('--max-depth', type=int, help='Maximum directory depth to search')
@click.option('--include', multiple=True, help='Include file patterns (e.g., *.py)')
@click.option('--exclude', multiple=True, help='Exclude file patterns (e.g., *.log)')
@click.option('--exclude-path', multiple=True, help='Exclude path patterns (e.g., */build/*, */venv/*)')
@click.option('--format', 'output_format', type=click.Choice(['table', 'json', 'csv']), 
              default='table', help='Output format')
@click.option('--max-results', type=int, default=100, help='Maximum number of results')
@click.pass_context
def name(ctx, pattern, search_path, case_sensitive, include_hidden, max_depth, 
         include, exclude, exclude_path, output_format, max_results):
    """Search files by name pattern"""
    config = ctx.obj['config']
    formatter = ctx.obj['formatter']
    
    # Get configuration
    search_config = config.get_search_config()
    output_config = config.get_output_config()
    
    # Override config with CLI options
    include_hidden = include_hidden or search_config.get('include_hidden', False)
    max_depth = max_depth or search_config.get('max_depth')
    
    exclude_patterns = list(exclude) if exclude else search_config.get('exclude_patterns', [])
    include_patterns = list(include) if include else search_config.get('include_patterns', [])
    exclude_paths = list(exclude_path) if exclude_path else search_config.get('exclude_paths', [])
    
    # Initialize searcher
    searcher = LocalFileSearcher(
        include_hidden=include_hidden,
        max_depth=max_depth,
        include_patterns=include_patterns,
        exclude_patterns=exclude_patterns,
        exclude_paths=exclude_paths
    )
    
    try:
        with formatter.show_progress("Searching files by name..."):
            results = searcher.search_by_name(
                search_path=search_path,
                pattern=pattern,
                case_sensitive=case_sensitive
            )
        
        formatter.format_results(
            results=results,
            format_type=output_format,
            max_results=max_results,
            show_size=output_config.get('show_size', True),
            show_modified_time=output_config.get('show_modified_time', True),
            show_file_type=output_config.get('show_file_type', True)
        )
    
    except FileNotFoundError as e:
        formatter.print_error(str(e))
        sys.exit(1)
    except Exception as e:
        formatter.print_error(f"Search failed: {e}")
        if ctx.obj['config'].get('verbose', False):
            import traceback
            traceback.print_exc()
        sys.exit(1)

@cli.command()
@click.argument('pattern')
@click.argument('search_path', default='.')
@click.option('--case-sensitive', is_flag=True, help='Case sensitive search')
@click.option('--include-hidden', is_flag=True, help='Include hidden files')
@click.option('--max-depth', type=int, help='Maximum directory depth to search')
@click.option('--file-pattern', multiple=True, help='File patterns to search in (e.g., *.py)')
@click.option('--exclude', multiple=True, help='Exclude file patterns (e.g., *.log)')
@click.option('--exclude-path', multiple=True, help='Exclude path patterns (e.g., */build/*, */venv/*)')
@click.option('--format', 'output_format', type=click.Choice(['table', 'json', 'csv']), 
              default='table', help='Output format')
@click.option('--max-results', type=int, default=100, help='Maximum number of results')
@click.pass_context
def content(ctx, pattern, search_path, case_sensitive, include_hidden, max_depth, 
           file_pattern, exclude, exclude_path, output_format, max_results):
    """Search files by content"""
    config = ctx.obj['config']
    formatter = ctx.obj['formatter']
    
    # Get configuration
    search_config = config.get_search_config()
    output_config = config.get_output_config()
    
    # Override config with CLI options
    include_hidden = include_hidden or search_config.get('include_hidden', False)
    max_depth = max_depth or search_config.get('max_depth')
    
    exclude_patterns = list(exclude) if exclude else search_config.get('exclude_patterns', [])
    exclude_paths = list(exclude_path) if exclude_path else search_config.get('exclude_paths', [])
    file_patterns = list(file_pattern) if file_pattern else search_config.get('content_search_patterns', [])
    
    # Initialize searcher
    searcher = LocalFileSearcher(
        include_hidden=include_hidden,
        max_depth=max_depth,
        exclude_patterns=exclude_patterns,
        exclude_paths=exclude_paths
    )
    
    try:
        with formatter.show_progress("Searching files by content..."):
            results = searcher.search_by_content(
                search_path=search_path,
                pattern=pattern,
                file_patterns=file_patterns,
                case_sensitive=case_sensitive
            )
        
        formatter.format_results(
            results=results,
            format_type=output_format,
            max_results=max_results,
            show_size=output_config.get('show_size', True),
            show_modified_time=output_config.get('show_modified_time', True),
            show_file_type=output_config.get('show_file_type', True)
        )
    
    except FileNotFoundError as e:
        formatter.print_error(str(e))
        sys.exit(1)
    except Exception as e:
        formatter.print_error(f"Search failed: {e}")
        if ctx.obj['config'].get('verbose', False):
            import traceback
            traceback.print_exc()
        sys.exit(1)

@cli.command()
@click.argument('search_path', default='.')
@click.option('--min-size', type=str, help='Minimum file size (e.g., 1MB, 500KB)')
@click.option('--max-size', type=str, help='Maximum file size (e.g., 10MB, 2GB)')
@click.option('--include-hidden', is_flag=True, help='Include hidden files')
@click.option('--max-depth', type=int, help='Maximum directory depth to search')
@click.option('--include', multiple=True, help='Include file patterns (e.g., *.py)')
@click.option('--exclude', multiple=True, help='Exclude file patterns (e.g., *.log)')
@click.option('--exclude-path', multiple=True, help='Exclude path patterns (e.g., */build/*, */venv/*)')
@click.option('--format', 'output_format', type=click.Choice(['table', 'json', 'csv']), 
              default='table', help='Output format')
@click.option('--max-results', type=int, default=100, help='Maximum number of results')
@click.pass_context
def size(ctx, search_path, min_size, max_size, include_hidden, max_depth, 
         include, exclude, exclude_path, output_format, max_results):
    """Search files by size"""
    config = ctx.obj['config']
    formatter = ctx.obj['formatter']
    
    # Get configuration
    search_config = config.get_search_config()
    output_config = config.get_output_config()
    
    # Override config with CLI options
    include_hidden = include_hidden or search_config.get('include_hidden', False)
    max_depth = max_depth or search_config.get('max_depth')
    
    exclude_patterns = list(exclude) if exclude else search_config.get('exclude_patterns', [])
    include_patterns = list(include) if include else search_config.get('include_patterns', [])
    
    # Parse size strings
    min_size_bytes = _parse_size(min_size) if min_size else None
    max_size_bytes = _parse_size(max_size) if max_size else None
    
    exclude_paths = list(exclude_path) if exclude_path else search_config.get('exclude_paths', [])
    
    # Initialize searcher
    searcher = LocalFileSearcher(
        include_hidden=include_hidden,
        max_depth=max_depth,
        include_patterns=include_patterns,
        exclude_patterns=exclude_patterns,
        exclude_paths=exclude_paths
    )
    
    try:
        with formatter.show_progress("Searching files by size..."):
            results = searcher.search_by_size(
                search_path=search_path,
                min_size=min_size_bytes,
                max_size=max_size_bytes
            )
        
        formatter.format_results(
            results=results,
            format_type=output_format,
            max_results=max_results,
            show_size=output_config.get('show_size', True),
            show_modified_time=output_config.get('show_modified_time', True),
            show_file_type=output_config.get('show_file_type', True)
        )
    
    except FileNotFoundError as e:
        formatter.print_error(str(e))
        sys.exit(1)
    except Exception as e:
        formatter.print_error(f"Search failed: {e}")
        if ctx.obj['config'].get('verbose', False):
            import traceback
            traceback.print_exc()
        sys.exit(1)

@cli.command()
@click.pass_context
def config_show(ctx):
    """Show current configuration"""
    config = ctx.obj['config']
    formatter = ctx.obj['formatter']
    
    # Handle different formatter types - now unified
    if formatter.rich_enabled:
        formatter.console.print_json(data=config._config)
    else:
        import json
        print(json.dumps(config._config, indent=2))

@cli.command()
@click.argument('key')
@click.argument('value')
@click.pass_context
def config_set(ctx, key, value):
    """Set configuration value"""
    config = ctx.obj['config']
    formatter = ctx.obj['formatter']
    
    # Try to parse value as JSON first
    try:
        import json
        parsed_value = json.loads(value)
    except json.JSONDecodeError:
        # If not JSON, treat as string
        parsed_value = value
    
    config.set(key, parsed_value)
    formatter.print_info(f"Set {key} = {parsed_value}")

def _parse_size(size_str: str) -> int:
    """Parse size string like '1MB', '500KB' to bytes"""
    size_str = size_str.upper().strip()
    
    multipliers = {
        'B': 1,
        'K': 1024, 'KB': 1024,
        'M': 1024**2, 'MB': 1024**2,
        'G': 1024**3, 'GB': 1024**3,
        'T': 1024**4, 'TB': 1024**4,
    }
    
    for suffix, multiplier in multipliers.items():
        if size_str.endswith(suffix):
            number_part = size_str[:-len(suffix)]
            try:
                return int(float(number_part) * multiplier)
            except ValueError:
                raise ValueError(f"Invalid size format: {size_str}")
    
    # If no suffix, assume bytes
    try:
        return int(size_str)
    except ValueError:
        raise ValueError(f"Invalid size format: {size_str}")

if __name__ == '__main__':
    cli()
