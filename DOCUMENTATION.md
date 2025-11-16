# srt-voiceover Documentation

Complete documentation for the srt-voiceover audio dubbing pipeline.

---

## Table of Contents

1. [Installation](#installation)
2. [Basic Usage](#basic-usage)
3. [Voice Timing Modes](#voice-timing-modes)
4. [Two-Step Workflow](#two-step-workflow)
5. [Advanced Features](#advanced-features)
6. [Configuration](#configuration)
7. [API Reference](#api-reference)
8. [Troubleshooting](#troubleshooting)

---

## Installation

### Core Installation

```bash
# Install core package
pip install srt-voiceover

# Or from source
git clone https://github.com/leakydata/srt-voiceover.git
cd srt-voiceover
pip install -e .
```

### Optional Features

```bash
# Audio transcription (Whisper)
pip install srt-voiceover[transcription]

# Professional speaker diarization
pip install srt-voiceover[diarization]

# All features (CPU versions)
pip install srt-voiceover[all]

# GPU acceleration (install CUDA PyTorch first)
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121
pip install srt-voiceover[cuda]
```

### Requirements

- **FFmpeg**: Required for audio/video processing
- **Python 3.7+**: Core requirement
- **CUDA GPU** (optional): For faster processing

---

## Basic Usage

### Convert SRT to Voiceover

```bash
# Basic conversion
srt-voiceover voiceover subtitles.srt -o output.mp3

# With custom voice and settings
srt-voiceover voiceover subtitles.srt -o output.mp3 \
  --default-voice "en-US-JennyNeural" \
  --rate "+20%" --volume "+10%"
```

### Transcribe Audio to SRT

```bash
# Basic transcription
srt-voiceover transcribe audio.mp3 -o output.srt

# With speaker detection
srt-voiceover transcribe audio.mp3 -o output.srt --use-pyannote

# From video file
srt-voiceover transcribe video.mp4 -o output.srt
```

### Complete Workflow (Audio → SRT → New Voice)

```bash
# One-command dubbing
srt-voiceover revoice input.mp4 -o output.mp3 \
  --use-word-timing --elastic-timing

# With speaker detection
srt-voiceover revoice podcast.mp3 -o new_voice.mp3 \
  --use-pyannote --use-word-timing --elastic-timing
```

---

## Voice Timing Modes

Choose the right timing mode for your content:

### 1. Default Mode (Fast & Natural)

**Best for:** Audio-only content (podcasts, audiobooks)

```bash
srt-voiceover revoice audio.mp3 -o output.mp3
```

**Characteristics:**
- ✅ Very natural-sounding
- ✅ Fast processing
- ⚠️ May drift slightly from original timing
- ⚠️ Not ideal for strict lip-sync

### 2. Word-Level Timing (Dynamic Pacing)

**Best for:** Screen recordings, tutorials without visible faces

```bash
srt-voiceover revoice video.mp4 -o output.mp3 --use-word-timing
```

**Characteristics:**
- ✅ Excellent timing accuracy
- ✅ Matches original pacing variations
- ⚠️ Speed variations may be noticeable

### 3. Elastic Timing with Smoothing (Recommended)

**Best for:** Video dubbing with visible speakers

```bash
srt-voiceover revoice video.mp4 -o output.mp3 \
  --use-word-timing --elastic-timing
```

**Characteristics:**
- ✅ Excellent timing accuracy
- ✅ Most natural-sounding transitions
- ✅ Perfect for professional lip-sync
- ✅ Smooth pacing changes (no jarring jumps)

**How it works:**
- Extracts word-level timestamps from Whisper
- Calculates dynamic speaking rates per segment
- Expands timing windows by borrowing from gaps
- Smooths rate changes (max 15% per segment)

**Example output:**
```
[SMOOTHING] Applied rate smoothing to 6/18 segments

Segment 1: +29%
Segment 2: +14% (smoothed from +12%)
Segment 3: -1% (smoothed from -4%)
Segment 4: +14% (smoothed from +40%)  ← Big improvement!
```

---

## Two-Step Workflow

Edit transcriptions before generating voiceovers - perfect for fixing transcription errors.

### Step 1: Transcribe with Word Timings

```bash
srt-voiceover transcribe video.mp4 -o transcript.srt --save-word-timings
```

**Creates:**
- `transcript.srt` - Editable subtitle file
- `transcript_word_timings.json` - Word timestamps (don't edit!)

### Step 2: Edit the SRT

Open `transcript.srt` in any text editor and fix errors:
- Fix spelling: "recieve" → "receive"
- Fix homophones: "their" → "there"
- Fix names and technical terms
- Add punctuation

### Step 3: Generate Corrected Voiceover

```bash
srt-voiceover voiceover transcript.srt -o output.mp3 \
  --word-timings transcript_word_timings.json \
  --elastic-timing
```

### Editing Guidelines

**✅ Safe Edits (Timing Still Works)**
- Fix spelling and punctuation
- Fix homophones and capitalization
- Correct names and technical terms

**⚠️ Use Caution**
- Adding/removing single words
- Minor reordering

**❌ Avoid (Timing Won't Match)**
- Complete rewrites
- Adding/removing entire sentences
- Major structural changes

---

## Advanced Features

### Multi-Speaker Support

**Automatic Speaker Detection:**
```bash
# Basic heuristic detection
srt-voiceover revoice audio.mp3 -o output.mp3 --multi-speaker

# Professional ML-based (requires HF_TOKEN)
srt-voiceover revoice audio.mp3 -o output.mp3 --use-pyannote
```

**Manual Speaker Assignment:**

Create `config.yaml`:
```yaml
speaker_voices:
  Alice: "en-US-EmmaMultilingualNeural"
  Bob: "en-US-AndrewMultilingualNeural"
  Speaker A: "en-US-JennyNeural"
  Speaker B: "en-US-GuyNeural"
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

### GPU Acceleration

GPU acceleration is automatic if CUDA is available:

```bash
# Install PyTorch with CUDA
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121

# Install features
pip install srt-voiceover[cuda]

# Use normally (GPU detected automatically)
srt-voiceover revoice video.mp4 -o output.mp3 --use-word-timing
```

### Video Dubbing Pipeline

```bash
# 1. Extract and re-voice
srt-voiceover revoice video.mp4 -o dubbed_audio.mp3 \
  --use-word-timing --elastic-timing

# 2. Merge audio with video
ffmpeg -i video.mp4 -i dubbed_audio.mp3 \
  -c:v copy -map 0:v:0 -map 1:a:0 output.mp4
```

### Voice Customization

```bash
# Adjust speech parameters
srt-voiceover voiceover script.srt -o output.mp3 \
  --default-voice "en-US-AndrewMultilingualNeural" \
  --rate "+20%" \    # Speed (−50% to +100%)
  --volume "+10%" \  # Volume (−50% to +100%)
  --pitch "-10Hz"    # Pitch (−50Hz to +100Hz)
```

### List Available Voices

```bash
# Show all 400+ voices
srt-voiceover --list-voices

# Filter by language
srt-voiceover --list-voices | grep "en-US"
```

---

## Configuration

### Configuration File

Create `config.yaml`:

```yaml
# Voice Settings
default_voice: "en-US-AndrewMultilingualNeural"
rate: "+0%"
volume: "+0%"
pitch: "+0Hz"

# Timing Options
timing_tolerance_ms: 200
use_word_timing: true
elastic_timing: true

# Transcription
whisper_model: "base"
use_whisper_api: false

# Speaker Diarization
use_pyannote: false

# Speaker to Voice Mapping
speaker_voices:
  Nathan: "en-US-AndrewMultilingualNeural"
  Nicole: "en-US-EmmaMultilingualNeural"
  Speaker A: "en-US-GuyNeural"
  Speaker B: "en-US-JennyNeural"
```

**Use with any command:**
```bash
srt-voiceover revoice audio.mp3 -o output.mp3 -c config.yaml
```

### Environment Variables

```bash
# HuggingFace token for pyannote.audio
export HF_TOKEN=hf_your_token_here

# Windows PowerShell
[System.Environment]::SetEnvironmentVariable('HF_TOKEN', 'hf_your_token_here', 'User')
```

---

## API Reference

### Python API

```python
from srt_voiceover.core import build_voiceover_from_srt
from srt_voiceover.transcribe import (
    transcribe_audio_to_srt,
    audio_to_voiceover_workflow
)

# Convert SRT to voiceover
build_voiceover_from_srt(
    srt_path="subtitles.srt",
    output_audio_path="output.mp3",
    default_voice="en-US-AndrewMultilingualNeural",
    rate="+20%",
    volume="+0%",
    pitch="+0Hz",
    word_timings=word_timings,  # Optional
    elastic_timing=True,         # Optional
    verbose=True
)

# Transcribe audio to SRT
srt_path = transcribe_audio_to_srt(
    audio_path="audio.mp3",
    output_srt_path="output.srt",
    model="base",
    language="en",
    use_pyannote=False,
    device="auto",
    use_word_timing=True,
    save_word_timings_path="output_word_timings.json"
)

# Complete workflow
srt_path, audio_path = audio_to_voiceover_workflow(
    input_audio="input.mp4",
    output_audio="output.mp3",
    default_voice="en-US-AndrewMultilingualNeural",
    whisper_model="base",
    use_word_timing=True,
    elastic_timing=True,
    use_pyannote=False,
    device="auto",
    verbose=True
)
```

### CLI Commands

```bash
# Voiceover generation
srt-voiceover voiceover INPUT.srt [OPTIONS]
  -o, --output PATH          Output audio file
  --default-voice NAME       Voice to use
  --rate PERCENT            Speech rate
  --volume PERCENT          Volume level
  --pitch HZ                Pitch adjustment
  --word-timings PATH       Word timings JSON
  --elastic-timing          Enable elastic timing
  -c, --config PATH         Config file

# Audio transcription
srt-voiceover transcribe INPUT [OPTIONS]
  -o, --output PATH         Output SRT file
  --model NAME              Whisper model (tiny/base/small/medium/large)
  --language CODE           Language code (en, es, fr, etc.)
  --multi-speaker           Enable speaker detection
  --use-pyannote            Use professional diarization
  --save-word-timings       Save word timings to JSON
  --device auto|cpu|cuda    Processing device

# Complete workflow
srt-voiceover revoice INPUT [OPTIONS]
  -o, --output PATH         Output audio file
  --use-word-timing         Enable word-level timing
  --elastic-timing          Enable elastic timing
  --use-pyannote            Use professional diarization
  (combines transcribe + voiceover options)

# Utilities
srt-voiceover --list-voices          List all available voices
srt-voiceover --version              Show version
srt-voiceover --init-config          Generate config.yaml
```

---

## Troubleshooting

### Common Issues

**"FFmpeg not found"**
- Install FFmpeg and add to PATH
- Windows: Download from ffmpeg.org
- Mac: `brew install ffmpeg`
- Linux: `sudo apt install ffmpeg`

**"GPU not detected"**
```bash
# Install CUDA-enabled PyTorch first
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121

# Then install features
pip install srt-voiceover[cuda]
```

**"Word timings file not found"**
```bash
# Use --save-word-timings when transcribing
srt-voiceover transcribe video.mp4 -o output.srt --save-word-timings
```

**"Elastic timing requires word timings"**
```bash
# Provide word timings JSON when using elastic timing
srt-voiceover voiceover script.srt -o output.mp3 \
  --word-timings script_word_timings.json --elastic-timing
```

**"Speech sounds rushed/robotic"**
- Try elastic timing: `--elastic-timing`
- Reduce global rate: `--rate "-10%"`
- Use default mode without word timing

**"Timing drifts over time"**
- Enable word-level timing: `--use-word-timing`
- Use elastic timing: `--elastic-timing`

**"Pyannote authentication error"**
```bash
# Set HuggingFace token
export HF_TOKEN=hf_your_token_here

# Accept license at:
# https://huggingface.co/pyannote/speaker-diarization-3.1
```

### Performance Tips

1. **Use appropriate Whisper model:**
   - `tiny` - Fastest, less accurate
   - `base` - Good balance (default)
   - `small` - Better accuracy
   - `medium` - High accuracy
   - `large` - Best accuracy, slowest

2. **GPU acceleration:**
   - 5-10x faster for transcription
   - 3-5x faster for diarization
   - Install CUDA PyTorch + `srt-voiceover[cuda]`

3. **Processing time estimates:**
   - Default mode: ~1-2min per minute of audio (TTS only)
   - Word-level: +15-20% (includes transcription)
   - With pyannote: +30-40% (includes diarization)

### Getting Help

- **GitHub Issues**: https://github.com/leakydata/srt-voiceover/issues
- **Discussions**: https://github.com/leakydata/srt-voiceover/discussions
- **Documentation**: Check this file and README.md

---

## Advanced Use Cases

### Multi-Language Translation Dubbing

```bash
# 1. Transcribe original
srt-voiceover transcribe english_video.mp4 -o english.srt --save-word-timings

# 2. Translate SRT to Spanish (use any translation service)
# Keep timing, translate text → spanish.srt

# 3. Generate Spanish voiceover
srt-voiceover voiceover spanish.srt -o spanish_audio.mp3 \
  --word-timings english_word_timings.json \
  --default-voice "es-ES-ElviraNeural"

# 4. Create Spanish version
ffmpeg -i english_video.mp4 -i spanish_audio.mp3 \
  -c:v copy -map 0:v:0 -map 1:a:0 spanish_video.mp4
```

### Podcast Cleanup

```bash
# 1. Transcribe with word timings
srt-voiceover transcribe raw_podcast.mp3 -o podcast.srt --save-word-timings

# 2. Edit SRT to remove filler words, fix mistakes

# 3. Generate clean version
srt-voiceover voiceover podcast.srt -o clean_podcast.mp3 \
  --word-timings podcast_word_timings.json \
  --elastic-timing
```

### Batch Processing

```bash
#!/bin/bash
# Process multiple videos

for video in *.mp4; do
  base="${video%.mp4}"
  
  # Transcribe
  srt-voiceover transcribe "$video" -o "${base}.srt" --save-word-timings
  
  # Generate voiceover
  srt-voiceover voiceover "${base}.srt" -o "${base}_dubbed.mp3" \
    --word-timings "${base}_word_timings.json" \
    --elastic-timing
  
  # Merge with video
  ffmpeg -i "$video" -i "${base}_dubbed.mp3" \
    -c:v copy -map 0:v:0 -map 1:a:0 "${base}_final.mp4"
done
```

---

## License

MIT License - See LICENSE file for details.

## Credits

- **Whisper**: OpenAI's speech recognition model
- **Edge TTS**: Microsoft's text-to-speech service
- **Pyannote.audio**: Speaker diarization toolkit
- **FFmpeg**: Audio/video processing

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for development setup and guidelines.

