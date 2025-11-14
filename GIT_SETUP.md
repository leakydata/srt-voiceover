# Git Setup Instructions

Follow these steps to push your srt-voiceover package to GitHub.

## Step 1: Review What's Been Created

Your project now has a complete Python package structure:

```
SRTVoice/
├── src/srt_voiceover/          # Main package
│   ├── __init__.py             # Package initialization
│   ├── core.py                 # Core conversion logic
│   └── cli.py                  # Command-line interface
├── examples/                    # Example files
│   ├── config.yaml             # Sample configuration
│   └── sample.srt              # Sample subtitle file
├── .github/                     # GitHub templates
│   └── ISSUE_TEMPLATE/
│       ├── bug_report.md
│       └── feature_request.md
├── .gitignore                   # Files to exclude from Git
├── pyproject.toml              # Package configuration (modern)
├── setup.py                    # Setup script (compatibility)
├── requirements.txt            # Python dependencies
├── MANIFEST.in                 # Package manifest
├── README.md                   # Main documentation
├── QUICKSTART.md               # Quick start guide
├── CONTRIBUTING.md             # Contribution guidelines
├── edgetts_voices_list.md      # List of available voices
└── srt_to_edgtts_voiceover_old.py  # Your original script (kept for reference)
```

## Step 2: Initialize Git Repository

```powershell
# Make sure you're in the project directory
cd "C:\Users\njones\Documents\Python Scripts\SRTVoice"

# Initialize git (if not already done)
git init

# Add all files
git add .

# Check what will be committed (optional)
git status

# Create initial commit
git commit -m "Initial commit: Complete Python package structure for srt-voiceover"
```

## Step 3: Connect to Your GitHub Repository

```powershell
# Add your GitHub repo as remote
git remote add origin https://github.com/leakydata/srt-voiceover.git

# Verify the remote was added
git remote -v

# Set the branch name to main
git branch -M main
```

## Step 4: Push to GitHub

```powershell
# Push your code to GitHub
git push -u origin main
```

If you get an error about the remote having commits (like the LICENSE file), use:

```powershell
# Pull the LICENSE file first
git pull origin main --allow-unrelated-histories

# Then push
git push -u origin main
```

## Step 5: Verify on GitHub

Visit https://github.com/leakydata/srt-voiceover and you should see:
- ✅ All your files
- ✅ Formatted README with badges and documentation
- ✅ Proper package structure
- ✅ Issue templates

## Step 6: Test Installation

To verify the package works:

```powershell
# Create a test environment
cd ..
mkdir test_install
cd test_install
python -m venv venv
venv\Scripts\activate

# Install from local directory
pip install "C:\Users\njones\Documents\Python Scripts\SRTVoice"

# Test the command
srt-voiceover --version
srt-voiceover --init-config test_config.yaml

# Deactivate when done
deactivate
```

## What's Protected by .gitignore

Your .gitignore prevents these from being committed:
- ❌ Generated MP3/WAV files (except examples)
- ❌ Your personal config files (keeps examples)
- ❌ API keys and .env files
- ❌ Python cache files
- ❌ Log files
- ❌ Virtual environments

## Future Updates

When you make changes:

```powershell
# Check what changed
git status

# Add specific files
git add src/srt_voiceover/core.py
git add README.md

# Or add everything
git add .

# Commit with a meaningful message
git commit -m "Add: new feature description"
# or
git commit -m "Fix: bug description"
# or
git commit -m "Update: documentation improvements"

# Push to GitHub
git push
```

## Helpful Git Commands

```powershell
# See commit history
git log --oneline

# See what files changed
git diff

# Undo changes to a file (before commit)
git checkout -- filename

# Create a new branch for features
git checkout -b feature/new-feature

# Switch back to main
git checkout main

# Merge a feature branch
git merge feature/new-feature
```

## Publishing to PyPI (Future)

When ready to publish to PyPI:

```powershell
# Install build tools
pip install build twine

# Build the package
python -m build

# Upload to PyPI (you'll need a PyPI account)
python -m twine upload dist/*
```

## Need Help?

- Git basics: https://git-scm.com/doc
- GitHub guides: https://guides.github.com/
- Python packaging: https://packaging.python.org/

---

**Your repository is ready! 🚀**

After pushing, your package will be available at:
https://github.com/leakydata/srt-voiceover

People can install it with:
```bash
pip install git+https://github.com/leakydata/srt-voiceover.git
```

