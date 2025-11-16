# Smart Time-Stretching Feature for Better Lip-Sync

## 🎯 What Is This?

**Smart Time-Stretching** makes your dubbed audio match video timing perfectly by stretching/compressing speech **without changing pitch or voice quality**. This creates natural-sounding voiceovers that sync with actors' lip movements.

## 💡 The Problem It Solves

### Old Approach (Padding/Trimming):
```
Original timing: 00:00:00 -> 00:00:05 (5 seconds)
Edge TTS generates: 4.2 seconds of audio

Solution: Add 0.8 seconds of silence at the end
Result: Actor's lips stop moving but audio continues 😞
```

### New Approach (Time-Stretching):
```
Original timing: 00:00:00 -> 00:00:05 (5 seconds)  
Edge TTS generates: 4.2 seconds of audio

Solution: Stretch audio by 19% (4.2s → 5.0s) while preserving pitch
Result: Speech naturally fills the timing, lips stay synced 🎉
```

## ✅ Works on Both CPU and GPU

**Good news!** Time-stretching is CPU-based, so it works on:
- ✅ Your laptop (CPU only)
- ✅ Your home PC (RTX 4090)
- ✅ Any system with Python

**No GPU required** for this feature (though GPU helps with transcription/diarization).

## 📦 Installation

### Basic Installation (TTS only):
```bash
pip install srt-voiceover
```

### With Time-Stretching:
```bash
pip install srt-voiceover[timestretch]
# Or install everything:
pip install srt-voiceover[all]
```

This installs:
- `librosa` - Audio time-stretching library  
- `soundfile` - Audio file I/O

## 🚀 Usage

### Command Line

#### Enable for SRT → Voiceover:
```bash
# Without time-stretch (old behavior)
srt-voiceover input.srt -o output.mp3

# With time-stretch (better lip-sync!)
srt-voiceover input.srt -o output.mp3 --enable-time-stretch
```

#### Enable for Complete Workflow (Transcribe + Re-voice):
```bash
# Transcribe video and re-voice with time-stretching
srt-voiceover revoice video.mp4 -o dubbed.mp3 --enable-time-stretch

# With professional diarization + time-stretching
srt-voiceover revoice video.mp4 -o dubbed.mp3 \\
    --use-pyannote \\
    --enable-time-stretch
```

### Configuration File

Add to your `config.yaml`:

```yaml
# Enable smart time-stretching for all projects
enable_time_stretch: true

# Other settings...
default_voice: "en-US-AndrewMultilingualNeural"
timing_tolerance_ms: 150
```

Then run normally:
```bash
srt-voiceover input.srt -o output.mp3 -c config.yaml
```

### Python API

```python
from srt_voiceover import build_voiceover_from_srt

build_voiceover_from_srt(
    srt_path="subtitles.srt",
    output_audio_path="output.mp3",
    speaker_voices={
        "Alice": "en-US-EmmaMultilingualNeural",
        "Bob": "en-US-GuyNeural",
    },
    default_voice="en-US-AndrewMultilingualNeural",
    enable_time_stretch=True,  # ← Enable time-stretching!
    verbose=True
)
```

## ⚙️ How It Works

### 1. Generate Speech
Edge TTS creates audio: `"Hello world!"` → 2.3 seconds

### 2. Check Target Timing
SRT says this line should be: 2.8 seconds

### 3. Calculate Stretch Ratio
```
stretch_ratio = target / current = 2.8 / 2.3 = 1.217
```

### 4. Apply Phase-Vocoder Time-Stretching
```python
# librosa stretches audio duration without changing pitch
y_stretched = librosa.effects.time_stretch(audio, rate=1.217)
```

### 5. Result
Audio is now 2.8 seconds, pitch unchanged, sounds natural! 🎵

## 🎛️ Technical Details

### Stretch Limits
To avoid weird-sounding audio, stretching is limited:
- **Maximum speedup**: 25% faster (ratio 1.25)
- **Maximum slowdown**: 20% slower (ratio 0.80)

If Edge TTS timing is too far off, it falls back to padding/trimming.

### Tolerance Zone
Within `timing_tolerance_ms` (default 150ms), no adjustment is made at all:

```python
# If difference < 150ms, no adjustment
if abs(target - current) < 150:
    return audio  # Good enough!
```

### Verbose Output
When enabled with `verbose=True`, you'll see:
```
Processing subtitle 1/10 - Speaker: Alice Voice: en-US-EmmaMultilingualNeural
   Text: 'Hello, how are you today?'
  [STRETCH] 12.3% faster (2450ms -> 2800ms)
```

## 🔍 When to Use This

