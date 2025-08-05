"""Entry point for python -m personalparakeet."""
import os
import json
from pathlib import Path

# Set cache directories before any imports that might use them
def setup_cache_directories():
    """Set up custom cache directories from config before ML imports."""
    config_path = Path.home() / ".personalparakeet" / "config.json"
    if config_path.exists():
        try:
            with open(config_path) as f:
                config = json.load(f)
            cache_dir = config.get("audio", {}).get("model_cache_dir")
            if cache_dir:
                cache_path = Path(cache_dir).expanduser().absolute()
                os.environ['HF_HOME'] = str(cache_path / 'huggingface')
                os.environ['HUGGINGFACE_HUB_CACHE'] = str(cache_path / 'huggingface' / 'hub')
                os.environ['TORCH_HOME'] = str(cache_path / 'torch')
                os.environ['TRANSFORMERS_CACHE'] = str(cache_path / 'transformers')
                print(f"Cache directories set to: {cache_path}")
        except Exception as e:
            print(f"Could not set cache directories: {e}")

setup_cache_directories()

from personalparakeet.main import main

if __name__ == "__main__":
    main()
