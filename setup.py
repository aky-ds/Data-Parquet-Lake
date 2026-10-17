from setuptools import setup, find_packages

def get_requires(file_path: str):
    with open(file_path, "r") as f:
        lines = f.readlines()
        # Clean up whitespace/newlines and ignore empty lines or comments
        requires = [line.strip() for line in lines if line.strip() and not line.startswith("#")]
        
        # Safely remove editable install flag if present
        if "-e ." in requires:
            requires.remove("-e .")
            
    return requires

setup(
    name="csv-cleaner-parquet-data-lake",  # Best practice: lowercase with hyphens
    version="0.1.0",  # Version is mandatory for setuptools
    description="An application to import CSV files, normalize data, validate fields, and export to JSON, CSV, and Parquet.",
    author="Ayaz ul haq yousafzai",
    author_email="syedthescientist@gmail.com",
    packages=find_packages(),  # Corrected from setup_requires
    install_requires=get_requires("requirements.txt")  # Corrected from requires
)