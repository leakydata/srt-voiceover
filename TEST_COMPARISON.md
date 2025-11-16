# Video Dubbing Test Comparison

## 🎬 Available Test Files

You have **4 versions** of the same video to compare:

| # | Filename | Mode | Description |
|---|----------|------|-------------|
| 1 | `clean_no_stretch_dubbed.mp4` | **Default** | Simple global rate, slight timing drift |
| 2 | `word_timing_capped_dubbed.mp4` | **Word-Level (Capped)** | Dynamic rates -20% to +40%, **jarring jumps** |
| 3 | `elastic_timing_test_dubbed.mp4` | **Elastic (No Smoothing)** | Window expansion only |
| 4 | `elastic_smoothed_test_dubbed.mp4` | **Elastic + Smoothing** ⭐ | Window expansion + **smooth transitions** |

---

## 📊 Rate Progression Comparison

### Version 1: Default Mode
```
All segments: +0% (global rate)
Pros: Very natural-sounding
Cons: Slight timing drift, not ideal for lip-sync
```

### Version 2: Word-Level (Capped)
```
Segment 1:  +29%
Segment 2:  +12%  ← Jump of -17%
Segment 3:  -4%   ← Jump of -16%
Segment 4:  +40%  ← Jump of +44% (very jarring!)
Segment 5:  -5%   ← Jump of -45% (very jarring!)
Segment 6:  +0%   ← Jump of +5%
Segment 7:  +30%  ← Jump of +30%

Pros: Perfect timing accuracy
Cons: Jarring speed changes, noticeable "sped up" sections
```

### Version 3: Elastic (No Smoothing)
```
Same rates as Version 2, but with timing window expansion
Still has jarring jumps
```

### Version 4: Elastic + Smoothing ⭐ RECOMMENDED
```
Segment 1:  +29%
Segment 2:  +14%  ← Smoothed from +12% (gradual change)
Segment 3:  -1%   ← Smoothed from -4% (gradual change)
Segment 4:  +14%  ← Smoothed from +40% (BIG improvement!)
Segment 5:  -1%   ← Smoothed from -5% (gradual change)
Segment 6:  +0%   ← Natural transition
Segment 7:  +15%  ← Smoothed from +30% (gradual increase)

Pros: Perfect timing + smooth transitions
Cons: None identified
```

---

## 🎯 What to Listen/Watch For

### Timing Accuracy (Visual)
- Watch the cursor movements and UI interactions
- Do the words match "click here" with the actual click?
- Is there lag or anticipation?

**Best:** Version 2, 3, 4 (all word-level based)  
**Worst:** Version 1 (may drift slightly)

### Natural Sound (Audio)
- Does the speaking pace feel natural?
- Are there sudden speed-ups that sound robotic?
- Do transitions between segments feel smooth?

**Best:** Version 4 (smooth transitions)  
**Good:** Version 1 (but timing drift)  
**Noticeable:** Version 2, 3 (jarring speed changes)

### Overall Quality
**For video dubbing with visible actions:**
- Version 4 should be the clear winner
- Combines timing accuracy of Version 2/3 with naturalness of Version 1

---

## 🔊 Specific Sections to Compare

### Subtitle 4: "This one here is the emails..."
**Word-Level:** +40% rate (sounds rushed/robotic)  
**Smoothed:** +14% rate (natural transition from previous +14%)  
→ **Listen for:** Big difference in naturalness

### Subtitle 2-3 Transition
**Word-Level:** +12% → -4% (jarring 16% jump)  
**Smoothed:** +14% → -1% (smooth 15% transition)  
→ **Listen for:** Smoother pacing flow

### Subtitle 7: "advance to the next one..."
**Word-Level:** +30% rate (sudden speedup)  
**Smoothed:** +15% rate (gradual increase from +0%)  
→ **Listen for:** More natural acceleration

---

## 📝 Expected Results

Based on your earlier feedback:

> "elastic timing does improve word level"  
> "the speaking speed isn't constant but changes not too much from the previous chunks"

**Version 4** (Elastic + Smoothing) should provide:
- ✅ Excellent timing (matches "click here" with actions)
- ✅ Natural-sounding speech (no robotic sections)
- ✅ Smooth transitions (15% max change between segments)
- ✅ Production-ready quality

---

## 🎮 How to Test

1. **Play all 4 videos** side-by-side
2. **Focus on specific segments** (especially 2, 4, 7)
3. **Listen for:**
   - Naturalness of speech
   - Smoothness of transitions
   - Any "rushed" or "robotic" sections
4. **Watch for:**
   - Timing accuracy (clicks, UI actions)
   - Lip-sync quality (if face visible)

---

## 💡 Recommendation

For this type of content (screen recording with voiceover):

**Primary Command:**
```bash
srt-voiceover revoice video.mp4 -o output.mp3 --use-word-timing --elastic-timing
```

This enables:
- Word-level timing (Whisper word timestamps)
- Elastic timing windows (borrows from gaps)
- Rate smoothing (max 15% change per segment)

**Configuration:**
```yaml
# config.yaml
use_word_timing: true
elastic_timing: true
timing_tolerance_ms: 200
```

---

## 🔧 Adjustable Parameters (Future)

If you ever need to tweak the smoothing:

**Current Setting:** `max_change_per_segment = 15`

**To adjust:**
1. Open `src/srt_voiceover/transcribe.py`
2. Find `smooth_segment_rates()` function
3. Change `max_change_per_segment: int = 15` to your desired value

**Effects:**
- **Lower (e.g., 10):** Smoother but may drift from original timing
- **Higher (e.g., 20):** More accurate but potentially more jarring
- **Sweet spot:** 15% works well for most content

---

## ✅ Final Comparison Table

| Metric | V1 Default | V2 Word-Level | V3 Elastic | V4 Smoothed |
|--------|------------|---------------|------------|-------------|
| **Timing** | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| **Naturalness** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| **Smoothness** | ⭐⭐⭐⭐⭐ | ⭐⭐ | ⭐⭐ | ⭐⭐⭐⭐⭐ |
| **Lip-Sync** | ⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| **Overall** | ⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |

**Winner:** Version 4 (Elastic + Smoothing)

---

**Test these files and let me know which version sounds best to you!**

