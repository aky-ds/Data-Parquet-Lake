from pathlib import Path
import os

list_of_files = [
    "app.py",
    "requirements.txt",
    "setup.py",
    "tests/__init__.py",
    "tests/test_pipeline.py",
    "README.md",
    "config/schema.yaml",
    "src/__init__.py",
    "src/ingestion.py",
    "src/config.py",
    "src/transform.py",
    "src/validation.py",
    "src/pipeline.py",
    "src/exporters.py"
]

for filepath in list_of_files:
    file_path = Path(filepath)
    file_dir, file_name = os.path.split(file_path)
    
    # Create directory if it doesn't exist
    if file_dir != "":
        os.makedirs(file_dir, exist_ok=True)
        
    # Create the file if it doesn't exist or is empty
    if not file_path.exists() or file_path.stat().st_size == 0:
        with open(file_path, "w") as f:
            pass
        print(f"Created: {file_path}")
    else:
        print(f"Skipped (already exists): {file_path}")