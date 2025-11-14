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
- **👥 Speaker Detection**: Basic speaker identification (Speaker A/B)
- **🎬 Video Support**: Extract audio from video files automatically
- **🌍 Multi-Language**: Supports 50+ languages via Whisper

### 🔊 Voice Generation
- **🎭 Multi-Speaker Support**: Assign different voices to different speakers
- **⏱️ Perfect Timing**: Synchronizes audio precisely with subtitle timestamps
- **🌍 70+ Voices**: Access to all Microsoft Edge TTS voices in 40+ languages
- **🎚️ Speed Control**: Adjust speech rate from 0.25x to 4.0x

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

2. **Edge TTS Server** - For voiceover generation (text-to-speech)
   - Clone and run: [OpenAI-EdgeTTS](https://github.com/travisvn/openai-edge-tts)
   ```bash
   git clone https://github.com/travisvn/openai-edge-tts.git
   cd openai-edge-tts
   npm install
   npm start
   ```
   Provides endpoint: `http://localhost:5050/v1/audio/speech`

3. **OpenAI Whisper** (Optional) - For audio transcription features
   ```bash
   pip install openai-whisper
   # Or install srt-voiceover with transcription support
   pip install srt-voiceover[transcription]
   ```
   Transcription runs **locally** on your machine (no server needed!)

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
# Edge TTS (Text-to-Speech) - REQUIRED
# ===================================
edge_tts_url: "http://localhost:5050/v1/audio/speech"
api_key: "your_api_key_here"

# ===================================
# Whisper Transcription - OPTIONAL
# ===================================
# Uses LOCAL whisper by default (pip install openai-whisper)
whisper_model: "base"  # tiny, base, small, medium, large
use_whisper_api: false  # Only set true for OpenAI API

# Optional: OpenAI API mode
# use_whisper_api: true
# whisper_api_url: "https://api.openai.com/v1/audio/transcriptions"
# whisper_api_key: "sk-your-openai-key"

# ===================================
# Voice Settings
# ===================================
default_voice: "en-US-AndrewMultilingualNeural"
response_format: "mp3"
speed: 1.0
timing_tolerance_ms: 150

# Map speaker names to voices
speaker_voices:
  Nathan: "en-US-AndrewMultilingualNeural"
  Nicole: "en-US-EmmaMultilingualNeural"
  Speaker A: "en-US-GuyNeural"  # Auto-detected speakers
  Speaker B: "en-US-JennyNeural"
```

Or use JSON format:

```json
{
  "edge_tts_url": "http://localhost:5050/v1/audio/speech",
  "api_key": "your_api_key_here",
  "default_voice": "en-US-AndrewMultilingualNeural",
  "speaker_voices": {
    "Nathan": "en-US-AndrewMultilingualNeural",
    "Nicole": "en-US-EmmaMultilingualNeural"
  }
}
```

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

### Speed Control

Adjust speech rate from 0.25x (very slow) to 4.0x (very fast):

```bash
srt-voiceover input.srt -o output.mp3 -c config.yaml --speed 1.2
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

## 🚀 Publishing to GitHub

```bash
# Initialize git
git init
git add .
git commit -m "Initial commit: Complete dubbing pipeline with transcription"

# Connect to your repo
git remote add origin https://github.com/leakydata/srt-voiceover.git
git branch -M main

# Pull the LICENSE file
git pull origin main --allow-unrelated-histories

# Push to GitHub
git push -u origin main
```

After pushing, users can install directly from GitHub:
```bash
pip install git+https://github.com/leakydata/srt-voiceover.git

# With transcription support
pip install "git+https://github.com/leakydata/srt-voiceover.git#egg=srt-voiceover[transcription]"
```

## 🤝 Contributing

Contributions are welcome! See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Built with [Microsoft Edge TTS](https://github.com/rany2/edge-tts)
- Inspired by the need for an open-source alternative to expensive dubbing services
- Special thanks to [OpenAI-EdgeTTS](https://github.com/travisvn/openai-edge-tts) for the API server

## ❓ FAQ

### Do I need the localhost:5050 server for transcription?
**No!** Transcription runs locally using openai-whisper. The server is only needed for voiceover generation.

### Which Whisper model should I use?
- **tiny/base**: Fast, good for testing or lower-end hardware
- **small**: Good balance of speed and accuracy
- **medium/large**: Best quality, needs more RAM and time

### Can I use this without installing Whisper?
**Yes!** If you only need SRT → voiceover conversion, you don't need Whisper at all.

### Is my audio sent to any servers?
With local Whisper (default), your audio never leaves your machine. Only the final voiceover generation uses the Edge TTS server.

### Can I use this commercially?
Yes, MIT license. But check the licenses of Edge TTS and Whisper for your use case.

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
        edge_tts_url="http://localhost:5050/v1/audio/speech",
        edge_tts_api_key="your_key",
        speaker_voices={"Speaker A": "en-US-AndrewMultilingualNeural"},
        whisper_model="base"
    )
```

## 🗺️ Roadmap

- [x] Audio transcription to SRT (v0.2.0)
- [x] Complete re-voicing workflow (v0.2.0)
- [x] Video audio extraction (v0.2.0)
- [ ] Publish to PyPI
- [ ] Advanced speaker diarization (pyannote.audio integration)
- [ ] Add web UI
- [ ] Support for more TTS engines (Google Cloud TTS, AWS Polly)
- [ ] Batch processing mode with parallel processing
- [ ] Voice emotion/style control
- [ ] Background music mixing
- [ ] Direct video output (merge with video file automatically)

---

**Made with ❤️ by Nathan Jones**

*If this tool saves you money on dubbing services, consider starring the repo!* ⭐
