""" A configuration file to read the yaml configuration"""
from pathlib import Path
import yaml

DEFAULT_CONFIG=Path("config/schema.yaml")

SUPPORTED_TYPES = {
    "string",
    "int",
    "float",
    "bool",
    "datetime",
}

def load_config(config_path=DEFAULT_CONFIG):
    """Load the YAML configuration."""
    path = Path(config_path)
    print("Data Loaded")

load_config()