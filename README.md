# 🎙️ srt-voiceover

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.7+](https://img.shields.io/badge/python-3.7+-blue.svg)](https://www.python.org/downloads/)

**Complete AI-powered audio dubbing pipeline: Transcribe audio to SRT with speaker detection, then convert to synchronized voiceovers using Microsoft Edge TTS.**

Perfect alternative to SpeechGen, Murf.ai, and other paid dubbing services! Create high-quality voiceovers for:
- 🎬 Video dubbing and localization
- 🎧 Podcast re-voicing and translation
- 📹 YouTube content creation
- 🎭 ADR (Automated Dialogue Replacement) workflows
- 📺 Audiobook production
- 🔄 Voice replacement in existing recordings

## ✨ Features

### 🎤 Audio Transcription (NEW!)
- **🎙️ Audio → SRT**: Transcribe any audio file to subtitles with timestamps
- **👥 Speaker Detection**: Three modes - single speaker, basic heuristic, or professional ML-based (pyannote)
- **🎬 Video Support**: Extract audio from MP4/AVI/MKV and other video formats automatically
- **🌍 Multi-Language**: Supports 50+ languages via Whisper
- **💻 Local Processing**: Runs on your machine (no cloud API needed)

### 🔊 Voice Generation
- **🎭 Multi-Speaker Support**: Assign different voices to different speakers
- **⏱️ Perfect Timing**: Synchronizes audio precisely with subtitle timestamps
- **🌍 400+ Voices**: Access to all Microsoft Edge TTS voices in 80+ languages
- **🎚️ Voice Customization**: Adjust speech rate, volume, and pitch
- **🚫 No API Costs**: Uses free Microsoft Edge TTS service directly

### 🔄 Complete Workflow
- **One-Command Dubbing**: Audio → Transcribe → Re-voice in one step
- **📦 Easy Installation**: Install via pip and use from command line
- **⚙️ Flexible Configuration**: YAML/JSON config files or command-line arguments
- **💰 Free & Open Source**: No subscriptions or API costs (runs locally)

## 🚀 Quick Start

### Installation

```bash
# Install from PyPI (coming soon)
pip install srt-voiceover

# Or install from source
git clone https://github.com/leakydata/srt-voiceover.git
cd srt-voiceover
pip install -e .
```

### Prerequisites

1. **FFmpeg** - Required for audio processing
   - Windows: Download from [ffmpeg.org](https://ffmpeg.org/download.html) and add to PATH
   - Mac: `brew install ffmpeg`
   - Linux: `sudo apt-get install ffmpeg`

2. **OpenAI Whisper** (Optional) - For audio transcription features
   ```bash
   pip install openai-whisper
   # Or install with transcription support
   pip install srt-voiceover[transcription]
   ```

3. **Pyannote Audio** (Optional) - For professional speaker diarization
   ```bash
   pip install pyannote.audio
   # Or install with diarization support
   pip install srt-voiceover[diarization]
   ```
   
   **Setup HuggingFace Token:**
   - Get token at: https://huggingface.co/settings/tokens
   - Accept license: https://huggingface.co/pyannote/speaker-diarization-3.1
   - Set environment variable:
     ```bash
     # Windows PowerShell (permanent):
     [System.Environment]::SetEnvironmentVariable('HF_TOKEN', 'hf_your_token_here', 'User')
     
     # Windows CMD:
     setx HF_TOKEN "hf_your_token_here"
     
     # Linux/Mac (add to ~/.bashrc or ~/.zshrc):
     export HF_TOKEN=hf_your_token_here
     ```

### Basic Usage

```bash
# Create a sample config file
srt-voiceover --init-config config.yaml

# Edit config.yaml with your settings (API URLs, voices, etc.)

# Method 1: SRT → Voiceover (original functionality)
srt-voiceover input.srt -o output.mp3 --config config.yaml

# Method 2: Audio → SRT (NEW! transcription)
srt-voiceover transcribe audio.mp3 -o output.srt --config config.yaml

# Method 3: Complete workflow - Audio → SRT → New Voiceover (NEW!)
srt-voiceover revoice original_audio.mp3 -o new_audio.mp3 --config config.yaml
```

## 📖 Usage Examples

### Command Line Interface

#### 1. SRT to Voiceover (Original Feature)
```bash
# Using config file (recommended)
srt-voiceover subtitles.srt -o voiceover.mp3 --config config.yaml

# Using command line arguments
srt-voiceover subtitles.srt -o voiceover.mp3 \
  --url http://localhost:5050/v1/audio/speech \
  --api-key your_api_key \
  --speed 1.1

# WAV output instead of MP3
srt-voiceover input.srt -o output.wav --format wav -c config.yaml
```

#### 2. Audio to SRT (NEW! Transcription)
```bash
# Transcribe audio file to SRT
srt-voiceover transcribe podcast.mp3 -o subtitles.srt --config config.yaml

# Transcribe with language specification
srt-voiceover transcribe audio.mp3 -o output.srt --language en

# Transcribe without speaker detection
srt-voiceover transcribe audio.mp3 -o output.srt --no-speaker-detection
```

#### 3. Complete Re-voicing Workflow (NEW!)
```bash
# One command: transcribe + re-voice
srt-voiceover revoice original.mp3 -o new_voice.mp3 --config config.yaml

# Keep the generated SRT file
srt-voiceover revoice original.mp3 -o new_voice.mp3 --keep-srt -c config.yaml

# With custom speed
srt-voiceover revoice podcast.mp3 -o faster_podcast.mp3 --speed 1.2 -c config.yaml
```

#### 4. Extract Audio from Video (NEW!)
```bash
# Extract audio from video
srt-voiceover extract-audio video.mp4 -o audio.wav

# Extract as MP3
srt-voiceover extract-audio video.mp4 -o audio.mp3 --format mp3
```

### Python API

#### SRT to Voiceover
```python
from srt_voiceover import build_voiceover_from_srt

build_voiceover_from_srt(
    srt_path="subtitles.srt",
    output_audio_path="output.mp3",
    edge_tts_url="http://localhost:5050/v1/audio/speech",
    api_key="your_api_key",
    speaker_voices={
        "Nathan": "en-US-AndrewMultilingualNeural",
        "Nicole": "en-US-EmmaMultilingualNeural",
    },
    default_voice="en-US-GuyNeural",
    speed=1.0,
    response_format="mp3"
)
```

#### Audio to SRT (NEW!)
```python
from srt_voiceover import transcribe_audio_to_srt

transcribe_audio_to_srt(
    audio_path="podcast.mp3",
    output_srt_path="subtitles.srt",
    whisper_url="http://localhost:5050/v1/audio/transcriptions",
    api_key="your_api_key",
    language="en",
    enable_speaker_detection=True
)
```

#### Complete Workflow (NEW!)
```python
from srt_voiceover import audio_to_voiceover_workflow

# One function does it all!
srt_path, audio_path = audio_to_voiceover_workflow(
    input_audio="original.mp3",
    output_audio="revoiced.mp3",
    whisper_url="http://localhost:5050/v1/audio/transcriptions",
    edge_tts_url="http://localhost:5050/v1/audio/speech",
    api_key="your_api_key",
    speaker_voices={
        "Speaker A": "en-US-AndrewMultilingualNeural",
        "Speaker B": "en-US-EmmaMultilingualNeural",
    },
    language="en",
    speed=1.0
)
```

## ⚙️ Configuration

### Config File Format

Create a `config.yaml` file:

```yaml
# ===================================
# Voice Settings
# ===================================
default_voice: "en-US-AndrewMultilingualNeural"

# Speech adjustments
rate: "+0%"      # Speed: -50% to +100%
volume: "+0%"    # Volume: -50% to +100%
pitch: "+0Hz"    # Pitch: -50Hz to +100Hz

# Timing tolerance in milliseconds
timing_tolerance_ms: 150

# ===================================
# Whisper Transcription - OPTIONAL
# ===================================
# Uses LOCAL whisper by default (pip install openai-whisper)
whisper_model: "base"  # tiny, base, small, medium, large
use_whisper_api: false

# Optional: OpenAI API mode
# use_whisper_api: true
# whisper_api_url: "https://api.openai.com/v1/audio/transcriptions"
# whisper_api_key: "sk-your-openai-key"

# ===================================
# Pyannote Speaker Diarization - OPTIONAL
# ===================================
use_pyannote: false  # Set true for professional speaker detection
# hf_token: "hf_your_token"  # Optional, will be prompted if needed

# ===================================
# Speaker to Voice Mapping
# ===================================
speaker_voices:
  Nathan: "en-US-AndrewMultilingualNeural"
  Nicole: "en-US-EmmaMultilingualNeural"
  Speaker A: "en-US-GuyNeural"  # Auto-detected speakers
  Speaker B: "en-US-JennyNeural"
```

See `examples/config.yaml` for a complete example configuration.

### SRT File Format

Your SRT file should include speaker names in the format `Speaker: dialogue`

```srt
1
00:00:00,000 --> 00:00:03,500
Nathan: Welcome to our tutorial on converting subtitles to voiceovers.

2
00:00:03,500 --> 00:00:07,000
Nicole: This is a powerful tool for creating automated dubbing.

3
00:00:07,500 --> 00:00:11,000
Nathan: Let's see how easy it is to use.
```

If no speaker is specified, the default voice will be used.

## 🎤 Available Voices

See [edgetts_voices_list.md](edgetts_voices_list.md) for a complete list of available voices.

Popular voices:
- **English (US)**: `en-US-AndrewMultilingualNeural`, `en-US-EmmaMultilingualNeural`, `en-US-AriaNeural`, `en-US-GuyNeural`
- **English (UK)**: `en-GB-RyanNeural`, `en-GB-SoniaNeural`
- **Spanish**: `es-ES-AlvaroNeural`, `es-MX-DaliaNeural`
- **French**: `fr-FR-DeniseNeural`, `fr-FR-HenriNeural`
- **German**: `de-DE-KatjaNeural`, `de-DE-ConradNeural`
- **Japanese**: `ja-JP-NanamiNeural`, `ja-JP-KeitaNeural`

## 🔧 Advanced Features

### Voice Customization

Adjust speech rate, volume, and pitch:

```bash
# Faster speech
srt-voiceover input.srt -o output.mp3 --rate "+20%"

# Quieter volume
srt-voiceover input.srt -o output.mp3 --volume "-30%"

# Lower pitch
srt-voiceover input.srt -o output.mp3 --pitch "-50Hz"

# Combine multiple adjustments
srt-voiceover input.srt -o output.mp3 --rate "+10%" --volume "+5%" --pitch "-20Hz"
```

### Speaker Detection Modes

Choose your speaker detection mode based on your needs:

```bash
# Single speaker (DEFAULT - fastest)
srt-voiceover revoice video.mp4 -o output.mp3

# Basic multi-speaker (fast, heuristic-based)
srt-voiceover revoice video.mp4 -o output.mp3 --multi-speaker

# Professional pyannote (best quality, slower)
srt-voiceover revoice video.mp4 -o output.mp3 --use-pyannote
```

### Timing Tolerance

Control how strictly audio duration matches subtitle timing:

```bash
# Strict timing (adjust audio if off by more than 50ms)
srt-voiceover input.srt -o output.mp3 -c config.yaml --tolerance 50

# Relaxed timing (only adjust if off by more than 500ms)
srt-voiceover input.srt -o output.mp3 -c config.yaml --tolerance 500
```

## 🆚 Comparison with Other Tools

| Feature | srt-voiceover | SpeechGen | Murf.ai | ElevenLabs |
|---------|---------------|-----------|---------|------------|
| **Price** | Free | $$ | $$$ | $$$ |
| **Multi-speaker** | ✅ | ✅ | ✅ | ✅ |
| **Timing sync** | ✅ Auto | Manual | Manual | Manual |
| **Local processing** | ✅ | ❌ | ❌ | ❌ |
| **API limits** | None | Limited | Limited | Limited |
| **Voice count** | 70+ | 50+ | 120+ | 100+ |
| **Open source** | ✅ | ❌ | ❌ | ❌ |


## 🤝 Contributing

Contributions are welcome! See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## ❓ FAQ

### Do I need any servers running?
**No!** Everything runs locally. The tool uses the `edge-tts` Python module directly for text-to-speech, and `openai-whisper` for transcription. No external servers or API keys needed (except HuggingFace token for optional pyannote).

### Which Whisper model should I use?
- **tiny/base**: Fast, good for testing or lower-end hardware
- **small**: Good balance of speed and accuracy
- **medium/large**: Best quality, needs more RAM and time

### Can I use this without installing Whisper?
**Yes!** If you only need SRT → voiceover conversion, you don't need Whisper at all.

### Is my audio sent to any servers?
With local Whisper (default), your audio never leaves your machine. Only the final voiceover generation uses the Edge TTS server.

### Can I use this commercially?
Yes, MIT license. However, please check the Microsoft Edge TTS terms of service and the licenses of dependencies (Whisper, pyannote) for your specific use case.

### How do I set up pyannote speaker diarization?
1. Install: `pip install pyannote.audio`
2. Create free account at [huggingface.co](https://huggingface.co/)
3. Get token at [Settings → Tokens](https://huggingface.co/settings/tokens) (Read access)
4. Accept license at [pyannote/speaker-diarization-3.1](https://huggingface.co/pyannote/speaker-diarization-3.1)
5. Set `HF_TOKEN` environment variable (see Prerequisites section above)
6. Use with `--use-pyannote` flag

## 📧 Support

- **Quick Start**: [QUICKSTART.md](QUICKSTART.md)
- **Issues**: [GitHub Issues](https://github.com/leakydata/srt-voiceover/issues)
- **Discussions**: [GitHub Discussions](https://github.com/leakydata/srt-voiceover/discussions)

## 🔄 Common Workflows

### Video Dubbing
```bash
# 1. Extract audio from video
srt-voiceover extract-audio video.mp4 -o audio.wav

# 2. Transcribe and re-voice in one step
srt-voiceover revoice audio.wav -o new_audio.mp3 --keep-srt -c config.yaml

# 3. Merge back with video using ffmpeg
ffmpeg -i video.mp4 -i new_audio.mp3 -c:v copy -map 0:v:0 -map 1:a:0 output.mp4
```

### Podcast Re-voicing
```bash
# Create different voice versions
srt-voiceover revoice podcast.mp3 -o version_a.mp3 -c config_formal.yaml
srt-voiceover revoice podcast.mp3 -o version_b.mp3 -c config_casual.yaml
```

### Batch Processing (Python)
```python
from srt_voiceover import audio_to_voiceover_workflow
from pathlib import Path

for audio_file in Path("./episodes").glob("*.mp3"):
    audio_to_voiceover_workflow(
        input_audio=str(audio_file),
        output_audio=f"./output/{audio_file.name}",
        speaker_voices={"Speaker A": "en-US-AndrewMultilingualNeural"},
        default_voice="en-US-AndrewMultilingualNeural",
        whisper_model="base",
        verbose=False
    )
```

## 🗺️ Roadmap

- [x] Audio transcription to SRT (v0.2.0)
- [x] Complete re-voicing workflow (v0.2.0)
- [x] Video audio extraction (v0.2.0)
- [x] Professional speaker diarization with pyannote (v0.3.0)
- [x] Direct edge-tts module integration (v0.3.0)
- [ ] Publish to PyPI
- [ ] Add web UI
- [ ] Support for more TTS engines (Google Cloud TTS, AWS Polly)
- [ ] Batch processing mode with parallel processing
- [ ] Voice emotion/style control
- [ ] Background music mixing
- [ ] Direct video output (merge with video file automatically)

## 🙏 Acknowledgments

This project is built on the shoulders of amazing open-source tools:

- **[edge-tts](https://github.com/rany2/edge-tts)** - Python interface to Microsoft Edge's TTS service (MIT License)
- **[openai-whisper](https://github.com/openai/whisper)** - Robust speech recognition by OpenAI (MIT License)
- **[pyannote-audio](https://github.com/pyannote/pyannote-audio)** - State-of-the-art speaker diarization (MIT License)
- **[pydub](https://github.com/jiaaro/pydub)** - Audio manipulation made easy (MIT License)
- **[pysrt](https://github.com/byroot/pysrt)** - SRT file parsing (GPL-3.0 License)
- **[FFmpeg](https://ffmpeg.org/)** - The backbone of audio/video processing (LGPL/GPL)

Special thanks to the creators and maintainers of these projects! 🎉

---

**Made with ❤️ by Nathan Jones**

*If this tool saves you money on dubbing services, consider starring the repo!* ⭐
