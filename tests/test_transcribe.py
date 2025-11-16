import types
from pathlib import Path
from unittest.mock import MagicMock

import pytest

from srt_voiceover import transcribe as tr


def _make_audio_file(tmp_path: Path) -> Path:
    audio_path = tmp_path / "input.wav"
    audio_path.write_bytes(b"dummy")
    return audio_path


def test_transcribe_audio_to_srt_local(monkeypatch, tmp_path):
    audio_path = _make_audio_file(tmp_path)
    model = MagicMock()
    model.transcribe.return_value = {
        "segments": [
            {"start": 0.0, "end": 1.0, "text": "Hello"},
        ]
    }
    fake_whisper = types.SimpleNamespace(load_model=MagicMock(return_value=model))

    monkeypatch.setattr(tr, "WHISPER_AVAILABLE", True)
    monkeypatch.setattr(tr, "whisper", fake_whisper)

    output = tmp_path / "out.srt"
    tr.transcribe_audio_to_srt(str(audio_path), str(output), verbose=False)

    assert output.exists()
    assert "Hello" in output.read_text(encoding="utf-8")


def test_transcribe_audio_to_srt_api(monkeypatch, tmp_path):
    audio_path = _make_audio_file(tmp_path)

    class DummyResponse:
        def raise_for_status(self):
            return None

        def json(self):
            return {"segments": [{"start": 0.0, "end": 1.0, "text": "API text"}]}

    def fake_post(*args, **kwargs):
        return DummyResponse()

    monkeypatch.setattr(tr, "REQUESTS_AVAILABLE", True)
    monkeypatch.setattr(tr, "requests", types.SimpleNamespace(post=fake_post))

    output = tmp_path / "api.srt"
    tr.transcribe_audio_to_srt(
        str(audio_path),
        str(output),
        verbose=False,
        use_api=True,
        api_url="https://example.com",
        api_key="token",
    )

    assert "API text" in output.read_text(encoding="utf-8")


def test_group_words_into_segments():
    words = [
        {"start": 0.0, "end": 0.4, "word": "Hello"},
        {"start": 0.5, "end": 0.9, "word": "there"},
        {"start": 2.0, "end": 2.4, "word": "world"},
    ]
    segments = tr._group_words_into_segments(words, max_duration=1.0)
    assert len(segments) == 2
    assert segments[0]["text"].strip() == "Hello there"


def test_get_speaker_at_time():
    speaker_map = {(0.0, 2.0): "SPEAKER_00", (2.0, 4.0): "SPEAKER_01"}
    speaker = tr._get_speaker_at_time(speaker_map, start_time=0.5, end_time=1.5)
    assert speaker == "SPEAKER_00"
    fallback = tr._get_speaker_at_time(speaker_map, start_time=4.5, end_time=5.0)
    assert fallback in {"SPEAKER_00", "SPEAKER_01"}


def test_audio_to_voiceover_workflow_invokes_steps(monkeypatch, tmp_path):
    audio_path = _make_audio_file(tmp_path)
    srt_path = tmp_path / "temp.srt"
    srt_path.write_text("1\n00:00:00,000 --> 00:00:01,000\nText", encoding="utf-8")

    calls = {"transcribe": False, "build": False}

    def fake_transcribe(**kwargs):
        calls["transcribe"] = True
        return str(srt_path)

    def fake_build(**kwargs):
        calls["build"] = True
        calls["build_kwargs"] = kwargs

    monkeypatch.setattr(tr, "transcribe_audio_to_srt", fake_transcribe)
    monkeypatch.setattr("srt_voiceover.core.build_voiceover_from_srt", fake_build)

    result = tr.audio_to_voiceover_workflow(
        input_audio=str(audio_path),
        output_audio=str(tmp_path / "out.mp3"),
        speaker_voices={"Nathan": "en-US-AndrewMultilingualNeural"},
        verbose=False,
    )

    assert calls["transcribe"] and calls["build"]
    assert result[0] == str(srt_path)
    assert calls["build_kwargs"]["speaker_voices"]["Nathan"] == "en-US-AndrewMultilingualNeural"

