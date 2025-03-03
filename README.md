# MarkUpNote
"A note that converts images into a markup language." 

# System Requirements
- Windows 10 or later
- Python 3.8 or later
- Microsoft Visual C++ Redistributable 2015-2022 (x64)
  - Download: https://aka.ms/vs/17/release/vc_redist.x64.exe
  - Or install via winget: `winget install Microsoft.VCRedist.2015+.x64`

# How to Launch
1. Install system requirements (see above)
2. Install Python dependencies:
```
python3.12 -m venv .venv
./.venv/Scripts/activate
pip install -r requirements.txt
```
3. Run the application:
```
set PYTHONPATH=.
python src/main.py
```

## Installation and Setup

### 1. Installation Dependencies
```bash
pip install -r requirements.txt
```

### 2. Setting up Hugging Face Token
1. Generate a new token at https://huggingface.co/settings/tokens
2. Create a `util/access_token/token` file and paste your token:
   ```bash
   # Windows
   mkdir -p util/access_token
   echo "your-token-here" > util/access_token/token
   
   # Linux/Mac
   mkdir -p util/access_token
   echo "your-token-here" > util/access_token/token
   ```
3. This file is included in .gitignore to prevent accidental exposure.
