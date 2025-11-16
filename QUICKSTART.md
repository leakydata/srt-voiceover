# Quick Start Guide

Get started with srt-voiceover in 5 minutes.

## Installation

```bash
# Basic installation
pip install srt-voiceover

# With transcription support
pip install srt-voiceover[transcription]

# Everything (CPU)
pip install srt-voiceover[all]
```

**Required:** Install [FFmpeg](https://ffmpeg.org/download.html) and add to PATH

## 30-Second Tutorial

### 1. Convert SRT to Voiceover

```bash
srt-voiceover voiceover subtitles.srt -o output.mp3
```

###2. Transcribe Audio to SRT

```bash
srt-voiceover transcribe audio.mp3 -o output.srt
```

### 3. Re-voice an Entire Video

```bash
srt-voiceover revoice video.mp4 -o new_audio.mp3 --use-word-timing --elastic-timing
```

## Common Use Cases

### Video Dubbing

```bash
# 1. Extract and re-voice with perfect timing
srt-voiceover revoice video.mp4 -o dubbed_audio.mp3 --use-word-timing --elastic-timing

# 2. Merge audio back into video
ffmpeg -i video.mp4 -i dubbed_audio.mp3 -c:v copy -map 0:v:0 -map 1:a:0 output.mp4
```

### Fix Transcription Errors

```bash
# 1. Transcribe and save word timings
srt-voiceover transcribe video.mp4 -o transcript.srt --save-word-timings

# 2. Edit transcript.srt to fix errors (use any text editor)

# 3. Generate corrected voiceover
srt-voiceover voiceover transcript.srt -o fixed.mp3 \
  --word-timings transcript_word_timings.json --elastic-timing
```

### Multi-Speaker Content

```bash
# With automatic speaker detection
srt-voiceover revoice podcast.mp3 -o new_voices.mp3 --use-pyannote --use-word-timing

# Note: Requires HF_TOKEN environment variable
# Get token at: https://huggingface.co/settings/tokens
```

## Voice Selection

```bash
# List all 400+ available voices
srt-voiceover --list-voices

# Use specific voice
srt-voiceover voiceover script.srt -o output.mp3 --default-voice "en-US-JennyNeural"
```

## Configuration File (Optional)

Create `config.yaml`:

```yaml
default_voice: "en-US-AndrewMultilingualNeural"
rate: "+0%"
volume: "+0%"
use_word_timing: true
elastic_timing: true
```

Use it:

```bash
srt-voiceover revoice video.mp4 -o output.mp3 -c config.yaml
```

## GPU Acceleration (Optional)

For 5-10x faster processing on NVIDIA GPUs:

```bash
# 1. Install CUDA PyTorch
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121

# 2. Install CUDA features
pip install srt-voiceover[cuda]

# 3. Use normally (GPU detected automatically)
srt-voiceover revoice video.mp4 -o output.mp3 --use-word-timing
```

## Timing Modes Explained

| Mode | Command | Best For |
|------|---------|----------|
| **Default** | (no flags) | Audio-only content, fastest |
| **Word-Level** | `--use-word-timing` | Screen recordings, tutorials |
| **Elastic** | `--use-word-timing --elastic-timing` | Video dubbing, lip-sync |

**Recommendation:** Use `--use-word-timing --elastic-timing` for best quality video dubbing.

## Next Steps

- **Full Documentation:** See [DOCUMENTATION.md](DOCUMENTATION.md)
- **Voice List:** Run `srt-voiceover --list-voices`
- **Config Example:** Run `srt-voiceover --init-config`
- **Help:** Run `srt-voiceover --help`

## Getting Help

- GitHub Issues: https://github.com/leakydata/srt-voiceover/issues
- Discussions: https://github.com/leakydata/srt-voiceover/discussions