### ✅ Perfect For:
- **Video dubbing** - Lip-sync matters
- **ADR (Automated Dialogue Replacement)** - Matching original timing
- **Localization** - Translating and dubbing foreign videos
- **Training videos** - Professional quality output

### ⚠️ Skip For:
- **Audio-only content** - Podcasts, audiobooks (no visual sync needed)
- **Speed priority** - Time-stretching adds ~20-30% processing time
- **Very short clips** - Not worth it for <1 second segments

## 📊 Performance Impact

### Processing Time:
- **Without time-stretch**: 1 minute audio = ~15 seconds processing
- **With time-stretch**: 1 minute audio = ~20 seconds processing

**Added cost**: +20-30% processing time  
**Quality benefit**: Significantly better lip-sync

### System Requirements:
- **CPU**: Any modern processor (time-stretch is CPU-only)
- **RAM**: +200MB for librosa
- **Disk**: ~50MB for librosa/soundfile packages

## 🐛 Troubleshooting

### "librosa not installed"
```bash
pip install librosa soundfile
# Or:
pip install srt-voiceover[timestretch]
```

### "Stretch ratio X.XX too high, using padding"
This means Edge TTS timing was too far off (>25% difference).  
Try:
1. Adjusting `--rate` parameter to speed up/slow down Edge TTS
2. Increasing `timing_tolerance_ms` to allow more variance
3. Breaking long subtitles into shorter ones

### Audio sounds "robotic" or "watery"
This can happen with extreme stretches. Solutions:
- Check your stretch limits (default: 0.80-1.25x is safe)
- Use higher-quality Edge TTS voices (Neural voices)
- Adjust subtitle timing to better match natural speech

## 🔬 Advanced: How Librosa Works

### Phase Vocoder Algorithm:
1. **FFT Transform**: Convert time-domain audio → frequency-domain
2. **Phase Adjustment**: Shift spectral phases to maintain formants
3. **Resample**: Stretch/compress time axis
4. **IFFT Transform**: Convert back to time-domain

This preserves:
- ✅ Pitch (voice doesn't sound high/low)
- ✅ Timbre (voice quality maintained)
- ✅ Formants (vowel sounds stay natural)

### Why Not Just Speed Up Audio?
```python
# Simple speedup (changes pitch - sounds like chipmunk!)
fast_audio = audio.speedup(playback_speed=1.2)  

# Time-stretch (preserves pitch - sounds natural!)
stretched_audio = librosa.time_stretch(audio, rate=1.2)
```

## 🎓 Comparison with Other Tools

| Tool | Time-Stretch | Quality | Speed | Cost |
|------|--------------|---------|-------|------|
| **srt-voiceover** | librosa (phase vocoder) | Good | Fast | Free |
| **pyrubberband** | Rubber Band Library | Excellent | Very Fast | Free (C++ required) |
| **Adobe Audition** | Élastique | Excellent | Fast | $240/yr |
| **iZotope RX** | Radius | Excellent | Fast | $399 |

Our choice: **librosa** for ease of installation and good quality.

## 🚀 Future Enhancements

### Roadmap:
1. **Optional pyrubberband support** - Higher quality (requires C++ library)
2. **Per-word stretching** - Use Whisper timestamps for fine-grained control
3. **Adaptive tolerance** - Auto-adjust based on speech content
4. **Formant preservation tuning** - Better maintain voice characteristics

## 📚 References

- [Librosa Documentation](https://librosa.org/)
- [Phase Vocoder Algorithm](https://en.wikipedia.org/wiki/Phase_vocoder)
- [Time-Domain Pitch Synchronous Overlap-Add (TD-PSOLA)](https://www.csd.uoc.gr/~hy544/online/solafs.pdf)

---

## 🎬 Example Workflow

### Video Dubbing Project:

```bash
# 1. Install with time-stretch support
pip install srt-voiceover[all]

# 2. Create config for your project
srt-voiceover --init-config dubbing_config.yaml

# 3. Edit config to enable time-stretching
# dubbing_config.yaml:
#   enable_time_stretch: true
#   use_pyannote: true
#   default_voice: "es-ES-AlvaroNeural"  # Spanish voice

# 4. Process video (transcribe English -> dub to Spanish)
srt-voiceover revoice original_video.mp4 -o spanish_audio.mp3 -c dubbing_config.yaml

# 5. Merge back with video
ffmpeg -i original_video.mp4 -i spanish_audio.mp3 -c:v copy -map 0:v:0 -map 1:a:0 final_video.mp4
```

**Result**: Professional Spanish dub with perfect lip-sync! 🎉

---

**Made with ❤️ for video creators, localizers, and dubbing enthusiasts**

