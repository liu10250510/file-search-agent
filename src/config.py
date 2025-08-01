import json
import os
from pathlib import Path
from typing import Dict, Any, List

class Config:
    """Configuration management for the file search agent"""
    
    DEFAULT_CONFIG = {
        'search': {
            'include_hidden': False,
            'max_depth': None,
            'case_sensitive': False,
            'exclude_patterns': [
                '*.pyc', '__pycache__', '.git', '.svn', 
                'node_modules', '.DS_Store', 'Thumbs.db',
                '*.log', '*.tmp'
            ],
            'exclude_paths': [
                '*/.git/*', '*/__pycache__/*', '*/node_modules/*',
                '*/.vscode/*', '*/.idea/*', '*/build/*', '*/dist/*',
                '*/.pytest_cache/*', '*/.coverage/*',
                '/Users/lucy/Library', '**/venv/**', '**/.env/**'
            ],
            'include_patterns': [],
            'content_search_patterns': [
                '*.txt', '*.py', '*.js', '*.html', '*.css', 
                '*.md', '*.json', '*.xml', '*.yaml', '*.yml'
            ]
        },
        'output': {
            'format': 'table',  # table, json, csv
            'max_results': 100,
            'show_size': True,
            'show_modified_time': True,
            'show_file_type': True
        },
        'google_drive': {
            'enabled': False,
            'credentials_path': None,
            'cache_enabled': True,
            'cache_duration': 3600  # seconds
        }
    }
    
    def __init__(self, config_path: str = None):
        if config_path is None:
            config_path = os.path.join(Path.home(), '.file_search_agent', 'config.json')
        
        self.config_path = config_path
        self.config_dir = os.path.dirname(config_path)
        self._config = self.load_config()
    
    def load_config(self) -> Dict[str, Any]:
        """Load configuration from file or create default"""
        if os.path.exists(self.config_path):
            try:
                with open(self.config_path, 'r') as f:
                    user_config = json.load(f)
                    # Merge with defaults
                    config = self.DEFAULT_CONFIG.copy()
                    self._deep_merge(config, user_config)
                    return config
            except (json.JSONDecodeError, IOError) as e:
                print(f"Warning: Could not load config from {self.config_path}: {e}")
        
        # Create default config
        self.save_config(self.DEFAULT_CONFIG)
        return self.DEFAULT_CONFIG.copy()
    
    def save_config(self, config: Dict[str, Any] = None) -> None:
        """Save configuration to file"""
        if config is None:
            config = self._config
        
        # Ensure config directory exists
        os.makedirs(self.config_dir, exist_ok=True)
        
        try:
            with open(self.config_path, 'w') as f:
                json.dump(config, f, indent=2)
        except IOError as e:
            print(f"Warning: Could not save config to {self.config_path}: {e}")
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value using dot notation"""
        keys = key.split('.')
        value = self._config
        
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        
        return value
    
    def set(self, key: str, value: Any) -> None:
        """Set configuration value using dot notation"""
        keys = key.split('.')
        config = self._config
        
        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]
        
        config[keys[-1]] = value
        self.save_config()
    
    def get_search_config(self) -> Dict[str, Any]:
        """Get search-specific configuration"""
        return self._config.get('search', {})
    
    def get_output_config(self) -> Dict[str, Any]:
        """Get output-specific configuration"""
        return self._config.get('output', {})
    
    def get_google_drive_config(self) -> Dict[str, Any]:
        """Get Google Drive-specific configuration"""
        return self._config.get('google_drive', {})
    
    def _deep_merge(self, base: Dict, update: Dict) -> None:
        """Deep merge two dictionaries"""
        for key, value in update.items():
            if key in base and isinstance(base[key], dict) and isinstance(value, dict):
                self._deep_merge(base[key], value)
            else:
                base[key] = value
