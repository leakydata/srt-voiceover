# 🎙️ srt-voiceover

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.7+](https://img.shields.io/badge/python-3.7+-blue.svg)](https://www.python.org/downloads/)

**AI-powered tool that converts SRT subtitle files into synchronized voiceovers using Microsoft Edge TTS voices.**

Perfect alternative to SpeechGen, Murf.ai, and other paid dubbing services! Create high-quality voiceovers for:
- 🎬 Video dubbing and localization
- 🎧 Podcast creation
- 📹 YouTube content
- 🎭 ADR (Automated Dialogue Replacement) workflows
- 📺 Audiobook production

## ✨ Features

- **🎭 Multi-Speaker Support**: Automatically detect and assign different voices to different speakers
- **⏱️ Perfect Timing**: Synchronizes audio precisely with subtitle timestamps
- **🌍 70+ Voices**: Access to all Microsoft Edge TTS voices in 40+ languages
- **🎚️ Speed Control**: Adjust speech rate from 0.25x to 4.0x
- **📦 Easy Installation**: Install via pip and use from command line
- **⚙️ Flexible Configuration**: YAML/JSON config files or command-line arguments
- **🔄 Batch Processing**: Process multiple files with consistent settings
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

2. **Edge TTS API Server** - You need a local OpenAI-compatible Edge TTS server
   - Clone and run: [OpenAI-EdgeTTS](https://github.com/travisvn/openai-edge-tts)
   ```bash
   git clone https://github.com/travisvn/openai-edge-tts.git
   cd openai-edge-tts
   npm install
   npm start
   ```

### Basic Usage

```bash
# Create a sample config file
srt-voiceover --init-config config.yaml

# Edit config.yaml with your settings (API URL, voices, etc.)

# Generate voiceover
srt-voiceover input.srt -o output.mp3 --config config.yaml
```

## 📖 Usage Examples

### Command Line Interface

```bash
# Using config file (recommended)
srt-voiceover subtitles.srt -o voiceover.mp3 --config config.yaml

# Using command line arguments
srt-voiceover subtitles.srt -o voiceover.mp3 \
  --url http://localhost:5050/v1/audio/speech \
  --api-key your_api_key \
  --speed 1.1

# Quiet mode (suppress progress output)
srt-voiceover input.srt -o output.mp3 -c config.yaml --quiet

# WAV output instead of MP3
srt-voiceover input.srt -o output.wav --format wav -c config.yaml
```

### Python API

```python
from srt_voiceover import build_voiceover_from_srt

# Basic usage
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

## 🗺️ Roadmap

- [ ] Publish to PyPI
- [ ] Add web UI
- [ ] Support for more TTS engines (Google Cloud TTS, AWS Polly)
- [ ] Batch processing mode
- [ ] Voice emotion/style control
- [ ] Background music mixing
- [ ] Direct video output (merge with video file)

---

**Made with ❤️ by Nathan Jones**

*If this tool saves you money on dubbing services, consider starring the repo!* ⭐
