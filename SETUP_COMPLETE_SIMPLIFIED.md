# 🎉 MAJOR SIMPLIFICATION - No Server Needed!

## What Changed

We've **eliminated the Node.js server requirement** by using the [`edge-tts` Python module](https://github.com/rany2/edge-tts) directly!

### Before (Complex)
1. Install Node.js
2. Clone openai-edge-tts repo
3. Run `npm install` 
4. Keep server running (`npm start`)
5. Configure server URL in config
6. Install srt-voiceover

### After (Simple)  
1. Install srt-voiceover: `pip install edge-tts pysrt pydub pyyaml`
2. Done! ✅

## Key Changes

### Dependencies
- ❌ **Removed**: Node.js, npm, openai-edge-tts server
- ✅ **Added**: `edge-tts` Python module (9.3k stars on GitHub)
- ✅ **Kept**: FFmpeg (still needed for audio processing)

### Configuration
**Old config.yaml:**
```yaml
edge_tts_url: "http://localhost:5050/v1/audio/speech"
api_key: "your_api_key_here"
speed: 1.0  # multiplier
```

**New config.yaml:**
```yaml
rate: "+0%"     # Edge TTS native format
volume: "+0%"
pitch: "+0Hz"
```

### Code Changes
- Parameters changed from `speed` to `rate`, `volume`, `pitch`
- Removed `edge_tts_url` and `api_key` parameters
- Uses `edge_tts.Communicate` directly (async)
- All TTS now runs locally via Microsoft's free service

## Benefits

✅ **Simpler installation** - Just pip install  
✅ **Fewer dependencies** - No Node.js needed  
✅ **More reliable** - One less service to manage  
✅ **Same quality** - Uses the same Microsoft Edge TTS  
✅ **Same voices** - All 70+ voices still available  
✅ **No servers** - Everything runs in Python  

## Migration Guide

If you've been using the old version:

1. **Uninstall the server** (optional, no longer needed):
   ```bash
   # You can delete the openai-edge-tts folder
   ```

2. **Update your code**:
   ```python
   # OLD
   build_voiceover_from_srt(
       srt_path="input.srt",
       output_audio_path="output.mp3",
       edge_tts_url="http://localhost:5050/v1/audio/speech",
       api_key="key",
       speed=1.2
   )
   
   # NEW  
   build_voiceover_from_srt(
       srt_path="input.srt",
       output_audio_path="output.mp3",
       rate="+20%"  # equivalent to speed=1.2
   )
   ```

3. **Update config.yaml**:
   - Remove `edge_tts_url`
   - Remove `api_key`
   - Change `speed: 1.2` to `rate: "+20%"`

## Installation Now

```bash
# Install core package
pip install pysrt pydub pyyaml edge-tts

# Optional: transcription
pip install openai-whisper

# Or install everything
pip install -e .[all]
```

## Usage Examples

### Simple voiceover
```bash
srt-voiceover input.srt -o output.mp3
```

### With rate adjustment
```bash
srt-voiceover input.srt -o output.mp3 --rate "+20%"
```

### Complete workflow (transcribe + re-voice)
```bash
# No server setup needed!
srt-voiceover revoice podcast.mp3 -o new_podcast.mp3
```

## What You DON'T Need Anymore

❌ Node.js  
❌ npm  
❌ openai-edge-tts repository  
❌ Server running in background  
❌ Server URL configuration  
❌ API keys for Edge TTS  

## What You DO Need

✅ Python 3.7+  
✅ FFmpeg (for audio processing)  
✅ `pip install edge-tts`  
✅ Optional: `pip install openai-whisper` (for transcription)  

---

**This is a HUGE improvement!** The package is now much easier to use and maintain. 🎉

