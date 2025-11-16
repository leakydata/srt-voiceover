from pydub import AudioSegment

from srt_voiceover.core import (
    align_segment_duration,
    get_voice_for_speaker,
    parse_speaker_and_text,
    srt_time_to_milliseconds,
)


def test_srt_time_to_milliseconds():
    import pysrt

    time = pysrt.SubRipTime(hours=0, minutes=1, seconds=2, milliseconds=345)
    assert srt_time_to_milliseconds(time) == 62345


def test_parse_speaker_and_text_with_label():
    speaker, text = parse_speaker_and_text("Nicole: Hello\nHow are you?")
    assert speaker == "Nicole"
    assert text == "Hello How are you?"


def test_parse_speaker_and_text_without_label():
    speaker, text = parse_speaker_and_text("No speaker line")
    assert speaker is None
    assert text == "No speaker line"


def test_get_voice_for_speaker_mapping():
    mapping = {"Nicole": "en-US-EmmaMultilingualNeural"}
    assert get_voice_for_speaker("Nicole", mapping, "default") == "en-US-EmmaMultilingualNeural"
    assert get_voice_for_speaker("Unknown", mapping, "default") == "default"


def test_align_segment_duration_padding(silent_segment: AudioSegment):
    original = silent_segment[:200]
    target_duration = len(original) + 300
    aligned = align_segment_duration(original, target_duration, tolerance_ms=10)
    assert len(aligned) == target_duration


def test_align_segment_duration_trimming(silent_segment: AudioSegment):
    target_duration = len(silent_segment) - 200
    aligned = align_segment_duration(silent_segment, target_duration, tolerance_ms=10)
    assert len(aligned) == target_duration

