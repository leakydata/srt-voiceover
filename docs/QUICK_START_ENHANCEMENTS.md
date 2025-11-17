# Quick Start: Enhanced Features

## 5-Minute Overview

Your SRT Voiceover system now has powerful new features for better voice synthesis and word synchronization.

---

## Handling Different Subtitle Types

### Type 1: Pre-Labeled Subtitles (Best Case)
```
Nathan: Hello everyone!
Nicole: Great to see you!
```

**Automatic detection:**
- System automatically extracts "Nathan" and "Nicole" as speakers
- No extra configuration needed

### Type 2: Unlabeled Single Speaker
```
Hello everyone!
Welcome to the tutorial.
```

**What happens:**
- System uses the default voice for everything
- Pass `default_voice` parameter to choose the voice

### Type 3: Unlabeled Multiple Speakers
```
Hello everyone!
Great to see you!
```

**System handles it:**
- Tries to detect speakers from context
- Falls back to default voice if unsure
- For best results, add speaker labels manually

---

## Basic Usage (3 Steps)

### Step 1: Generate SRT from Audio
```python
import srt_voiceover as svo

srt_path = svo.transcribe_audio_to_srt(
    audio_path="video.mp4",
    output_srt_path="subtitles.srt",
    use_word_timing=True  # Get word-level timing
)
```

### Step 2: Create Voiceover
```python
# Optional: Define speaker voices
speaker_voices = {
    "Nathan": "en-US-AndrewMultilingualNeural",
    "Nicole": "en-US-EmmaMultilingualNeural"
}

# Generate voiceover
quality_report = svo.build_voiceover_from_srt(
    srt_path="subtitles.srt",
    output_audio_path="voiceover.mp3",
    speaker_voices=speaker_voices,
    default_voice="en-US-AndrewMultilingualNeural"
)
```

### Step 3: Check Quality
```python
# See how well the audio synced
summary = quality_report.get_summary()
print(f"Quality: {summary['confidence_level']}")

# Find any problem areas
problems = quality_report.get_problematic_segments()
for seg in problems:
    print(f"Segment {seg.segment_idx}: {seg.issues}")
```

---

## Advanced: Word-Level Timing

For better synchronization with original speech patterns:

```python
import srt_voiceover as svo
import json

# Step 1: Transcribe with word timing
srt_path, word_timings = svo.transcribe_audio_to_srt(
    audio_path="video.mp4",
    output_srt_path="subtitles.srt",
    use_word_timing=True  # Returns (srt_path, word_timings)
)

# Step 2: Generate voiceover WITH word timing
quality_report = svo.build_voiceover_from_srt(
    srt_path="subtitles.srt",
    output_audio_path="voiceover.mp3",
    word_timings=word_timings,  # Pass word timing
    elastic_timing=True,         # Let system adjust timing windows
    verbose=True                 # Show progress
)

# Step 3: Export for manual refinement
svo.export_word_timings_multi(
    word_timings,
    "word_timings",
    formats=['json', 'vtt', 'csv']
)
```

---

## Key Features at a Glance

### 1. Smart Speaker Detection
```python
from srt_voiceover import parse_speaker_and_text_advanced

# Explicit: "Nathan: Hello"
speaker, text = parse_speaker_and_text_advanced("Nathan: Hello")
# Result: ("Nathan", "Hello")

# Context: Previous speaker was Nathan
speaker, text = parse_speaker_and_text_advanced(
    "And that's how it works",
    prev_speaker="Nathan"
)
# Result: ("Nathan", "And that's how it works")
```

### 2. Quality Metrics
```python
# Automatic during build_voiceover_from_srt()
quality_report = svo.build_voiceover_from_srt(...)

# Get summary
summary = quality_report.get_summary()
print(f"Average confidence: {summary['avg_confidence']:.0%}")

# Export for analysis
quality_report.export_json("quality_report.json")
```

### 3. Voice Optimization
```python
from srt_voiceover import list_available_voices, get_voice_profile

# See all available voices
voices = list_available_voices()
for v in voices[:5]:
    print(f"{v['display_name']} ({v['id']})")

# Check voice settings
profile = get_voice_profile("en-US-AndrewMultilingualNeural")
print(f"Baseline: {profile['baseline_wpm']} WPM")
print(f"Rate range: {profile['min_rate']}% to {profile['max_rate']}%")
```

### 4. Word Matching
```python
from srt_voiceover import match_words_to_segment

# See how well words matched
matched, confidence, unmatched = match_words_to_segment(
    "Hello world",
    word_timings,
    start_time=0.0,
    end_time=1.5
)
print(f"Confidence: {confidence:.0%}")
print(f"Unmatched: {unmatched}")
```

### 5. Multi-Format Export
```python
# Export to all formats at once
files = svo.export_word_timings_multi(
    word_timings,
    "word_timings"
)
# Creates: word_timings.json, .vtt, .srt, .csv

# Or individual exports
svo.export_word_timings_vtt(word_timings, "timings.vtt")      # Web players
svo.export_word_timings_srt(word_timings, "timings.srt")      # Subtitle editors
svo.export_word_timings_json(word_timings, "timings.json")    # Data analysis
svo.export_word_timings_csv(word_timings, "timings.csv")      # Spreadsheets
```

