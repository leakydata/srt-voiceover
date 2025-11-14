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

2. **Edge TTS & Whisper API Server** - You need a local OpenAI-compatible server
   - Clone and run: [OpenAI-EdgeTTS](https://github.com/travisvn/openai-edge-tts) (supports both TTS and Whisper)
   ```bash
   git clone https://github.com/travisvn/openai-edge-tts.git
   cd openai-edge-tts
   npm install
   npm start
   ```
   This provides both endpoints:
   - TTS: `http://localhost:5050/v1/audio/speech`
   - Whisper: `http://localhost:5050/v1/audio/transcriptions`

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
# Edge TTS API endpoint
edge_tts_url: "http://localhost:5050/v1/audio/speech"

# API key for authentication
api_key: "your_api_key_here"

# Default voice for speakers without specific assignment
default_voice: "en-US-AndrewMultilingualNeural"

# Output format (mp3 or wav)
response_format: "mp3"

# Speech speed (1.0 = normal, 0.5 = half, 2.0 = double)
speed: 1.0

# Timing tolerance in milliseconds
timing_tolerance_ms: 150

# Map speaker names to voices
speaker_voices:
  Nathan: "en-US-AndrewMultilingualNeural"
  Nicole: "en-US-EmmaMultilingualNeural"
  John: "en-US-GuyNeural"
  Sarah: "en-US-JennyNeural"
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

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Built with [Microsoft Edge TTS](https://github.com/rany2/edge-tts)
- Inspired by the need for an open-source alternative to expensive dubbing services
- Special thanks to [OpenAI-EdgeTTS](https://github.com/travisvn/openai-edge-tts) for the API server

## 📧 Support

- **Issues**: [GitHub Issues](https://github.com/leakydata/srt-voiceover/issues)
- **Discussions**: [GitHub Discussions](https://github.com/leakydata/srt-voiceover/discussions)

## 🔄 Complete Workflows

For detailed workflow examples and real-world use cases, see [WORKFLOWS.md](WORKFLOWS.md):
- Video dubbing pipeline
- Podcast re-voicing
- Multi-language content creation
- Batch processing
- A/B testing with different voices

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
