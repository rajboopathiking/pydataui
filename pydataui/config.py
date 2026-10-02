import os
import secrets
from typing import List, Optional, Any, Dict

class AppConfig:
    """Application configuration for PyDataUI."""
    
    title: str = 'PyDataUI App'
    description: str = ''
    version: str = '0.1.0'
    debug: bool = False
    host: str = '127.0.0.1'
    port: int = 8000
    reload: bool = False
    session_secret: str = secrets.token_hex(32)
    session_max_age: int = 3600  # seconds
    api_prefix: str = '/api'
    internal_prefix: str = '/_pdu'
    theme: str = 'default'
    cors_origins: List[str] = ['*']
    static_dir: Optional[str] = None
    
    def __init__(self, **kwargs: Any):
        # Load from defaults
        self._load_from_env()
        # Override with kwargs
        for k, v in kwargs.items():
            if hasattr(self, k):
                setattr(self, k, v)
                
    def _load_from_env(self) -> None:
        """Load configuration from environment variables prefixed with PYDATAUI_."""
        for key in dir(self):
            if not key.startswith('_') and not callable(getattr(self, key)):
                env_key = f"PYDATAUI_{key.upper()}"
                if env_key in os.environ:
                    val = os.environ[env_key]
                    # Attempt simple type casting based on current type
                    current_val = getattr(self, key)
                    if isinstance(current_val, bool):
                        setattr(self, key, val.lower() in ('true', '1', 'yes'))
                    elif isinstance(current_val, int):
                        setattr(self, key, int(val))
                    else:
                        setattr(self, key, val)
    
    def load_from_dict(self, config_dict: Dict[str, Any]) -> None:
        """Load configuration from a dictionary."""
        for k, v in config_dict.items():
            if hasattr(self, k):
                setattr(self, k, v)
                
    def load_from_toml(self, filepath: str) -> None:
        """Load configuration from a TOML file (requires tomli/tomllib)."""
        try:
            import tomllib
        except ImportError:
            try:
                import tomli as tomllib
            except ImportError:
                return
        if os.path.exists(filepath):
            with open(filepath, 'rb') as f:
                data = tomllib.load(f)
                if 'pydataui' in data:
                    self.load_from_dict(data['pydataui'])
