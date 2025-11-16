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
- **Sample SRT file or audio** (if applicable)
- **Error messages and stack traces**

### Suggesting Enhancements

Enhancement suggestions are tracked as GitHub issues. When creating an enhancement suggestion, include:

- **Clear use case and problem statement**
- **Current behavior and proposed behavior**
- **Why this enhancement would be useful**
- **Potential implementation approach** (optional)

### Pull Requests

1. **Fork** the repository
2. **Create a branch** from `main`:
   ```bash
   git checkout -b feature/your-feature-name
   ```
3. **Make your changes**
4. **Test your changes** thoroughly
5. **Update documentation** if needed (README.md, DOCUMENTATION.md, etc.)
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

### Prerequisites

- Python 3.7+
- FFmpeg installed and in PATH
- Git

### Setup Steps

1. **Clone your fork:**
   ```bash
   git clone https://github.com/YOUR_USERNAME/srt-voiceover.git
   cd srt-voiceover
   ```

2. **Create a virtual environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install in development mode:**
   ```bash
   # Install all features for development
   pip install -e .[all]
   ```

4. **Verify installation:**
   ```bash
   # Test basic functionality
   srt-voiceover --version
   srt-voiceover --list-voices | head -10
   ```

## Project Structure

```
srt-voiceover/
├── src/
│   └── srt_voiceover/
│       ├── __init__.py      # Package initialization
│       ├── core.py          # Core voiceover generation
│       ├── transcribe.py    # Audio transcription and workflows
│       └── cli.py           # Command-line interface
├── examples/
│   └── config.yaml          # Example configuration
├── tests/                   # (Future) Test files
├── pyproject.toml           # Package configuration
├── setup.py                 # Setup script
├── requirements.txt         # Core dependencies
├── README.md                # Main entry point
├── QUICKSTART.md            # Quick start guide
├── DOCUMENTATION.md         # Complete documentation
└── CONTRIBUTING.md          # This file
```

## Coding Standards

### Python Style

- **Python 3.7+** compatible code
- **PEP 8** style guide (max line length: 100 characters)
- **Type hints** where appropriate
- **Docstrings** for all public functions/classes (Google style)
- **Clear, descriptive variable names**

### Example Function

```python
from typing import Optional, Tuple

def parse_speaker_and_text(raw_text: str) -> Tuple[Optional[str], str]:
    """
    Extract speaker name and text from subtitle content.
    
    Args:
        raw_text: Raw subtitle text with optional speaker prefix (e.g., "Nathan: Hello")
        
    Returns:
        Tuple of (speaker_name, cleaned_text). speaker_name is None if no speaker found.
        
    Example:
        >>> parse_speaker_and_text("Nathan: Hello world")
        ("Nathan", "Hello world")
        >>> parse_speaker_and_text("Hello world")
        (None, "Hello world")
    """
    if ':' in raw_text:
        parts = raw_text.split(':', 1)
        speaker = parts[0].strip()
        text = parts[1].strip()
        return speaker, text
    return None, raw_text.strip()
```

### Code Organization

- Keep functions focused and single-purpose
- Extract complex logic into separate functions
- Use meaningful names (avoid single-letter variables except in loops)
- Add comments for non-obvious logic
- Group related functionality together

## Testing

### Manual Testing

Test your changes with real files:

```bash
# Test voiceover generation
srt-voiceover voiceover examples/sample.srt -o test.mp3

# Test transcription
srt-voiceover transcribe test_audio.mp3 -o test.srt

# Test complete workflow
srt-voiceover revoice test_video.mp4 -o test_output.mp3 --use-word-timing
```

### Future: Automated Testing

We welcome contributions to add:
- Unit tests with pytest
- Integration tests
- CI/CD pipeline
- Test fixtures and sample files

## Documentation

When adding features, update:

1. **Docstrings** - Add/update function docstrings
2. **DOCUMENTATION.md** - Add detailed usage examples
3. **README.md** - Update if it affects quick start
4. **QUICKSTART.md** - Add to quick examples if relevant
5. **CLI help** - Update argument help text

## Areas Needing Help

We'd love contributions in these areas:

### High Priority
- **Testing framework** - pytest setup with fixtures
- **Error handling** - Better error messages and recovery
- **Performance optimization** - Async processing, parallel TTS
- **Memory management** - Optimize for large files

### Features
- **Voice preview** - Tool to test voices quickly
- **Batch processing** - Process multiple files efficiently
- **GUI/Web UI** - Simple interface for non-technical users
- **Additional TTS engines** - Google Cloud, AWS Polly integration
- **Voice cloning** - Integration with voice cloning services

### Documentation
- **Video tutorials** - YouTube guide showing features
- **More examples** - Real-world use cases
- **Translations** - README in other languages
- **Troubleshooting guide** - Common issues and solutions

### Quality
- **Code coverage** - Achieve >80% test coverage
- **Type hints** - Full mypy compatibility
- **Linting** - Setup pre-commit hooks
- **Performance benchmarks** - Track processing speed

## Development Workflow

### Adding a New Feature

1. **Create an issue** first to discuss the feature
2. **Wait for approval** before starting work
3. **Create a branch** from main
4. **Develop with tests** (if applicable)
5. **Update documentation**
6. **Submit PR** with clear description and examples

### Bug Fix Workflow

1. **Confirm the bug** - Reproduce it
2. **Create issue** if none exists
3. **Create branch** - `fix/bug-description`
4. **Fix and test**
5. **Add regression test** (if possible)
6. **Submit PR** referencing the issue

## Release Process

(For maintainers)

1. Update version in `pyproject.toml` and `__init__.py`
2. Update CHANGELOG (if we add one)
3. Create release on GitHub with notes
4. Build and publish to PyPI

## Getting Help

- **Questions?** Open an issue with `question` label
- **Discussions** Use GitHub Discussions for ideas
- **Chat** (if we add Discord/Slack in the future)

## Recognition

Contributors are recognized in:
- GitHub contributors page
- README acknowledgments (for significant contributions)
- Release notes

## License

By contributing, you agree that your contributions will be licensed under the MIT License.

---

Thank you for contributing to srt-voiceover! 🎉

Your work helps make high-quality voiceovers accessible to everyone.
