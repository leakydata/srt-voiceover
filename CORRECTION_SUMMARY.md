# ✅ Transcription Feature - CORRECTED

## What Was Wrong

Initially, the transcription feature incorrectly assumed that the **localhost:5050** Edge TTS server provided Whisper transcription endpoints. 

**Reality:**
- `http://localhost:5050` = **Edge TTS ONLY** (text → speech)
- It does NOT provide speech-to-text/Whisper endpoints

## What Was Fixed

The transcription feature now uses **OpenAI Whisper locally** by default!

### NEW Approach (v0.2.0)

**Two modes available:**

#### 1. Local Mode (DEFAULT - Recommended) ✅
- Uses `openai-whisper` Python library
- Runs completely on your machine
- No server needed for transcription!
- Works offline
- Free (no API costs)

**Installation:**
```bash
pip install openai-whisper
```

**Usage:**
```bash
# Transcribe locally (no server needed!)
srt-voiceover transcribe audio.mp3 -o output.srt

# Complete workflow (local transcription + Edge TTS for voices)
srt-voiceover revoice podcast.mp3 -o new_podcast.mp3 -c config.yaml
```

#### 2. API Mode (Optional)
- For OpenAI API users
- Or custom Whisper API servers
- Requires configuration

**Setup:**
```yaml
use_whisper_api: true
whisper_api_url: "https://api.openai.com/v1/audio/transcriptions"
whisper_api_key: "sk-your-api-key"
```

---

## What You Need Now

### For SRT → Voiceover (Original Feature)
```bash
# 1. Start Edge TTS server
cd openai-edge-tts
npm start

# 2. Use srt-voiceover
srt-voiceover subtitles.srt -o voiceover.mp3 -c config.yaml
```

### For Audio → SRT (Transcription - NEW!)
```bash
# 1. Install Whisper (one time)
pip install openai-whisper

# 2. Transcribe (no server needed!)
srt-voiceover transcribe audio.mp3 -o subtitles.srt
```

### For Complete Workflow (Audio → Transcribe → Re-voice)
```bash
# 1. Install Whisper
pip install openai-whisper

# 2. Start Edge TTS server (separate terminal)
cd openai-edge-tts
npm start

# 3. Run complete workflow
srt-voiceover revoice podcast.mp3 -o new_podcast.mp3 -c config.yaml
```

---

## Architecture Summary

```
┌─────────────────────────────────────────────────────────┐
│                   srt-voiceover Package                  │
├─────────────────────────────────────────────────────────┤
│                                                          │
│  Feature 1: SRT → Voiceover                             │
│  ┌──────────┐      ┌──────────────────┐                │
│  │   SRT    │ ───► │  Edge TTS Server │ ───► Audio     │
│  │   File   │      │  localhost:5050  │                 │
│  └──────────┘      └──────────────────┘                 │
│                                                          │
│  Feature 2: Audio → SRT (NEW!)                          │
│  ┌──────────┐      ┌──────────────────┐                │
│  │  Audio   │ ───► │  Local Whisper   │ ───► SRT       │
│  │   File   │      │  (on your PC)    │                 │
│  └──────────┘      └──────────────────┘                 │
│                                                          │
│  Feature 3: Complete Workflow (NEW!)                    │
│  ┌──────────┐      ┌────────┐      ┌────────┐          │
│  │  Audio   │ ───► │Whisper │ ───► │EdgeTTS │ ───► New│
│  │  Input   │      │(local) │      │(server)│     Audio│
│  └──────────┘      └────────┘      └────────┘          │
│                                                          │
└─────────────────────────────────────────────────────────┘
```

---

## Configuration Changes

### Old (Incorrect)
```yaml
edge_tts_url: "http://localhost:5050/v1/audio/speech"
whisper_url: "http://localhost:5050/v1/audio/transcriptions"  # ❌ WRONG!
api_key: "your_api_key"
```

### New (Correct)
```yaml
# Edge TTS for voiceover generation
edge_tts_url: "http://localhost:5050/v1/audio/speech"
api_key: "your_api_key"

# Whisper for transcription (uses LOCAL library by default)
whisper_model: "base"  # Model size: tiny/base/small/medium/large
use_whisper_api: false  # Only set to true for OpenAI API

# Optional: if using OpenAI API instead of local
# use_whisper_api: true
# whisper_api_url: "https://api.openai.com/v1/audio/transcriptions"
# whisper_api_key: "sk-your-openai-key"

speaker_voices:
  Speaker A: "en-US-AndrewMultilingualNeural"
  Speaker B: "en-US-EmmaMultilingualNeural"
```

---

## Benefits of This Approach

✅ **Works Out of the Box**: Just `pip install openai-whisper`  
✅ **No Extra Servers**: Only need Edge TTS server  
✅ **Offline Support**: Transcription works without internet  
✅ **Privacy**: Audio never leaves your machine  
✅ **Free**: No API costs for transcription  
✅ **Fast**: GPU acceleration if available  
✅ **Flexible**: Can still use API if you prefer  

---

## Migration Guide

If you started using the transcription feature before this fix:

### What Changed
1. **Removed dependency** on localhost:5050 for transcription
2. **Added** openai-whisper as optional dependency
3. **Changed** function parameters (removed `whisper_url`, added `whisper_model`)

### What You Need to Do
1. Install Whisper:
   ```bash
   pip install openai-whisper
   ```

2. Update your config (if you have one):
   ```yaml
   # REMOVE this line:
   # whisper_url: "http://localhost:5050/v1/audio/transcriptions"
   
   # ADD this line:
   whisper_model: "base"
   ```

3. That's it! Everything else works the same.

---

## Documentation

- **Setup Guide**: See [TRANSCRIPTION_SETUP.md](TRANSCRIPTION_SETUP.md)
- **Complete Workflows**: See [WORKFLOWS.md](WORKFLOWS.md)
- **Main README**: See [README.md](README.md)

---

## Questions?

**Q: Do I still need the localhost:5050 server?**  
A: Yes, but ONLY for voiceover generation (SRT → Audio). Not for transcription!

**Q: Can I still use an API for transcription?**  
A: Yes! Set `use_whisper_api: true` in your config and provide API details.

**Q: Which is better - local or API?**  
A: Local is recommended (free, private, offline). API is useful if you have OpenAI credits or no GPU.

**Q: Will this cost more?**  
A: No! Local Whisper is completely free. API mode costs only if you use OpenAI.

---

Thank you for catching that issue! The feature is now much better. 🎉

