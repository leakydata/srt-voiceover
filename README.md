# 🎙️ srt-voiceover

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)

**AI-powered audio dubbing pipeline: Transcribe, edit, and convert to synchronized voiceovers using Whisper + Microsoft Edge TTS.**

Perfect free alternative to SpeechGen, Murf.ai, and other paid dubbing services!

## ✨ Features

- 🎤 **Audio Transcription** - Convert audio/video to SRT with Whisper
- 🎭 **Advanced Speaker Detection** - Works with pre-labeled & auto-detected speakers
- ⏱️ **Word-Level Timing** - Fuzzy word matching with confidence scoring
- 🎯 **Per-Voice Optimization** - 30+ voice profiles for natural sound
- 📊 **Quality Metrics** - Automatic sync quality reporting with issue detection
- 🌍 **400+ Voices** - Microsoft Edge TTS in 80+ languages
- 🌐 **Automatic Translation** - Translate SRT to 16+ languages using Ollama (local or remote)
- 🎬 **Video Dubbing** - Complete pipeline for video re-voicing
- ✏️ **Edit Workflow** - Fix transcription errors before voiceover generation
- 📤 **Multi-Format Export** - WebVTT, SRT, JSON, CSV, FCPXML
- 🚀 **GPU Acceleration** - 5-10x faster with CUDA
- 💰 **Free & Open Source** - No subscriptions or API costs

## 🚀 Quick Start

### Installation

```bash
pip install srt-voiceover[all]
```

