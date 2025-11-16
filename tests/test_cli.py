import sys
from pathlib import Path

from srt_voiceover import cli


def test_cli_init_config_creates_file(monkeypatch, tmp_path):
    config_path = tmp_path / "config.yaml"
    monkeypatch.setattr(sys, "argv", ["srt-voiceover", "--init-config", str(config_path)])

    cli.main()

    assert config_path.exists()
    content = config_path.read_text(encoding="utf-8")
    assert "default_voice" in content


def test_cli_voiceover_invokes_builder(monkeypatch, sample_srt, tmp_path):
    output_audio = tmp_path / "voice.mp3"
    called = {}

    def fake_build_voiceover_from_srt(**kwargs):
        called.update(kwargs)

    monkeypatch.setattr(cli, "build_voiceover_from_srt", fake_build_voiceover_from_srt)
    monkeypatch.setattr(
        sys,
        "argv",
        ["srt-voiceover", str(sample_srt), "-o", str(output_audio), "--default-voice", "en-US-GuyNeural"],
    )

    cli.main()

    assert called["output_audio_path"] == str(output_audio)
    assert called["default_voice"] == "en-US-GuyNeural"


def test_cli_transcribe_invokes_function(monkeypatch, tmp_path):
    audio_path = tmp_path / "input.wav"
    audio_path.write_bytes(b"dummy")
    called = {}

    def fake_transcribe_audio_to_srt(**kwargs):
        called.update(kwargs)

    monkeypatch.setattr(cli, "transcribe_audio_to_srt", fake_transcribe_audio_to_srt)
    monkeypatch.setattr(sys, "argv", ["srt-voiceover", "transcribe", str(audio_path), "-o", str(tmp_path / "out.srt")])

    cli.main()

    assert called["audio_path"] == str(audio_path)
    assert called["output_srt_path"].endswith("out.srt")

