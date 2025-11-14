"""
srt-voiceover: Convert SRT subtitle files to synchronized voiceover audio
"""

__version__ = "0.1.0"
__author__ = "Nathan Jones"
__license__ = "MIT"

from .core import (
    build_voiceover_from_srt,
    srt_time_to_milliseconds,
    parse_speaker_and_text,
    get_voice_for_speaker,
    synthesize_speech_segment,
    align_segment_duration,
)

__all__ = [
    "build_voiceover_from_srt",
    "srt_time_to_milliseconds",
    "parse_speaker_and_text",
    "get_voice_for_speaker",
    "synthesize_speech_segment",
    "align_segment_duration",
]