**Required:** [FFmpeg](https://ffmpeg.org/download.html) (must be in PATH)

### Basic Usage

```bash
# Convert SRT to voiceover
srt-voiceover voiceover subtitles.srt -o output.mp3

# Transcribe audio to SRT
srt-voiceover transcribe audio.mp3 -o output.srt

# Re-voice entire video (one command)
srt-voiceover revoice video.mp4 -o new_audio.mp3 --use-word-timing --elastic-timing

# Merge audio back into video
ffmpeg -i video.mp4 -i new_audio.mp3 -c:v copy -map 0:v:0 -map 1:a:0 final.mp4
```

### Two-Step Workflow (Edit Transcriptions)

```bash
# 1. Transcribe and save word timings
srt-voiceover transcribe video.mp4 -o transcript.srt --save-word-timings

# 2. Edit transcript.srt to fix errors (use any text editor)

# 3. Generate corrected voiceover
srt-voiceover voiceover transcript.srt -o output.mp3 \
  --word-timings transcript_word_timings.json --elastic-timing
```

## 📚 Documentation

- **[Quick Start Guide](QUICKSTART.md)** - 30-second to 5-minute tutorials
- **[Advanced Features Guide](ADVANCED_FEATURES.md)** - Fuzzy matching, voice profiles, quality metrics
- **[Translation Guide](TRANSLATION_GUIDE.md)** - Automatic SRT translation using Ollama (Phase 1 & 2)
- **[Quick Start Enhancements](QUICK_START_ENHANCEMENTS.md)** - New features overview
- **[Full Documentation](DOCUMENTATION.md)** - Complete guide with examples
- **[Implementation Details](IMPLEMENTATION_SUMMARY.md)** - Technical architecture
- **[Contributing Guide](CONTRIBUTING.md)** - Development setup
- **[Documentation Index](DOCS_INDEX.md)** - Navigate all guides by use case and feature

## 🎯 Use Cases

- 🎬 Video dubbing and localization
- 🎧 Podcast re-voicing and translation
- 📹 YouTube content creation
- 🎭 ADR (Automated Dialogue Replacement)
- 📺 Audiobook production
- 🔄 Voice replacement in recordings

## 🎨 Voice Timing Modes

### Default (Fast & Natural)
```bash
srt-voiceover revoice audio.mp3 -o output.mp3
```
Best for audio-only content. Very natural sounding, may drift slightly from original timing.

### Word-Level (Dynamic Pacing)
```bash
srt-voiceover revoice video.mp4 -o output.mp3 --use-word-timing
```
Extracts word timestamps from Whisper for accurate pacing. Good for screen recordings.

### Elastic with Smoothing (Recommended for Video)
```bash
srt-voiceover revoice video.mp4 -o output.mp3 --use-word-timing --elastic-timing
```
Perfect timing + smooth, natural transitions. Best for video dubbing with visible speakers.

**How it works:** Expands timing windows by borrowing from gaps, then smooths rate changes (max 15% per segment) to prevent jarring speed jumps.

## ✨ Advanced Features (NEW!)

### Smart Speaker Detection
Works seamlessly with both labeled and unlabeled subtitles:

```bash
# Pre-labeled: "Nathan: Hello world"
# Auto-detected: Uses context and previous speaker

srt-voiceover revoice video.mp4 -o output.mp3 --use-word-timing
```

See [Advanced Features Guide](ADVANCED_FEATURES.md) for details on:
- Explicit label detection
- Context-based speaker inference
- Multi-speaker analysis

### Fuzzy Word Matching
Handles transcription variations automatically:
- Typos and spelling variations (70% similarity threshold)
- Contractions: "don't" ↔ "dont"
- Punctuation handling
- **Confidence scoring** (0-100%) for sync quality

### Per-Voice Optimization
30+ voice profiles with:
- Baseline speaking rates per voice
- Natural rate adjustment ranges
- Voice-specific characteristics

```bash
# List available voices with profiles
python -c "from srt_voiceover import list_available_voices; [print(v) for v in list_available_voices()]"
```

### Quality Metrics & Reporting
Automatic analysis of synchronization:
- Segment-level confidence scores
- Issue detection (10+ issue types)
- Quality level classification (EXCELLENT/GOOD/FAIR/POOR)
- JSON export for analysis

```python
import srt_voiceover as svo

quality_report = svo.build_voiceover_from_srt(
    "subtitles.srt", "output.mp3",
    word_timings=timings,
    verbose=True  # Shows quality report
)

# Access metrics
print(quality_report.get_summary())
quality_report.export_json("report.json")
```

### Multi-Format Export
Export word timings for video editor integration:

```bash
srt-voiceover transcribe video.mp4 -o subs.srt --save-word-timings

# Then export to multiple formats:
python -c "from srt_voiceover import export_word_timings_multi; \
  export_word_timings_multi(timings, 'output', formats=['vtt', 'json', 'csv'])"
```

Supported formats:
- **JSON** - Machine-readable data
- **WebVTT** - Web video players
- **SubRip (SRT)** - Subtitle editors
- **CSV** - Spreadsheets
- **FCPXML** - Final Cut Pro

## 🌍 Multi-Language Support

400+ voices in 80+ languages:

```bash
# List all voices
srt-voiceover --list-voices

# Use specific voice
srt-voiceover voiceover script.srt -o output.mp3 \
  --default-voice "es-ES-ElviraNeural"  # Spanish
```

Popular voices:
- English (US): `en-US-AndrewMultilingualNeural`, `en-US-JennyNeural`
- Spanish: `es-ES-ElviraNeural`, `es-MX-DaliaNeural`
- French: `fr-FR-DeniseNeural`, `fr-CA-SylvieNeural`
- German: `de-DE-KatjaNeural`, `de-DE-ConradNeural`
- Japanese: `ja-JP-NanamiNeural`, `ja-JP-KeitaNeural`

## 🌐 Automatic Translation (NEW!)

Translate subtitles to 16+ languages automatically using Ollama:

```bash
# Transcribe English video and translate to Spanish
srt-voiceover transcribe video.mp4 -o output.srt --translate-to es

# Complete workflow: transcribe → translate → revoice
srt-voiceover revoice video.mp4 -o spanish_audio.mp3 \
  --translate-to es \
  --use-word-timing --elastic-timing

# Using remote Ollama (e.g., via ngrok)
srt-voiceover revoice video.mp4 -o output.mp3 \
  --translate-to fr \
  --ollama-base-url https://your-ngrok-url.ngrok-free.app
```

**Requirements:**
- [Ollama](https://ollama.ai) - Download and run locally or access remotely
- Model: `ollama pull gpt-oss:20b` (default) or any available model (mistral, neural-chat, etc.)

**Supported languages:** Spanish, French, German, Italian, Portuguese, Russian, Japanese, Chinese, Korean, Arabic, Hindi, Dutch, Polish, Turkish, Thai, Vietnamese

See [Translation Guide](TRANSLATION_GUIDE.md) for details on setup and configuration.

## 👥 Multi-Speaker Support

### Automatic Detection

```bash
# Basic speaker detection
srt-voiceover revoice podcast.mp3 -o output.mp3 --multi-speaker

# Professional ML-based diarization (requires HF_TOKEN)
srt-voiceover revoice podcast.mp3 -o output.mp3 --use-pyannote --use-word-timing
```

### Manual Assignment

Create `config.yaml`:
```yaml
speaker_voices:
  Alice: "en-US-EmmaMultilingualNeural"
  Bob: "en-US-AndrewMultilingualNeural"
```

Label speakers in SRT:
```srt
1
00:00:00,000 --> 00:00:02,000
Alice: Hello, how are you?

2
00:00:02,500 --> 00:00:04,000
Bob: I'm doing great, thanks!
```

## ⚡ GPU Acceleration

5-10x faster transcription and diarization:

```bash
# Install CUDA PyTorch (adjust cu121 for your CUDA version)
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121

# Install CUDA features
pip install srt-voiceover[cuda]

# GPU is detected and used automatically
srt-voiceover revoice video.mp4 -o output.mp3 --use-word-timing
```

## ⚙️ Configuration

Create `config.yaml` for persistent settings:

```yaml
# Voice settings
default_voice: "en-US-AndrewMultilingualNeural"
rate: "+0%"      # Speed: -50% to +100%
volume: "+0%"    # Volume: -50% to +100%
pitch: "+0Hz"    # Pitch: -50Hz to +100Hz

# Timing (recommended for video)
use_word_timing: true
elastic_timing: true
timing_tolerance_ms: 200

# Transcription
whisper_model: "base"  # tiny, base, small, medium, large

# Speaker mapping
speaker_voices:
  Alice: "en-US-EmmaMultilingualNeural"
  Bob: "en-US-AndrewMultilingualNeural"
```

Use with any command:
```bash
srt-voiceover revoice video.mp4 -o output.mp3 -c config.yaml
```

## 📦 Installation Options

```bash
# Core only (SRT to voiceover)
pip install srt-voiceover

# With transcription (Whisper)
pip install srt-voiceover[transcription]

# With professional speaker diarization
pip install srt-voiceover[diarization]

# Everything (CPU versions)
pip install srt-voiceover[all]

# GPU acceleration (install CUDA PyTorch first)
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121
pip install srt-voiceover[cuda]
```

## 🛠️ Requirements

- **Python 3.11+** (tested on 3.11 and 3.12)
- **FFmpeg** - For audio/video processing ([download](https://ffmpeg.org/download.html))
- **GPU (optional)** - NVIDIA CUDA for faster processing
- **HF Token (optional)** - For professional speaker diarization ([get token](https://huggingface.co/settings/tokens))

## 💡 Examples

### Video Dubbing Pipeline

```bash
# Complete workflow with best quality settings
srt-voiceover revoice video.mp4 -o dubbed.mp3 \
  --use-word-timing \
  --elastic-timing \
  --default-voice "en-US-AndrewMultilingualNeural" \
  --rate "+10%"

# Merge with original video
ffmpeg -i video.mp4 -i dubbed.mp3 -c:v copy -map 0:v:0 -map 1:a:0 final.mp4
```

### Multi-Language Translation

```bash
# 1. Transcribe original
srt-voiceover transcribe english.mp4 -o english.srt --save-word-timings

# 2. Translate SRT to Spanish (use any translation service)

# 3. Generate Spanish voiceover
srt-voiceover voiceover spanish.srt -o spanish.mp3 \
  --word-timings english_word_timings.json \
  --default-voice "es-ES-ElviraNeural" \
  --elastic-timing

# 4. Create Spanish version
ffmpeg -i english.mp4 -i spanish.mp3 -c:v copy -map 0:v:0 -map 1:a:0 spanish.mp4
```

### Batch Processing

```bash
# Process multiple videos
for video in *.mp4; do
  srt-voiceover revoice "$video" -o "${video%.mp4}_dubbed.mp3" \
    --use-word-timing --elastic-timing
done
```

## 🤝 Contributing

Contributions welcome! See [CONTRIBUTING.md](CONTRIBUTING.md) for development setup.

## 📄 License

MIT License - see [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

### Technologies
- **[OpenAI Whisper](https://github.com/openai/whisper)** - Speech recognition
- **[Microsoft Edge TTS](https://github.com/rany2/edge-tts)** - Text-to-speech
- **[Ollama](https://ollama.ai)** - Local LLM inference for translation (Phase 1 & 2)
- **[Pyannote.audio](https://github.com/pyannote/pyannote-audio)** - Speaker diarization
- **[FFmpeg](https://ffmpeg.org/)** - Audio/video processing

### Development
This project was created by **Nathan Jones** through an iterative collaborative process with **Claude AI (Anthropic)** via **[Cursor IDE](https://cursor.sh/)**. The architecture, feature decisions, and testing were driven by Nathan, with AI assistance in implementation, optimization, and documentation. This represents a modern approach to open-source development where human creativity and AI capabilities work together.

## 🗺️ Roadmap

### Recently Completed (Phase 1 & 2)
- ✅ **Automatic Translation** - Translate SRT to 16+ languages using Ollama (local or remote)
- ✅ **CLI Translation Integration** - `--translate-to` flag for transcribe and revoice commands
- ✅ **Remote Ollama Support** - Access Ollama via ngrok URLs for remote instances

### Coming Soon (Phase 3 & 4)
Future features and improvements we're planning:

### Translation & Localization Enhancements
- **Extended LLM Support** - OpenAI GPT, Anthropic Claude, DeepSeek (Phase 4)
- **Translation Caching** - Cache translations for faster re-runs (Phase 3)
- **Quality Metrics** - Automatic translation quality scoring (Phase 3)
- **YouTube accessibility** - Make content accessible across language barriers
- **Movie localization** - Professional-quality dubbing for films
- **Multi-track video creation** - One-command generation of videos with multiple audio/subtitle tracks
- **Subtitle embedding** - Automatically embed soft subtitles (toggle-able, not burned-in)

### Quality Improvements
- **Voice cloning support** - Preserve original speaker's voice characteristics
- **Emotion preservation** - Match emotional tone from original audio
- **Lip-sync optimization** - Even better timing for close-up face shots
- **Background audio mixing** - Preserve music/sfx while replacing dialogue

### Performance & UX
- **Batch processing UI** - Process multiple files efficiently
- **Web interface** - Browser-based tool for non-technical users
- **Real-time preview** - Hear voices before generating full audio
- **Cloud deployment** - Optional hosted service

**Want to help?** Check out [open issues](https://github.com/leakydata/srt-voiceover/issues) or suggest features in [discussions](https://github.com/leakydata/srt-voiceover/discussions)!

## 📞 Support

- **Issues**: https://github.com/leakydata/srt-voiceover/issues
- **Discussions**: https://github.com/leakydata/srt-voiceover/discussions
- **Documentation**: See [DOCUMENTATION.md](DOCUMENTATION.md)

---

**Made with ❤️ for the open-source community**
