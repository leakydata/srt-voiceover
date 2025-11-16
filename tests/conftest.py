import textwrap
import sys
from pathlib import Path

import pytest
from pydub import AudioSegment

# Ensure the src/ directory is importable when tests run without installation.
PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = PROJECT_ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))


@pytest.fixture
def sample_srt(tmp_path: Path) -> Path:
    """Create a simple SRT file for tests."""
    content = textwrap.dedent(
        """\
        1
        00:00:00,000 --> 00:00:02,000
        Nathan: Hello world!

        2
        00:00:02,000 --> 00:00:05,000
        Narrator: This is a test.
        """
    )
    srt_path = tmp_path / "sample.srt"
    srt_path.write_text(content, encoding="utf-8")
    return srt_path


@pytest.fixture
def silent_segment() -> AudioSegment:
    """Return a short silent AudioSegment (generated fully in memory)."""
    return AudioSegment.silent(duration=500)

