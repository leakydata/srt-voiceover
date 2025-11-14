# 🎤 NEW FEATURE: Audio Transcription & Re-voicing

## What's New in v0.2.0

Your srt-voiceover package now has **complete dubbing workflow capabilities**!

### Before (v0.1.0)
- ✅ SRT → Voiceover audio

### After (v0.2.0)
- ✅ SRT → Voiceover audio
- ✅ **Audio → SRT (NEW!)**
- ✅ **Audio → Transcribe → Re-voice (NEW!)**
- ✅ **Video → Extract audio (NEW!)**

---

## New Commands

### 1. `transcribe` - Audio to SRT
Convert any audio file to subtitles with timestamps:

```bash
srt-voiceover transcribe podcast.mp3 -o subtitles.srt --config config.yaml
```

**Features:**
- Automatic transcription using Whisper
- Speaker detection (Speaker A, Speaker B, etc.)
- Support for 50+ languages
- Timestamps automatically synchronized

### 2. `revoice` - Complete Workflow
One command to transcribe AND re-voice:

```bash
srt-voiceover revoice original.mp3 -o new_voices.mp3 --config config.yaml
```

**What it does:**
1. Transcribes audio to SRT with speaker detection
2. Maps speakers to voices from your config
3. Generates new audio with different voices
4. Perfect for voice replacement!

### 3. `extract-audio` - Video Processing
Extract audio from video files:

```bash
srt-voiceover extract-audio video.mp4 -o audio.wav
```

---

## Use Cases

### 🎙️ Podcast Re-voicing
Replace podcast voices while keeping the same content and timing:

```bash
# Before: Original podcast with real voices
# After: Same content with AI voices

srt-voiceover revoice podcast_ep1.mp3 -o ai_podcast_ep1.mp3 --config config.yaml
```

**Why?**
- Test different voice combinations
- Create anonymous versions
- Consistent voice across episodes
- Multi-language versions

### 🎬 Video Dubbing
Complete video dubbing pipeline:

```bash
# 1. Extract audio from video
srt-voiceover extract-audio original_video.mp4 -o audio.wav

# 2. Transcribe and re-voice
srt-voiceover revoice audio.wav -o dubbed_audio.mp3 --keep-srt -c config.yaml

# 3. Merge back with video (using ffmpeg)
ffmpeg -i original_video.mp4 -i dubbed_audio.mp3 -c:v copy -map 0:v:0 -map 1:a:0 dubbed_video.mp4
```

### 📝 Subtitle Generation
Create subtitles from audio:

```bash
srt-voiceover transcribe video_audio.wav -o subtitles.srt --language en
```

### 🔄 Voice Replacement
Change all voices in existing audio:

```bash
# Original: Nathan and Nicole talking
# Result: Andrew and Emma talking (different voices, same conversation)

srt-voiceover revoice interview.mp3 -o revoiced_interview.mp3 -c config.yaml
```

---

## Configuration Updates

Your config file now supports transcription:

```yaml
# Edge TTS API endpoint (for text-to-speech)
edge_tts_url: "http://localhost:5050/v1/audio/speech"

# Whisper API endpoint (for speech-to-text) - NEW!
whisper_url: "http://localhost:5050/v1/audio/transcriptions"

# API key for authentication
api_key: "your_api_key_here"

# Speaker voice mapping
# Works for both manual SRT and auto-detected speakers
speaker_voices:
  Nathan: "en-US-AndrewMultilingualNeural"
  Nicole: "en-US-EmmaMultilingualNeural"
  Speaker A: "en-US-GuyNeural"      # Auto-detected speakers
  Speaker B: "en-US-JennyNeural"
```

---

## Python API

### Transcription

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

### Complete Workflow

```python
from srt_voiceover import audio_to_voiceover_workflow

# Magic function! Does transcription + re-voicing in one call
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
    language="en"
)

print(f"Created: {srt_path} and {audio_path}")
```

---

## Technical Details

### Speaker Detection

The package includes basic speaker detection that alternates between speakers based on timing and patterns. For production use, consider:

