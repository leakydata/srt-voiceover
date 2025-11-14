# Contributing to srt-voiceover

Thank you for considering contributing to srt-voiceover! This document provides guidelines and instructions for contributing.

## Code of Conduct

Be respectful and inclusive. We're all here to make great software together.

## How Can I Contribute?

### Reporting Bugs

Before creating bug reports, please check existing issues to avoid duplicates. When creating a bug report, include:

- **Clear title and description**
- **Steps to reproduce**
- **Expected vs actual behavior**
- **Your environment** (OS, Python version, package versions)
- **Sample SRT file** (if applicable)

### Suggesting Enhancements

Enhancement suggestions are tracked as GitHub issues. When creating an enhancement suggestion, include:

- **Clear use case**
- **Current behavior and proposed behavior**
- **Why this enhancement would be useful**

### Pull Requests

1. **Fork** the repository
2. **Create a branch** from `main`:
   ```bash
   git checkout -b feature/your-feature-name
   ```
3. **Make your changes**
4. **Test your changes** thoroughly
5. **Update documentation** if needed
6. **Commit with clear messages**:
   ```bash
   git commit -m "Add feature: description of what you added"
   ```
7. **Push to your fork**:
   ```bash
   git push origin feature/your-feature-name
   ```
8. **Open a Pull Request** with a clear description

## Development Setup

1. Clone your fork:
   ```bash
   git clone https://github.com/YOUR_USERNAME/srt-voiceover.git
   cd srt-voiceover
   ```

2. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install in development mode:
   ```bash
   pip install -e .
   pip install -r requirements.txt
   ```

4. Set up the Edge TTS server for testing:
   ```bash
   # In a separate terminal
   git clone https://github.com/travisvn/openai-edge-tts.git
   cd openai-edge-tts
   npm install
   npm start
   ```

## Coding Standards

- **Python 3.7+** compatible code
- **PEP 8** style guide (line length 100)
- **Type hints** where appropriate
- **Docstrings** for all public functions/classes
- **Clear variable names**

### Example Function

```python
def parse_speaker_and_text(raw_text: str) -> Tuple[Optional[str], str]:
    """
    Extract speaker name and text from subtitle content.
    
    Args:
        raw_text: Raw subtitle text with optional speaker prefix
        
    Returns:
        Tuple of (speaker_name, cleaned_text)
        
    Example:
        >>> parse_speaker_and_text("Nathan: Hello world")
        ("Nathan", "Hello world")
    """
    # Implementation...
```

## Testing

Currently, testing is manual. Run the CLI with test files:

```bash
srt-voiceover examples/sample.srt -o test_output.mp3 -c examples/config.yaml
```

We welcome contributions to add automated testing!

## Documentation

- Keep the README.md up to date
- Update examples/ if you add new features
- Add docstrings to new functions
- Comment complex logic

## Project Structure

```
srt-voiceover/
├── src/
│   └── srt_voiceover/
│       ├── __init__.py      # Package initialization
│       ├── core.py          # Core conversion logic
│       └── cli.py           # Command-line interface
├── examples/
│   ├── config.yaml          # Example configuration
│   └── sample.srt           # Example SRT file
├── tests/                   # (Future) Test files
├── pyproject.toml           # Package configuration
├── setup.py                 # Setup script
├── requirements.txt         # Dependencies
└── README.md                # Main documentation
```

## Areas Needing Help

- **Testing framework** - Add pytest tests
- **Voice preview** - Tool to preview voices
- **Web UI** - Simple web interface
- **Additional TTS engines** - Support for Google/AWS TTS
- **Performance optimization** - Parallel processing
- **Error handling** - Better error messages
- **Documentation** - Video tutorials, more examples

## Questions?

Feel free to open an issue with the `question` label or start a discussion on GitHub Discussions.

Thank you for contributing! 🎉

