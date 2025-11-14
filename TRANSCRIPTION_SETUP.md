# 🎤 Transcription Feature Setup

## Important: Two Ways to Use Transcription

The transcription feature has been updated to work **locally** by default (no API server needed for transcription!).

### Method 1: Local Whisper (Recommended - Works Offline!)

Uses OpenAI's Whisper library directly on your machine.

**Advantages:**
- ✅ Works completely offline
- ✅ No API costs
- ✅ Fast on GPU (CUDA)
- ✅ Privacy (audio never leaves your machine)
- ✅ Multiple model sizes (tiny to large)

**Installation:**
```bash
pip install openai-whisper

# Or install srt-voiceover with transcription support
pip install -e .[transcription]
```

**Usage:**
```bash
# Transcribe audio locally
srt-voiceover transcribe audio.mp3 -o subtitles.srt

# Specify model size (tiny, base, small, medium, large)
srt-voiceover transcribe audio.mp3 -o output.srt --model small

# Complete workflow - transcribe + re-voice
srt-voiceover revoice podcast.mp3 -o new_podcast.mp3 -c config.yaml
```

**Model Sizes:**
| Model  | Size | Speed  | Quality |
|--------|------|--------|---------|
| tiny   | 39M  | Fastest | Basic  |
| base   | 74M  | Fast    | Good   |
| small  | 244M | Medium  | Better |
| medium | 769M | Slow    | Great  |
| large  | 1550M| Slowest | Best   |

**First Run:**
The model will be downloaded automatically (~75MB for "base"). This happens only once.

---

### Method 2: API Mode (OpenAI API or Compatible Server)

Use OpenAI's API or a compatible Whisper API server.

**When to use:**
- You have OpenAI API access
- You're on a machine without GPU
- You want to use a custom Whisper API server

**Setup for OpenAI API:**
```yaml
# config.yaml
use_whisper_api: true
whisper_api_url: "https://api.openai.com/v1/audio/transcriptions"
whisper_api_key: "sk-your-openai-api-key"
```