- **Manual editing**: Review and edit the generated SRT file
- **Custom logic**: Use Python API to implement your own detection
- **Future**: Advanced diarization with pyannote.audio (coming soon)

### Supported Audio Formats

- **Input**: MP3, WAV, M4A, FLAC, OGG (anything FFmpeg supports)
- **Output**: MP3, WAV
- **Video**: MP4, AVI, MKV, MOV (audio extraction)

### Languages Supported

All languages supported by Whisper:
- English, Spanish, French, German, Italian, Portuguese
- Japanese, Korean, Chinese, Arabic, Russian
- And 40+ more...

---

## File Structure Changes

```
srt-voiceover/
├── src/srt_voiceover/
│   ├── __init__.py          # Updated with new exports
│   ├── core.py              # Original voiceover generation
│   ├── cli.py               # Updated with new commands
│   └── transcribe.py        # NEW! Transcription features
├── examples/
│   ├── config.yaml          # Updated with whisper_url
│   └── sample.srt
├── WORKFLOWS.md             # NEW! Complete workflow examples
├── TRANSCRIPTION_FEATURE.md # NEW! This file
└── README.md                # Updated with new features
```

---

## Examples

### Example 1: Simple Transcription

```bash
srt-voiceover transcribe interview.mp3 -o subtitles.srt
```

**Output (subtitles.srt)**:
```srt
1
00:00:00,000 --> 00:00:03,500
Speaker A: Welcome to today's interview.

2
00:00:03,500 --> 00:00:07,000
Speaker B: Thanks for having me on the show!
```

### Example 2: Re-voice with Different Speeds

```bash
# Slower, more dramatic
srt-voiceover revoice podcast.mp3 -o dramatic.mp3 --speed 0.9 -c config.yaml

# Faster, more energetic
srt-voiceover revoice podcast.mp3 -o energetic.mp3 --speed 1.2 -c config.yaml
```

### Example 3: Keep SRT for Editing

```bash
# Generate with --keep-srt
srt-voiceover revoice interview.mp3 -o version1.mp3 --keep-srt -c config.yaml

# Edit the generated SRT file
code interview.srt  # Fix speaker names, correct errors

# Regenerate from edited SRT
srt-voiceover interview.srt -o version2.mp3 -c config.yaml
```

---

## Performance Notes

- **Transcription**: Depends on audio length and Whisper model
- **Voice Generation**: Same speed as before
- **Complete Workflow**: Sum of both operations

**Tips**:
- Use `--quiet` flag for faster processing
- Process long files in chunks
- Cache transcriptions with `--keep-srt`

---

## Limitations & Future Improvements

### Current Limitations
- Basic speaker detection (alternating pattern)
- No emotion/style control in transcription
- Single-file processing (no batch mode yet)

### Coming Soon
- Advanced speaker diarization (pyannote.audio)
- Batch processing mode
- GUI for reviewing/editing
- Direct video output
- More TTS engine options

---

## Migration Guide

If you're upgrading from v0.1.0:

### Old Workflow
```bash
# Had to manually create SRT files
srt-voiceover subtitles.srt -o output.mp3 -c config.yaml
```

### New Workflow Options

**Option 1: Still works exactly the same**
```bash
srt-voiceover subtitles.srt -o output.mp3 -c config.yaml
```

**Option 2: Generate SRT from audio first**
```bash
srt-voiceover transcribe audio.mp3 -o subtitles.srt -c config.yaml
srt-voiceover subtitles.srt -o output.mp3 -c config.yaml
```

**Option 3: Do both in one command**
```bash
srt-voiceover revoice audio.mp3 -o output.mp3 -c config.yaml
```

**No breaking changes!** All old code still works.

---

## Need Help?

- **Quick Start**: See [QUICKSTART.md](QUICKSTART.md)
- **Workflows**: See [WORKFLOWS.md](WORKFLOWS.md)
- **Full Docs**: See [README.md](README.md)
- **Issues**: [GitHub Issues](https://github.com/leakydata/srt-voiceover/issues)

---

**Enjoy the new features! 🎉**

You now have a complete dubbing pipeline from audio input to voiced output!

