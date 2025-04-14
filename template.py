import os
import logging
from pathlib import Path

logging.basicConfig(level=logging.INFO)

project_name = "llm_model_calculator"

list_of_files = [
    f"src/{project_name}/__init__.py",

    # App (UI and controller)
    f"src/{project_name}/app/__init__.py",
    f"src/{project_name}/app/ui.py",
    f"src/{project_name}/app/controller.py",
    f"src/{project_name}/app/main.py",

    # Services (core logic)
    f"src/{project_name}/services/__init__.py",
    f"src/{project_name}/services/price_scraper.py",
    f"src/{project_name}/services/calculator.py",
    f"src/{project_name}/services/model_data.py",

    # Data (storage)
    f"src/{project_name}/data/latest_prices.json",

    # Tests
    f"src/{project_name}/tests/__init__.py",
    f"src/{project_name}/tests/test_calculator.py",
    f"src/{project_name}/tests/test_scraper.py",
    f"src/{project_name}/tests/test_ui.py",

    # Root-level files
    "requirements.txt",
    "README.md",
    ".env",
]

for filepath in list_of_files:
    filepath = Path(filepath)
    filedir, filename = os.path.split(filepath)

    if filedir != "":
        os.makedirs(filedir, exist_ok=True)
        logging.info(f"Creating directory: {filedir} for file: {filename}")

    if (not os.path.exists(filepath)) or (os.path.getsize(filepath) == 0):
        with open(filepath, 'w') as f:
            if filepath.suffix == ".py":
                f.write("# Python module\n")
            elif filepath.name == "latest_prices.json":
                f.write("{}") 
            logging.info(f"Creating empty file: {filepath}")
    else:
        logging.info(f"File already exists: {filepath}")
