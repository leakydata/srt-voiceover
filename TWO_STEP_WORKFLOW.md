# Two-Step Workflow: Edit Transcriptions Before Voiceover

## 🎯 Overview

This feature allows you to **correct transcription errors** before generating the voiceover. Perfect for fixing:
- Misspelled words
- Wrong words (homophones like "their" vs "there")
- Technical terms or names that Whisper got wrong
- Punctuation and formatting

## 📋 The Workflow

###Step 1: Transcribe with Word Timings

```bash
srt-voiceover transcribe video.mp4 -o transcript.srt --save-word-timings
```

**This creates two files:**
- `transcript.srt` - Editable subtitle file
- `transcript_word_timings.json` - Word-level timestamps (don't edit!)

**Example output:**
```
[OK] Transcription complete!
[OK] SRT file saved: transcript.srt
   Total segments: 18
[OK] Word timings saved: transcript_word_timings.json
   You can now edit the SRT file and use these timings for voiceover generation

[WORKFLOW TIP] You can now:
  1. Edit 'transcript.srt' to fix any transcription errors
  2. Generate voiceover: srt-voiceover voiceover transcript.srt -o output.mp3 --word-timings transcript_word_timings.json
```

### Step 2: Edit the SRT File

Open `transcript.srt` in any text editor and fix errors:

**Before (transcription error):**
```srt
4
00:00:08,000 --> 00:00:13,000
This one here is the emails and of course I'll script this better ladder.
```

**After (corrected):**
```srt
4
00:00:08,000 --> 00:00:13,000
This one here is the emails and of course I'll script this better later.
```

### Step 3: Generate Voiceover with Corrected Text

```bash
srt-voiceover voiceover transcript.srt -o output.mp3 \
  --word-timings transcript_word_timings.json \
  --elastic-timing
```

**This will:**
- Use your corrected text
- Apply word-level timing for accurate pacing
- Use elastic timing with rate smoothing for natural sound
- Generate high-quality voiceover

---

## 🎬 Complete Example

### Real-World Use Case: Tutorial Video

```bash
# 1. Extract and transcribe from video
srt-voiceover transcribe tutorial.mp4 -o tutorial.srt --save-word-timings

# Files created:
# - tutorial.srt
# - tutorial_word_timings.json

# 2. Edit tutorial.srt to fix errors
# (Use Notepad, VS Code, or any text editor)

# 3. Generate corrected voiceover
srt-voiceover voiceover tutorial.srt -o corrected_audio.mp3 \
  --word-timings tutorial_word_timings.json \
  --elastic-timing

# 4. Merge with video
ffmpeg -i tutorial.mp4 -i corrected_audio.mp3 -c:v copy -map 0:v:0 -map 1:a:0 tutorial_fixed.mp4
```

---

## ⚙️ Options and Flags

### Transcribe Command

```bash
srt-voiceover transcribe [OPTIONS] INPUT

Options:
  -o, --output PATH           Output SRT file (default: output.srt)
  --save-word-timings        Save word-level timings to JSON file
  --model NAME               Whisper model (tiny, base, small, medium, large)
  --language CODE            Language code (en, es, fr, etc.)
  --multi-speaker            Enable basic speaker detection
  --use-pyannote             Use professional speaker diarization
  --device auto|cpu|cuda     Device to use (default: auto)
  -q, --quiet                Suppress progress output
```

### Voiceover Command

```bash
srt-voiceover voiceover [OPTIONS] INPUT.srt

Options:
  -o, --output PATH          Output audio file (default: output.mp3)
  --word-timings PATH        Word timings JSON file (from transcribe)
  --elastic-timing           Enable elastic timing with rate smoothing
  --rate PERCENT            Speech rate (e.g., "+20%")
  --volume PERCENT          Volume level (e.g., "+10%")
  --pitch HZ                Pitch adjustment (e.g., "-50Hz")
  --default-voice NAME      Voice to use
  -c, --config PATH         Configuration file
  -q, --quiet               Suppress progress output
```

---

## 🔍 Understanding Word Timings

### What Gets Saved

The `*_word_timings.json` file contains:

```json
[
  {
    "word": "Hello",
    "start": 0.5,
    "end": 0.9
  },
  {
    "word": "world",
    "start": 1.0,
    "end": 1.4
  }
]
```

### Important Notes

1. **Don't edit the JSON file** - It contains precise timing data from Whisper
2. **Minor text edits are OK** - Fixing spelling, punctuation, small word changes
3. **Major changes may cause issues** - If you significantly rewrite the text, timing might not match well

---

## ⚠️ Text Editing Guidelines

### ✅ Safe Edits (Timing Still Works)

- **Fix spelling:** "recieve" → "receive"
- **Fix homophones:** "their" → "there"
- **Fix capitalization:** "python" → "Python"
- **Add punctuation:** "Hello world" → "Hello, world!"
- **Fix names:** "John Doe" → "John Smith"

### ⚠️ Use Caution (May Affect Timing)

- **Adding words:** "click here" → "click right here"
- **Removing words:** "click on this button" → "click this"
- **Reordering:** "here and there" → "there and here"

### ❌ Avoid (Timing Won't Match)

- **Complete rewrites:** "This is example text" → "Here's how to do it"
- **Changing sentence structure:** "I want to show you" → "Let me demonstrate"
- **Adding/removing entire sentences**

**If you need major changes:** Re-transcribe the audio instead of using saved word timings.

---

## 💡 Pro Tips

### 1. Quick Spell-Check Workflow

```bash
# Transcribe
srt-voiceover transcribe video.mp4 -o script.srt --save-word-timings

# Open in VS Code (or any editor with spell-check)
code script.srt

# Fix errors, then generate voiceover
srt-voiceover voiceover script.srt -o fixed.mp3 \
  --word-timings script_word_timings.json --elastic-timing
```

### 2. Batch Processing

```bash
# Transcribe multiple files
for video in *.mp4; do
  srt-voiceover transcribe "$video" -o "${video%.mp4}.srt" --save-word-timings
done

# Edit all SRT files...

# Generate voiceovers
for srt in *.srt; do
  srt-voiceover voiceover "$srt" -o "${srt%.srt}_fixed.mp3" \
    --word-timings "${srt%.srt}_word_timings.json" --elastic-timing
done
```

### 3. Configuration File

Create `config.yaml`:

```yaml
default_voice: "en-US-AndrewMultilingualNeural"
use_word_timing: true
elastic_timing: true
timing_tolerance_ms: 200
```

Then use it:

```bash
# Transcribe
srt-voiceover transcribe video.mp4 -o script.srt --save-word-timings

# Generate with config
srt-voiceover voiceover script.srt -o output.mp3 \
  --word-timings script_word_timings.json -c config.yaml
```

---

## 🆚 Comparison: One-Step vs Two-Step

### One-Step Workflow (Original)

```bash
srt-voiceover revoice video.mp4 -o output.mp3 --use-word-timing --elastic-timing
```

**Pros:**
- ✅ Fast (one command)
- ✅ Automatic
- ✅ No manual intervention

**Cons:**
- ❌ Can't fix transcription errors
- ❌ Mistakes get read aloud

### Two-Step Workflow (New)

```bash
# Step 1
srt-voiceover transcribe video.mp4 -o script.srt --save-word-timings

# Step 2 (edit script.srt)

# Step 3
srt-voiceover voiceover script.srt -o output.mp3 \
  --word-timings script_word_timings.json --elastic-timing
```

**Pros:**
- ✅ Fix transcription errors
- ✅ Quality control
- ✅ Perfect for important content

**Cons:**
- ❌ Requires manual review
- ❌ Takes longer

**Recommendation:** Use two-step workflow for important content, one-step for quick tests.

---

## 📊 Word Timings File Format

### Structure

```json
[
  {
    "word": "string",    // The actual word
    "start": float,      // Start time in seconds
    "end": float         // End time in seconds
  }
]
```

### Example

```json
[
  {"word": "Okay", "start": 0.5, "end": 0.7},
  {"word": "so", "start": 0.74, "end": 0.88},
  {"word": "this", "start": 0.9, "end": 1.04},
  {"word": "is", "start": 1.06, "end": 1.14},
  {"word": "me", "start": 1.16, "end": 1.3},
  {"word": "testing", "start": 1.32, "end": 1.76}
]
```

### How It's Used

1. **Rate Calculation:** Determines words per minute for each segment
2. **Elastic Timing:** Identifies gaps between segments for time borrowing
3. **Rate Smoothing:** Creates gradual transitions between speaking speeds

---

## 🐛 Troubleshooting

### "Word timings file not found"

**Problem:** The JSON file wasn't generated or moved.

**Solution:**
```bash
# Make sure to use --save-word-timings
srt-voiceover transcribe video.mp4 -o output.srt --save-word-timings

# Check if file exists
ls output_word_timings.json
```

### "Elastic timing requires word timings"

**Problem:** Used `--elastic-timing` without providing word timings.

**Solution:**
```bash
# Either use both flags:
srt-voiceover voiceover script.srt -o output.mp3 \
  --word-timings script_word_timings.json --elastic-timing

# Or skip elastic timing:
srt-voiceover voiceover script.srt -o output.mp3
```

### "Timing seems off after editing"

**Problem:** Text was changed too much from the original.

**Cause:** Word timings are based on original transcription. Major changes break the alignment.

**Solution:**
- **Option 1:** Use without word timings: `srt-voiceover voiceover script.srt -o output.mp3`
- **Option 2:** Re-transcribe to get new word timings

---

## 🎓 Advanced Use Cases

### 1. Multi-Language Translation

```bash
# Transcribe English video
srt-voiceover transcribe english.mp4 -o english.srt --save-word-timings

# Translate SRT to Spanish (use Google Translate, DeepL, etc.)
# Keep the timing, translate the text

# Generate Spanish voiceover
srt-voiceover voiceover spanish.srt -o spanish_audio.mp3 \
  --word-timings english_word_timings.json \
  --default-voice "es-ES-ElviraNeural"
```

**Note:** This works because you keep the timing structure even though the words change.

### 2. Voice Cloning Workflow

```bash
# Get perfect transcript
srt-voiceover transcribe video.mp4 -o script.srt --save-word-timings

# Edit for perfection

# Generate with voice cloning API (hypothetical)
srt-voiceover voiceover script.srt -o output.mp3 \
  --word-timings script_word_timings.json \
  --elastic-timing \
  --voice-clone my_voice.wav
```

### 3. Podcast Editing

```bash
# Transcribe raw podcast
srt-voiceover transcribe raw_podcast.mp3 -o podcast.srt --save-word-timings

# Edit SRT to remove filler words, fix mistakes
# Keep timing structure intact

# Regenerate clean version
srt-voiceover voiceover podcast.srt -o clean_podcast.mp3 \
  --word-timings podcast_word_timings.json \
  --elastic-timing \
  --default-voice "en-US-AndrewMultilingualNeural"
```

---

## ✅ Best Practices

1. **Always save word timings** if you plan to edit the transcript
2. **Make minor edits only** to preserve timing accuracy
3. **Use elastic timing** for best quality with edited transcripts
4. **Test with a short clip** before processing long videos
5. **Keep backups** of original SRT and word timings files
6. **Name files consistently** (video.srt, video_word_timings.json, video_edited.srt)

---

## 📝 Summary

The two-step workflow gives you **quality control** over transcriptions while maintaining **professional timing and natural speech**.

**Perfect for:**
- Tutorial videos with technical terms
- Presentations with names and specialized vocabulary
- Content where accuracy is critical
- Multi-language dubbing projects
- Professional video production

**Simple workflow:**
1. `transcribe --save-word-timings` → Get SRT + JSON
2. Edit SRT → Fix errors
3. `voiceover --word-timings` → Generate perfect audio

---

**Now you can create perfectly accurate voiceovers with full editorial control!** 🎉