---

## Common Scenarios

### Scenario 1: Single Speaker, No Labels
```python
import srt_voiceover as svo

# Simple case
quality_report = svo.build_voiceover_from_srt(
    srt_path="subtitles.srt",
    output_audio_path="output.mp3",
    default_voice="en-US-EmmaMultilingualNeural"
)

print(quality_report.get_summary()['confidence_level'])
```

### Scenario 2: Multiple Pre-Labeled Speakers
```python
speaker_voices = {
    "John": "en-US-GuyNeural",
    "Sarah": "en-US-JennyNeural",
    "Mike": "en-US-AndrewMultilingualNeural"
}

quality_report = svo.build_voiceover_from_srt(
    srt_path="interview.srt",
    output_audio_path="output.mp3",
    speaker_voices=speaker_voices,
    default_voice="en-US-AndrewMultilingualNeural"
)
```

### Scenario 3: Perfect Synchronization with Word Timing
```python
# Transcribe with word-level accuracy
srt_path, word_timings = svo.transcribe_audio_to_srt(
    audio_path="original.mp4",
    output_srt_path="subtitles.srt",
    use_word_timing=True
)

# Use for precise re-voicing
quality_report = svo.build_voiceover_from_srt(
    srt_path="subtitles.srt",
    output_audio_path="revoiced.mp3",
    word_timings=word_timings,
    elastic_timing=True,
    enable_voice_profiles=True,
    verbose=True
)

# Check results
quality_report.print_report()
```

---

## Available Voices

Quick list of popular voices:

**English (US):**
- `en-US-AndrewMultilingualNeural` (Male, professional)
- `en-US-EmmaMultilingualNeural` (Female, professional)
- `en-US-GuyNeural` (Male, casual)
- `en-US-JennyNeural` (Female, friendly)

**English (UK):**
- `en-GB-RyanNeural` (Male, friendly)
- `en-GB-LibbyNeural` (Female, clear)

**English (Australia):**
- `en-AU-DuncanNeural` (Male, casual)
- `en-AU-NatashaNeural` (Female, friendly)

**Other Languages:**
- Spanish: `es-ES-AlvaroNeural`, `es-MX-JorgeNeural`
- French: `fr-FR-HenriNeural`, `fr-FR-DeniseNeural`
- German: `de-DE-KayanNeural`
- Italian: `it-IT-DiegoNeural`
- Japanese: `ja-JP-KeitaNeural`
- Mandarin: `zh-CN-YunxiNeural`

See full list:
```python
from srt_voiceover import list_available_voices
for voice in list_available_voices():
    print(f"{voice['display_name']}: {voice['id']}")
```

---

## Troubleshooting

### "Low confidence warning" in output
- Word timing didn't match subtitle text well
- Check if subtitles have typos or are very different from transcription
- Consider enabling `elastic_timing=True`

### Audio seems too fast/slow
- Check the voice's baseline WPM in profile
- Try different `enable_voice_profiles=True/False`
- Manually adjust word timings and re-generate

### Speaker not detected
- Add explicit label: "Nathan: Hello" (with colon)
- Check that speaker name starts with uppercase letter
- Make sure no extra punctuation in label

### Quality report shows issues
- Review problematic segments with low confidence
- Check word matching statistics
- Consider manual SRT adjustment

---

## Performance Tips

1. **First run takes longer** - Model downloads (~1-2 min)
2. **Use "base" model** - Fastest transcription
3. **Set `verbose=False`** - Faster execution
4. **Cache word timings** - Reuse same timings for multiple voiceovers
5. **Enable `enable_voice_profiles`** - Better quality at same speed

---

## Complete Example

```python
import srt_voiceover as svo

# Full pipeline
print("Step 1: Transcribing...")
srt_path, word_timings = svo.transcribe_audio_to_srt(
    audio_path="presentation.mp4",
    output_srt_path="subs.srt",
    model="base",
    use_word_timing=True
)

print("Step 2: Defining speakers...")
speakers = {
    "Presenter": "en-US-AndrewMultilingualNeural",
    "Interviewer": "en-US-JennyNeural"
}

print("Step 3: Generating voiceover...")
report = svo.build_voiceover_from_srt(
    srt_path=srt_path,
    output_audio_path="output.mp3",
    speaker_voices=speakers,
    word_timings=word_timings,
    elastic_timing=True,
    verbose=True
)

print("Step 4: Checking quality...")
print(f"Quality: {report.get_summary()['confidence_level']}")

print("Step 5: Exporting word timings...")
svo.export_word_timings_multi(
    word_timings,
    "timings",
    formats=['json', 'vtt']
)

print("✓ Done!")
```

---

## Need Help?

- **Full documentation**: See `ADVANCED_FEATURES.md`
- **Implementation details**: See `IMPLEMENTATION_SUMMARY.md`
- **Example code**: Check the `examples/` directory
- **API reference**: Use Python's built-in `help()`:
  ```python
  import srt_voiceover as svo
  help(svo.build_voiceover_from_srt)
  help(svo.match_words_to_segment)
  help(svo.list_available_voices)
  ```

