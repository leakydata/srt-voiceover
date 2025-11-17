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

# New advanced features
from .speaker_detection import (
    parse_speaker_and_text_advanced,
    SpeakerContext,
    get_speaker_statistics,
)

from .word_alignment import (
    fuzzy_match_word,
    match_words_to_segment,
    get_timing_strategy,
)

from .voice_profiles import (
    get_voice_profile,
    calculate_segment_rate_with_voice_profile,
    list_available_voices,
)

from .quality import (
    SyncQualityReport,
    SegmentQualityMetrics,
)

from .export import (
    export_word_timings_vtt,
    export_word_timings_srt,
    export_word_timings_json,
    export_word_timings_csv,
    export_word_timings_multi,
)

from .translation import (
    OllamaConfig,
    OllamaConnectionError,
    translate_text,
    translate_srt_segment,
    translate_srt,
    get_available_ollama_models,
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
    # Advanced speaker detection
    "parse_speaker_and_text_advanced",
    "SpeakerContext",
    "get_speaker_statistics",
    # Advanced word alignment
    "fuzzy_match_word",
    "match_words_to_segment",
    "get_timing_strategy",
    # Voice profiles
    "get_voice_profile",
    "calculate_segment_rate_with_voice_profile",
    "list_available_voices",
    # Quality metrics
    "SyncQualityReport",
    "SegmentQualityMetrics",
    # Export functions
    "export_word_timings_vtt",
    "export_word_timings_srt",
    "export_word_timings_json",
    "export_word_timings_csv",
    "export_word_timings_multi",
    # Translation functions
    "OllamaConfig",
    "OllamaConnectionError",
    "translate_text",
    "translate_srt_segment",
    "translate_srt",
    "get_available_ollama_models",
]

