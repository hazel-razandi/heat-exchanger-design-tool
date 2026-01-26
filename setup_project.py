import os

# Define the folder structure
structure = {
    "docs": ["architecture.md"],
    "src": ["__init__.py"],
    "src/core": ["__init__.py", "segmental_solver.py", "correlations.py", "properties.py"],
    "src/mechanical": ["__init__.py", "vibration.py", "api_660.py", "clearances.py"],
    "src/business": ["__init__.py", "tema_exporter.py", "quote_generator.py", "costing.py"],
    "src/data": ["__init__.py", "materials.py", "standards.py"],
    "src/platform": ["__init__.py", "auth.py", "project_db.py", "unit_converter.py"],
}

# Define content for specific files
file_contents = {
    "requirements.txt": """streamlit>=1.30.0
numpy>=1.24.0
pandas>=2.0.0
plotly>=5.18.0
CoolProp>=6.5.0
matplotlib>=3.8.0
XlsxWriter>=3.1.0
fpdf>=1.7.2
""",
    ".gitignore": """# Python
__pycache__/
*.pyc
*.pyo
*.pyd
.Python
env/
venv/
.env

# Data Stores
*.json
*.db
user_projects.json
projects/

# OS
.DS_Store
Thumbs.db
""",
    "README.md": """# ExchangerAI Enterprise (v6.0)
### The Intelligent Design Suite for Process Fabrication

![Status](https://img.shields.io/badge/Status-Active_Development-brightgreen)
![Version](https://img.shields.io/badge/Version-6.0_Enterprise-blue)

## 🏭 Overview
ExchangerAI is a defensible, industry-grade SaaS platform for the thermal design, mechanical validation, and commercial quoting of Shell & Tube heat exchangers. 

## 🚀 Key Features
1. **Engineering Truth:** 10-Zone Segmental Solver with NIST properties.
2. **Mechanical Safety:** Vibration analysis and API 660 erosion checks.
3. **Auto-Pilot:** Generative design optimization.
4. **Commercial Output:** TEMA Datasheets and PDF Quotes.
5. **SaaS Workflow:** Project Hub with Metric/Imperial toggles.

## 📦 Installation
1. `pip install -r requirements.txt`
2. `streamlit run app.py`
"""
}

def create_structure():
    base_dir = os.getcwd()
    print(f"🚀 Initializing ExchangerAI Structure in: {base_dir}")

    # 1. Create Directories and Empty Files
    for folder, files in structure.items():
        path = os.path.join(base_dir, folder)
        os.makedirs(path, exist_ok=True)
        print(f"   📂 Created: {folder}/")
        
        for file in files:
            file_path = os.path.join(path, file)
            if not os.path.exists(file_path):
                with open(file_path, 'w') as f:
                    f.write(f'"""\nModule: {file}\nExchangerAI Enterprise v6.0\n"""\n')
                print(f"      📄 Created: {file}")

    # 2. Create Root Files (app.py, README, etc.)
    root_files = ["app.py", "LICENSE"]
    for rf in root_files:
        if not os.path.exists(rf):
            with open(rf, 'w') as f:
                f.write("")
            print(f"   📄 Created Root File: {rf}")

    # 3. Populate Specific Files
    for filename, content in file_contents.items():
        with open(filename, 'w') as f:
            f.write(content)
        print(f"   📝 Populated: {filename}")

    print("\n✅ Setup Complete! You can now delete this script.")

if __name__ == "__main__":
    create_structure()