**Setup for Custom Server:**
If you have a custom Whisper API server (like [whisper-api](https://github.com/fedirz/faster-whisper-server)):
```yaml
# config.yaml
use_whisper_api: true
whisper_api_url: "http://localhost:8000/v1/audio/transcriptions"
whisper_api_key: "your_key_if_needed"
```

---

## Configuration

### Updated config.yaml

```yaml
# Edge TTS API (for text-to-speech) - REQUIRED
edge_tts_url: "http://localhost:5050/v1/audio/speech"
api_key: "your_api_key_here"

# Whisper settings (for transcription) - OPTIONAL
whisper_model: "base"  # Model size: tiny/base/small/medium/large
use_whisper_api: false  # Set to true to use API instead of local

# If using API mode:
# whisper_api_url: "https://api.openai.com/v1/audio/transcriptions"
# whisper_api_key: "sk-your-openai-key"

# Voice mapping (works for both SRT and transcription)
speaker_voices:
  Nathan: "en-US-AndrewMultilingualNeural"
  Nicole: "en-US-EmmaMultilingualNeural"
  Speaker A: "en-US-GuyNeural"      # Auto-detected speakers
  Speaker B: "en-US-JennyNeural"

default_voice: "en-US-AndrewMultilingualNeural"
speed: 1.0
```

---

## Examples

### Example 1: Local Transcription (Default)

```bash
# Install whisper
pip install openai-whisper

# Transcribe
srt-voiceover transcribe interview.mp3 -o interview.srt
```

### Example 2: Using Different Models

```bash
# Fast but less accurate
srt-voiceover transcribe audio.mp3 -o output.srt --model tiny

# Slower but more accurate
srt-voiceover transcribe audio.mp3 -o output.srt --model medium
```

### Example 3: Complete Workflow (Local)

```bash
# One command: transcribe + re-voice (all local!)
srt-voiceover revoice podcast.mp3 -o ai_podcast.mp3 -c config.yaml
```

### Example 4: Using OpenAI API

**config.yaml:**
```yaml
edge_tts_url: "http://localhost:5050/v1/audio/speech"
api_key: "edge_tts_key"

use_whisper_api: true
whisper_api_url: "https://api.openai.com/v1/audio/transcriptions"
whisper_api_key: "sk-your-openai-key"

speaker_voices:
  Speaker A: "en-US-AndrewMultilingualNeural"
  Speaker B: "en-US-EmmaMultilingualNeural"
```

```bash
srt-voiceover revoice podcast.mp3 -o new_podcast.mp3 -c config.yaml
```

---

## Python API

### Local Whisper
```python
from srt_voiceover import transcribe_audio_to_srt

# Local transcription (default)
transcribe_audio_to_srt(
    audio_path="podcast.mp3",
    output_srt_path="subtitles.srt",
    model="base",  # Model size
    language="en",
    enable_speaker_detection=True
)
```

### API Mode
```python
from srt_voiceover import transcribe_audio_to_srt

# Use OpenAI API
transcribe_audio_to_srt(
    audio_path="podcast.mp3",
    output_srt_path="subtitles.srt",
    model="whisper-1",
    language="en",
    use_api=True,
    api_url="https://api.openai.com/v1/audio/transcriptions",
    api_key="sk-your-api-key"
)
```

### Complete Workflow
```python
from srt_voiceover import audio_to_voiceover_workflow

# Local Whisper + Edge TTS
srt_path, audio_path = audio_to_voiceover_workflow(
    input_audio="original.mp3",
    output_audio="revoiced.mp3",
    edge_tts_url="http://localhost:5050/v1/audio/speech",
    edge_tts_api_key="your_edge_tts_key",
    whisper_model="base",  # Local model
    speaker_voices={
        "Speaker A": "en-US-AndrewMultilingualNeural",
        "Speaker B": "en-US-EmmaMultilingualNeural",
    },
    language="en",
    use_whisper_api=False  # Use local Whisper
)
```

---

## Hardware Requirements

### Local Whisper

**CPU Only:**
- Works on any modern CPU
- Slower but functional
- Recommended: base or small model

**With NVIDIA GPU:**
- Much faster with CUDA
- Whisper will automatically use GPU if available
- Can handle medium/large models

**Apple Silicon (M1/M2/M3):**
- Good performance with MPS (Metal)
- Recommended: small or medium model

### Memory Requirements

| Model  | RAM Needed |
|--------|------------|
| tiny   | ~1 GB      |
| base   | ~1 GB      |
| small  | ~2 GB      |
| medium | ~5 GB      |
| large  | ~10 GB     |

---

## Troubleshooting

### "No module named 'whisper'"

```bash
pip install openai-whisper
```

### Slow transcription on CPU

Use a smaller model:
```bash
srt-voiceover transcribe audio.mp3 --model tiny
```

### GPU not being used

Install PyTorch with CUDA:
```bash
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
```

### Out of memory errors

Use a smaller model or process shorter audio chunks.

---

## What About the localhost:5050 Server?

**Important clarification:**

- `http://localhost:5050` = **Edge TTS only** (text → speech)
  - Still required for voiceover generation
  - Still runs with `npm start` in openai-edge-tts

- **Whisper transcription** = Now runs **locally** by default (speech → text)
  - No server needed!
  - Just install `openai-whisper`

So you only need the Edge TTS server for the voiceover generation part, not for transcription!

---

## Summary

| Feature | What's Needed |
|---------|---------------|
| **SRT → Voiceover** | Edge TTS server (localhost:5050) |
| **Audio → SRT (transcription)** | openai-whisper package (local) |
| **Complete workflow** | Both of the above |

**Simple setup:**
```bash
# 1. Install srt-voiceover with transcription
pip install -e .[transcription]

# 2. Start Edge TTS server (separate terminal)
cd openai-edge-tts
npm start

# 3. Use everything!
srt-voiceover revoice podcast.mp3 -o new_podcast.mp3
```

That's it! No need for multiple API servers. 🎉

