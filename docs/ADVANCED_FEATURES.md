# Advanced Features Guide - SRT Voiceover

This guide covers the enhanced features added for improved word timing, voice switching, and quality metrics.

## Table of Contents

1. [Speaker Detection (Auto & Manual)](#speaker-detection)
2. [Fuzzy Word Matching](#fuzzy-word-matching)
3. [Voice Profiles](#voice-profiles)
4. [Quality Metrics & Reporting](#quality-metrics)
5. [Word Timing Export](#word-timing-export)

---

## Speaker Detection

The system supports **three methods** for detecting speakers:

### 1. Explicit Labels (Recommended for Pre-Labeled Subtitles)

If your SRT already has speaker labels, they'll be automatically extracted:

```
1
00:00:00,000 --> 00:00:03,000
Nathan: Hello everyone, this is a tutorial.

2
00:00:03,000 --> 00:00:06,000
Nicole: Great! Let's get started.
```

**Features:**
- Validates that speaker names start with uppercase and are alphabetic
- Handles names with spaces (e.g., "John Smith:")
- Strips the speaker prefix from the text automatically

### 2. Context-Based Detection (For Unlabeled Subtitles)

If subtitles don't have explicit labels, the system can infer speakers from context:

```
1
00:00:00,000 --> 00:00:03,000
Hello everyone, this is a tutorial.

2
00:00:03,000 --> 00:00:06,000
Great! Let's get started.
```

**How it works:**
- Looks for continuation words (and, but, so, or, because, they, it, etc.)
- Assumes same speaker if a subtitle starts with a continuation word
- Falls back to previous speaker if no continuation pattern found

**Usage Example:**

```python
from srt_voiceover import parse_speaker_and_text_advanced

# With context from previous speaker
speaker, text = parse_speaker_and_text_advanced(
    "And that's how it works.",
    prev_speaker="Nathan",  # Assumes Nathan is continuing
    use_heuristic=True
)
# Result: speaker = "Nathan", text = "And that's how it works."
```

### 3. Speaker Statistics

Analyze a subtitle file to understand speaker structure:

```python
from srt_voiceover import get_speaker_statistics
import pysrt

subs = pysrt.open("subtitles.srt")
segments = [{'speaker': parse_speaker_and_text(sub.text)[0]} for sub in subs]

stats = get_speaker_statistics(segments)
print(f"Unique speakers: {stats['unique_speakers']}")
print(f"Speaker counts: {stats['speaker_counts']}")
print(f"Has multiple speakers: {stats['has_multiple_speakers']}")
```

---

## Fuzzy Word Matching

Matches transcribed words to subtitle text with confidence scoring, handling variations:

### Handled Cases

- **Contractions**: "don't" → "dont", "it's" → "its"
- **Punctuation**: "Hello!" → "Hello"
- **Minor typos**: Up to 70% similarity threshold by default
- **Confidence scoring**: Reports how well words matched (0.0 to 1.0)

### Basic Usage

```python
from srt_voiceover import match_words_to_segment

word_timings = [
    {'word': 'Hello', 'start': 0.1, 'end': 0.5},
    {'word': 'world', 'start': 0.6, 'end': 1.2},
]

segment_text = "Hello world"
segment_start_s = 0.0
segment_end_s = 1.5

matched_words, confidence, unmatched = match_words_to_segment(
    segment_text,
    word_timings,
    segment_start_s,
    segment_end_s,
    fuzzy_threshold=0.7
)

print(f"Matched {len(matched_words)}/{len(matched_words) + len(unmatched)} words")
print(f"Confidence: {confidence:.0%}")
```

### Timing Strategy Selection

Based on confidence scores, the system automatically selects a timing strategy:

```python
from srt_voiceover import get_timing_strategy

confidence = 0.85

strategy = get_timing_strategy(confidence)
print(strategy)
# Output:
# {
#     'level': 'MEDIUM',
#     'use_word_timing': True,
#     'elastic_timing': True,
#     'rate_smoothing': True,
#     'max_rate_change': 15,
#     'enable_time_stretch': False,
#     'description': 'Medium confidence - using conservative timing'
# }
```

**Strategy Levels:**

| Confidence | Level | Features |
|---|---|---|
| > 90% | HIGH | Aggressive timing, elastic, time-stretching enabled |
| 70-90% | MEDIUM | Conservative timing, elastic enabled, no stretching |
| 50-70% | LOW | Minimal dynamic adjustment, no elastic timing |
| < 50% | NONE | Static timing only |

---

## Voice Profiles

Each voice has different speaking rates and adjustment limits. The system includes profiles for 30+ voices:

### Available Voices

```python
from srt_voiceover import list_available_voices, print_voice_profiles

# List all voices
voices = list_available_voices()
for voice in voices[:5]:
    print(f"{voice['display_name']}: {voice['baseline_wpm']} WPM")

# Print detailed profiles
print_voice_profiles(language='en-US')  # Filter by language
```

### Voice-Specific Rate Adjustment

Each voice has baseline WPM and adjustment limits:

```
en-US-AndrewMultilingualNeural:
  - Baseline: 155 WPM
  - Rate range: [-35%, +35%]
  - Natural pause threshold: 0.3s

en-US-EmmaMultilingualNeural:
  - Baseline: 160 WPM
  - Rate range: [-40%, +40%]
  - Natural pause threshold: 0.25s
```

### Using Voice-Specific Profiles

```python
from srt_voiceover import get_voice_profile, calculate_segment_rate_with_voice_profile

# Get profile for a specific voice
voice_id = "en-US-AndrewMultilingualNeural"
profile = get_voice_profile(voice_id)

print(f"Baseline WPM: {profile['baseline_wpm']}")
print(f"Rate range: {profile['min_rate']}% to {profile['max_rate']}%")

# Calculate optimal rate for this voice
measured_wpm = 180
rate = calculate_segment_rate_with_voice_profile(
    voice_id,
    wpm=measured_wpm,
    prev_rate=0,
    max_change_per_segment=15
)
print(f"Recommended rate: {rate:+d}%")
```

---

## Quality Metrics & Reporting

Comprehensive quality reports track synchronization accuracy and identify issues:

### Automatic Quality Reporting

During voiceover generation, quality metrics are automatically collected:

```python
from srt_voiceover import build_voiceover_from_srt

quality_report = build_voiceover_from_srt(
    srt_path="subtitles.srt",
    output_audio_path="output.mp3",
    word_timings=word_timings,  # Optional
    verbose=True  # Prints detailed quality report
)
```

### Accessing Report Data

```python
# Get summary statistics
summary = quality_report.get_summary()
print(f"Average confidence: {summary['avg_confidence']:.1%}")
print(f"Quality level: {summary['confidence_level']}")
print(f"Segments with issues: {summary['segments_with_issues']}")
print(f"Max rate change: {summary['max_rate_change']}%")

# Get detailed statistics
stats = quality_report.get_statistics()
print(f"Min/Max confidence: {stats['min_confidence']:.1%} to {stats['max_confidence']:.1%}")

# Find problematic segments
problem_segs = quality_report.get_problematic_segments()
for seg in problem_segs:
    print(f"Segment {seg.segment_idx}: {', '.join(seg.issues)}")

# Get confidence distribution
histogram = quality_report.get_confidence_histogram()
print(f"High confidence (0.8-1.0): {histogram['0.8-1.0']} segments")
print(f"Low confidence (0.0-0.2): {histogram['0.0-0.2']} segments")
```

### Print Human-Readable Report

```python
# Print to console (already shown during generation with verbose=True)
quality_report.print_report(
    max_issues_shown=10,
    show_all_segments=False  # Show only problematic segments
)

# Export as JSON
quality_report.export_json("quality_report.json")
```

### Issues Detected

The system automatically flags:

- **Low confidence** - Word matching confidence < 50%
- **Large rate jumps** - Rate change > 25% from previous segment
- **Extreme rates** - Rate > +40% or < -40%
- **Poor word matching** - Less than 50% of words successfully matched
- **No words matched** - Complete matching failure

---

## Word Timing Export

Export word-level timing data in multiple formats for integration with other tools:

### Multi-Format Export

```python
from srt_voiceover import export_word_timings_multi

word_timings = [
    {'word': 'Hello', 'start': 0.1, 'end': 0.5},
    {'word': 'world', 'start': 0.6, 'end': 1.2},
]

# Export to all formats
results = export_word_timings_multi(
    word_timings,
    output_base_path="word_timings",
    formats=['json', 'vtt', 'srt', 'csv'],  # Or omit for all formats
    verbose=True
)

print(f"JSON: {results['json']}")
print(f"VTT: {results['vtt']}")
print(f"SRT: {results['srt']}")
print(f"CSV: {results['csv']}")
```

### Individual Format Exports

**WebVTT (for web players):**
```python
from srt_voiceover import export_word_timings_vtt

export_word_timings_vtt(word_timings, "word_timings.vtt")
```

**SubRip (for subtitle editors):**
```python
from srt_voiceover import export_word_timings_srt

export_word_timings_srt(word_timings, "word_timings.srt")
```

**JSON (machine-readable):**
```python
from srt_voiceover import export_word_timings_json

export_word_timings_json(word_timings, "word_timings.json")
```

**CSV (for spreadsheets):**
```python
from srt_voiceover import export_word_timings_csv

export_word_timings_csv(word_timings, "word_timings.csv")
```

---

## Complete Example: Multi-Speaker Voiceover with Quality Reporting

```python
import srt_voiceover as svo

# Define speaker-to-voice mappings
speaker_voices = {
    "Nathan": "en-US-AndrewMultilingualNeural",
    "Nicole": "en-US-EmmaMultilingualNeural",
    "John": "en-US-GuyNeural"
}

# Load transcription with word timings
with open("word_timings.json") as f:
    import json
    word_timings = json.load(f)

# Generate voiceover with quality tracking
quality_report = svo.build_voiceover_from_srt(
    srt_path="subtitles.srt",
    output_audio_path="output.mp3",
    speaker_voices=speaker_voices,
    default_voice="en-US-AndrewMultilingualNeural",
    word_timings=word_timings,
    elastic_timing=True,
    enable_time_stretch=False,
    enable_voice_profiles=True,
    verbose=True  # Shows progress and quality report
)

# Export word timings for manual refinement
svo.export_word_timings_multi(
    word_timings,
    "word_timings_export",
    formats=['vtt', 'json', 'csv']
)

# Get detailed analysis
summary = quality_report.get_summary()
if summary['avg_confidence'] > 0.8:
    print("✓ Excellent synchronization quality!")
elif summary['avg_confidence'] > 0.6:
    print("~ Fair synchronization - check problematic segments")
else:
    print("✗ Poor synchronization - review and adjust")

# Get problem areas
problems = quality_report.get_problematic_segments()
for seg in problems[:3]:
    print(f"Check segment {seg.segment_idx}: {', '.join(seg.issues)}")
```

---

## Summary of Improvements

| Feature | Benefit | Use Case |
|---------|---------|----------|
| **Advanced Speaker Detection** | Handles both labeled & unlabeled | Mixed subtitle formats |
| **Fuzzy Word Matching** | Robust to transcription errors | Real-world audio |
| **Voice Profiles** | Optimal quality per voice | Multi-voice projects |
| **Quality Metrics** | Identify sync issues early | Quality assurance |
| **Multi-Format Export** | Integration with other tools | Professional workflows |
| **Confidence Scoring** | Understand sync accuracy | Debugging & analysis |

---

## Tips for Best Results

1. **For pre-labeled subtitles**: Use explicit speaker labels (e.g., "Nathan: text")
2. **For unlabeled subtitles**: System will use context or default to single voice
3. **With word timings**: Enable `elastic_timing=True` for fast speech
4. **For quality**: Review `quality_report` for confidence scores
5. **For different voices**: Define `speaker_voices` mapping for each speaker
6. **Check voice profiles**: Use `list_available_voices()` to find optimal baseline

