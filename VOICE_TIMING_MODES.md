# Voice Timing Modes Guide

This document explains the different timing strategies available in `srt-voiceover` for video dubbing and audio re-voicing.

---

## 🎯 Quick Recommendation

| Use Case | Recommended Mode | Command |
|----------|------------------|---------|
| **Audio-only content** (podcasts, audiobooks) | Default | `srt-voiceover revoice audio.mp3 -o output.mp3` |
| **Video with no visible faces** | Default | `srt-voiceover revoice video.mp4 -o output.mp3` |
| **Video dubbing with lip-sync** | Word-Level Timing | `srt-voiceover revoice video.mp4 -o output.mp3 --use-word-timing` |
| **Professional lip-sync (faces visible)** | Word-Level + Elastic (coming soon) | `srt-voiceover revoice video.mp4 -o output.mp3 --use-word-timing --elastic-timing` |

---

## 📊 Timing Modes Explained

### Mode 1: Default (Fast & Natural)

**How it works:**
- Uses a global TTS speed adjustment (default: natural speed)
- Simple padding/silence for timing alignment
- Consistent pacing throughout

**Characteristics:**
- ✅ Very natural-sounding voice
- ✅ Fast processing
- ⚠️ May drift slightly from original timing
- ⚠️ Not ideal for strict lip-sync

**Best for:**
- Podcasts and audiobooks
- Videos without visible speakers
- Content where exact timing isn't critical

**Example:**
```bash
# Default behavior
srt-voiceover revoice video.mp4 -o output.mp3

# With custom global speed
srt-voiceover revoice video.mp4 -o output.mp3 --rate "+20%"
```

**Processing Time:** Baseline (fastest)

---

### Mode 2: Word-Level Timing (Dynamic Pacing)

**How it works:**
- Whisper extracts word-level timestamps from original audio
- Calculates speaking rate (words per minute) per segment
- Adjusts TTS speed dynamically for each subtitle
- Caps speeds at reasonable limits (-20% to +40%)

**Characteristics:**
- ✅ Excellent timing accuracy
- ✅ Natural-sounding (with caps)
- ✅ Matches original pacing variations
- ⚠️ Slight speed variations may be noticeable in fast sections
- ⚠️ Slightly slower processing (+15-20%)

**Best for:**
- Video dubbing where timing matters
- Content with visible speakers (lip-sync)
- Matching varied speaking paces

**Example:**
```bash
# Enable word-level timing
srt-voiceover revoice video.mp4 -o output.mp3 --use-word-timing

# With config file
srt-voiceover revoice video.mp4 -o output.mp3 --use-word-timing -c config.yaml
```

**How the dynamic rates work:**
```
Original segment: 15 words in 6 seconds = 150 WPM (baseline)
→ TTS rate: +0% (matches baseline)

Fast segment: 20 words in 4 seconds = 300 WPM (very fast!)
→ TTS rate: +100% → capped to +40% (natural limit)

Slow segment: 10 words in 8 seconds = 75 WPM (slow with pauses)
→ TTS rate: -20% (matches slow pace)
```

**Configuration:**
```yaml
# config.yaml
use_word_timing: true  # Enable dynamic pacing
```

**Processing Time:** +15-20% (due to word timestamp extraction)

---

### Mode 3: Elastic Timing (Coming Soon - Best Quality)

**How it works:**
- Combines word-level timing with adaptive timing windows
- Detects segments that need high speeds (>30%)
- Expands/contracts timing windows by borrowing from adjacent silences
- Reduces need for extreme speed adjustments

**Characteristics:**
- ✅ Excellent timing accuracy
- ✅ Most natural-sounding
- ✅ Perfect for professional lip-sync
- ⏳ Same processing time as word-level

**Example (when available):**
```bash
# Future feature
srt-voiceover revoice video.mp4 -o output.mp3 --use-word-timing --elastic-timing
```

**Status:** Planned for future release

---

## 🔧 Technical Details

### Default Mode

```python
# All segments use same rate
for segment in subtitles:
    synthesize_speech(text, voice, rate="+20%")
    # Pad with silence if too short
    # Trim end if too long
```

### Word-Level Timing Mode

