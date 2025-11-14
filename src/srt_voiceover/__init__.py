"""
srt-voiceover: Convert SRT subtitle files to synchronized voiceover audio,
or transcribe audio to SRT with speaker detection
"""

__version__ = "0.2.0"
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

from .transcribe import (
    transcribe_audio_to_srt,
    audio_to_voiceover_workflow,
    extract_audio_from_video,
    convert_audio_format,
)

__all__ = [
    # Core voiceover functions
    "build_voiceover_from_srt",
    "srt_time_to_milliseconds",
    "parse_speaker_and_text",
    "get_voice_for_speaker",
    "synthesize_speech_segment",
    "align_segment_duration",
    # Transcription functions
    "transcribe_audio_to_srt",
    "audio_to_voiceover_workflow",
    "extract_audio_from_video",
    "convert_audio_format",
]

