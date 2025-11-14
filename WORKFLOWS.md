# 🔄 Complete Workflow Examples

This document shows real-world use cases and complete workflows for srt-voiceover.

## Table of Contents
- [Basic Workflows](#basic-workflows)
- [Advanced Use Cases](#advanced-use-cases)
- [Video Dubbing](#video-dubbing)
- [Podcast Re-voicing](#podcast-re-voicing)
- [Multi-Language Content](#multi-language-content)

---

## Basic Workflows

### Workflow 1: Convert Existing SRT to Voiceover

**Use Case**: You have subtitles and want to generate audio.

```bash
# Step 1: Create config
srt-voiceover --init-config config.yaml

# Step 2: Edit config.yaml with your voice preferences

# Step 3: Generate voiceover
srt-voiceover subtitles.srt -o voiceover.mp3 --config config.yaml
```

**When to use**: 
- You already have subtitles
- Creating voiceover for silent videos
- Generating audiobooks from text

---

### Workflow 2: Transcribe Audio to SRT

**Use Case**: You have audio and need subtitles.

```bash
# Transcribe audio
srt-voiceover transcribe podcast.mp3 -o subtitles.srt --config config.yaml

# Review and edit subtitles if needed (manual step)
# Open subtitles.srt in a text editor and adjust speaker names

# Optionally: Generate new voiceover from edited subtitles
srt-voiceover subtitles.srt -o final_audio.mp3 --config config.yaml
```

**When to use**:
- Creating subtitles for videos
- Transcribing interviews
- Converting speech to text with timestamps

---

### Workflow 3: Complete Re-voicing (One Command!)

**Use Case**: Replace all voices in existing audio.

```bash
# One command does it all: transcribe + re-voice
srt-voiceover revoice original_podcast.mp3 -o new_podcast.mp3 --config config.yaml --keep-srt
```

**What happens**:
1. Transcribes `original_podcast.mp3` to SRT
2. Detects speakers (Speaker A, Speaker B)
3. Maps speakers to voices from config
4. Generates new audio with different voices
5. Keeps the SRT file for review

**When to use**:
- Changing podcast host voices
- Creating different voice versions
- Voice replacement for privacy
- Testing different voice combinations

---

## Advanced Use Cases

### Use Case 1: Video Dubbing Pipeline

**Goal**: Dub a video into different voices while keeping the timing perfect.

```bash
# Step 1: Extract audio from video
srt-voiceover extract-audio original_video.mp4 -o original_audio.wav

# Step 2: Transcribe audio to SRT with speaker detection
srt-voiceover transcribe original_audio.wav -o subtitles.srt --config config.yaml

# Step 3: Review and edit SRT file
# Open subtitles.srt and:
# - Fix speaker names
# - Correct any transcription errors
# - Adjust timing if needed

# Step 4: Generate new voiceover
srt-voiceover subtitles.srt -o dubbed_audio.mp3 --config config.yaml

# Step 5: Merge new audio with video (use video editing software)
# Tools: FFmpeg, DaVinci Resolve, Adobe Premiere, etc.
```

**FFmpeg command to merge audio and video**:
```bash
ffmpeg -i original_video.mp4 -i dubbed_audio.mp3 -c:v copy -map 0:v:0 -map 1:a:0 -shortest dubbed_video.mp4
```

---

### Use Case 2: Podcast Re-voicing with Custom Voices

**Goal**: Take an existing podcast and create a version with AI voices.

**config.yaml**:
```yaml
edge_tts_url: "http://localhost:5050/v1/audio/speech"
whisper_url: "http://localhost:5050/v1/audio/transcriptions"
api_key: "your_api_key"
speed: 1.05  # Slightly faster

speaker_voices:
  # Map detected speakers to specific voices
  Speaker A: "en-US-AndrewMultilingualNeural"   # Host
  Speaker B: "en-US-EmmaMultilingualNeural"     # Co-host
  Speaker C: "en-US-BrianNeural"                 # Guest
  
default_voice: "en-US-GuyNeural"
```

**Command**:
```bash
srt-voiceover revoice podcast_episode.mp3 -o ai_version.mp3 -c config.yaml --keep-srt
```

**Post-processing**:
```bash
# Review generated subtitles
code podcast_episode.srt

# If speakers are wrong, edit the SRT file and regenerate:
srt-voiceover podcast_episode.srt -o ai_version_fixed.mp3 -c config.yaml
```

---

### Use Case 3: Multi-Language Content Creation

**Goal**: Create the same content in multiple languages/voices.

```bash
# Step 1: Create English version
srt-voiceover english_script.srt -o english_version.mp3 --config config_en.yaml

# Step 2: Translate SRT file (manual or using translation tool)
# Create spanish_script.srt, french_script.srt, etc.

# Step 3: Generate other language versions
srt-voiceover spanish_script.srt -o spanish_version.mp3 --config config_es.yaml
srt-voiceover french_script.srt -o french_version.mp3 --config config_fr.yaml
```

**config_es.yaml** (Spanish):
```yaml
edge_tts_url: "http://localhost:5050/v1/audio/speech"
api_key: "your_api_key"
default_voice: "es-ES-AlvaroNeural"
speaker_voices:
  Nathan: "es-ES-AlvaroNeural"
  Nicole: "es-MX-DaliaNeural"
```

---

### Use Case 4: Creating Different Voice Versions for A/B Testing

**Goal**: Create multiple versions with different voices to test audience preference.

```bash
# Create base transcription
srt-voiceover transcribe original.mp3 -o base.srt

# Version A: Professional corporate voices
srt-voiceover base.srt -o version_a.mp3 --config config_corporate.yaml

# Version B: Friendly casual voices
srt-voiceover base.srt -o version_b.mp3 --config config_casual.yaml

# Version C: Energetic voices
srt-voiceover base.srt -o version_c.mp3 --config config_energetic.yaml
```

**config_corporate.yaml**:
```yaml
speaker_voices:
  Speaker A: "en-US-GuyNeural"      # Deep, professional
  Speaker B: "en-US-JennyNeural"    # Clear, articulate
speed: 0.95  # Slightly slower, more authoritative
```

**config_casual.yaml**:
```yaml
speaker_voices:
  Speaker A: "en-US-AndrewMultilingualNeural"  # Friendly
  Speaker B: "en-US-EmmaMultilingualNeural"    # Warm
speed: 1.05  # Slightly faster, more conversational
```

---

## Python API Workflows

### Batch Processing Multiple Files

```python
from srt_voiceover import audio_to_voiceover_workflow
from pathlib import Path

# Configuration
config = {
    "whisper_url": "http://localhost:5050/v1/audio/transcriptions",
    "edge_tts_url": "http://localhost:5050/v1/audio/speech",
    "api_key": "your_api_key",
    "speaker_voices": {
        "Speaker A": "en-US-AndrewMultilingualNeural",
        "Speaker B": "en-US-EmmaMultilingualNeural",
    },
}

# Process all MP3 files in a directory
audio_dir = Path("./podcast_episodes")
output_dir = Path("./ai_voiced_episodes")
output_dir.mkdir(exist_ok=True)

for audio_file in audio_dir.glob("*.mp3"):
    print(f"Processing {audio_file.name}...")
    
    output_file = output_dir / f"ai_{audio_file.name}"
    srt_file = output_dir / f"{audio_file.stem}.srt"
    
    try:
        srt_path, audio_path = audio_to_voiceover_workflow(
            input_audio=str(audio_file),
            output_audio=str(output_file),
            temp_srt=str(srt_file),
            **config
        )
        print(f"✓ Created: {audio_path}")
    except Exception as e:
        print(f"✗ Error: {e}")

print("Batch processing complete!")
```

---

### Custom Speaker Detection

```python
from srt_voiceover import transcribe_audio_to_srt, build_voiceover_from_srt
import pysrt

# Step 1: Transcribe
transcribe_audio_to_srt(
    audio_path="interview.mp3",
    output_srt_path="temp.srt",
    whisper_url="http://localhost:5050/v1/audio/transcriptions",
    api_key="your_key",
    enable_speaker_detection=False  # We'll do custom detection
)

# Step 2: Custom speaker assignment based on your logic
subs = pysrt.open("temp.srt")

for i, sub in enumerate(subs):
    # Your custom logic here
    # Example: First half is Speaker A, second half is Speaker B
    if i < len(subs) // 2:
        sub.text = f"Interviewer: {sub.text}"
    else:
        sub.text = f"Guest: {sub.text}"

subs.save("final.srt")

# Step 3: Generate voiceover
build_voiceover_from_srt(
    srt_path="final.srt",
    output_audio_path="interview_revoiced.mp3",
    edge_tts_url="http://localhost:5050/v1/audio/speech",
    api_key="your_key",
    speaker_voices={
        "Interviewer": "en-US-GuyNeural",
        "Guest": "en-US-AndrewMultilingualNeural",
    }
)
```

---

## Pro Tips

### 1. Speed Optimization
- Use `--quiet` flag for faster processing (no print statements)
- Process multiple files in parallel using Python's multiprocessing
- Use WAV for faster intermediate processing, convert to MP3 at the end

### 2. Quality Improvement
- Review and edit SRT files manually for best results
- Use `--keep-srt` to save transcriptions for reuse
- Adjust `timing_tolerance_ms` if audio sounds rushed or too slow

### 3. Voice Selection
- Test different voices with short samples first
- Use multilingual voices for better pronunciation of names
- Match voice characteristics to content (formal vs casual)

### 4. Troubleshooting
- If timing is off, increase `timing_tolerance_ms` in config
- If speakers aren't detected, manually edit the SRT file
- For long files, split into chunks and process separately

---

## Real-World Example: Complete YouTube Video Dubbing

```bash
# Download video from YouTube (use yt-dlp or similar)
yt-dlp -o original.mp4 "https://youtube.com/watch?v=VIDEO_ID"

# Extract audio
srt-voiceover extract-audio original.mp4 -o original_audio.wav

# Transcribe with speaker detection
srt-voiceover transcribe original_audio.wav -o subtitles.srt --language en -c config.yaml

# Review subtitles (edit speaker names, fix errors)
code subtitles.srt

# Generate new voiceover
srt-voiceover subtitles.srt -o new_audio.mp3 -c config.yaml

# Merge with original video (mute original audio)
ffmpeg -i original.mp4 -i new_audio.mp3 -c:v copy -map 0:v:0 -map 1:a:0 -shortest dubbed_video.mp4

# Upload dubbed_video.mp4 to YouTube!
```

---

## Need Help?

- Check [README.md](README.md) for basic usage
- See [QUICKSTART.md](QUICKSTART.md) for setup instructions
- Open an issue on [GitHub](https://github.com/leakydata/srt-voiceover/issues) for support

Happy dubbing! 🎙️