```python
# Extract word timings
word_timings = whisper.transcribe(audio, word_timestamps=True)

# Calculate rate per segment
for segment in subtitles:
    wpm = count_words(segment) / segment_duration_minutes
    rate = calculate_rate(wpm, baseline=150)
    rate = clamp(rate, min=-20%, max=+40%)  # Prevent extreme speeds
    
    synthesize_speech(text, voice, rate=rate)
```

### Elastic Timing Mode (Planned)

```python
# Expand timing windows for fast segments
for segment in subtitles:
    rate_needed = calculate_rate(segment)
    
    if rate_needed > 30%:  # Too fast
        # Borrow time from adjacent silences
        expanded_window = expand_timing(segment, max_expansion=400ms)
        rate_needed = recalculate_rate(segment, expanded_window)
    
    synthesize_speech(text, voice, rate=rate_needed)
```

---

## 📈 Performance Comparison

| Mode | Processing Time | Memory | Quality Score |
|------|----------------|---------|---------------|
| Default | 1.0x (baseline) | Low | ⭐⭐⭐⭐ |
| Word-Level | 1.15-1.20x | Medium | ⭐⭐⭐⭐⭐ |
| Elastic (planned) | 1.15-1.20x | Medium | ⭐⭐⭐⭐⭐ |

**Note:** Processing time is primarily TTS generation, which is the same for all modes. The +15-20% overhead in word-level mode comes from Whisper word timestamp extraction during transcription.

---

## 🎬 Real-World Examples

### Example 1: Podcast Re-voicing
```bash
# Podcast with consistent pacing - default is perfect
srt-voiceover revoice podcast.mp3 -o new_voice.mp3 --rate "+15%"
```

**Result:** Natural-sounding, consistent pace. Minor timing drift is not noticeable in audio-only content.

### Example 2: YouTube Tutorial (No Face)
```bash
# Screen recording with voiceover - default works well
srt-voiceover revoice tutorial.mp4 -o dubbed_tutorial.mp3
```

**Result:** Clean audio, slight timing variance OK since no lip-sync needed.

### Example 3: Interview Video (Visible Speakers)
```bash
# People on camera - use word-level timing
srt-voiceover revoice interview.mp4 -o dubbed_interview.mp3 --use-word-timing
```

**Result:** Better timing accuracy, minimal speed variations with caps. Suitable for casual video dubbing.

### Example 4: Professional Film Dubbing (Future)
```bash
# Close-ups of faces - use elastic timing
srt-voiceover revoice movie.mp4 -o dubbed_movie.mp3 --use-word-timing --elastic-timing
```

**Result:** Perfect timing + natural sound. Best for professional productions.

---

## ⚙️ Configuration Examples

### Default Config (Fast & Natural)
```yaml
# config.yaml
default_voice: "en-US-AndrewMultilingualNeural"
rate: "+0%"  # Natural speed
timing_tolerance_ms: 400  # Accept 400ms variance
use_word_timing: false  # Simple global rate
```

### Quality Config (Lip-Sync)
```yaml
# config.yaml
default_voice: "en-US-AndrewMultilingualNeural"
rate: "+0%"  # Will be calculated per segment
timing_tolerance_ms: 200  # Stricter timing
use_word_timing: true  # Dynamic per-segment rates
```

---

## 🐛 Troubleshooting

### "Word-level timing sounds rushed"
- **Cause:** Your original speech is very fast
- **Solution:** Caps are already in place (-20% to +40%). If still too rushed, speak slower when recording or use default mode.

### "Timing drifts over time"
- **Cause:** Using default mode with very different speaking pace than TTS
- **Solution:** Use `--use-word-timing` for better accuracy

### "Processing is slow"
- **Cause:** Word-level timing extracts word timestamps
- **Solution:** This is normal (+15-20% overhead). For faster processing, use default mode.

---

## 📚 Further Reading

- **Time-stretching** (deprecated): See `KNOWN_ISSUES.md` for why we moved away from audio stretching
- **Advanced features**: See `ADVANCED_FEATURES_EXPLAINED.md` for technical deep-dives
- **Voice styles**: See documentation on emotion/style parameters (coming soon)

---

**Last Updated:** Current session  
**Status:** Default and Word-Level modes are production-ready. Elastic timing is planned for future release.

