# Advanced Features: Deep Dive

This document explains two sophisticated features suggested for enhancing the `srt-voiceover` module for professional dubbing and localization work.

---

## 1. Smart Timing Alignment (Lip-Sync)

### The Problem with Current Approach

Right now, `align_segment_duration()` in `core.py` uses **padding/trimming**:
- If synthesized audio is **too short**: add silence at the end
- If synthesized audio is **too long**: speed it up using `pydub.speedup()`

**Why this falls short for dubbing:**
- Padding with silence makes characters' lips stop moving while audio plays
- Speeding up the entire segment uniformly sounds unnatural
- It doesn't preserve the **micro-timing** of word boundaries that human eyes expect

### What Smart Timing Alignment Does

Instead of just matching total duration, it **time-stretches audio** while preserving pitch and formants, so the synthesized speech naturally fits the original timing without sounding chipmunk-like or robotic.

### How It Works

#### Step 1: Forced Alignment
Get word-level timestamps for your synthesized audio:

**Option A: Whisper (Easiest)**
```python
import whisper
model = whisper.load_model("tiny")  # Fast for alignment
result = model.transcribe(synthesized_audio_path, word_timestamps=True)

# Extract word timings
for segment in result['segments']:
    for word_info in segment['words']:
        word = word_info['word']
        start = word_info['start']
        end = word_info['end']
        # Now you know EXACTLY when each word happens
```

**Option B: Gentle (Kaldi-based, more accurate)**
```bash
# Install: git clone https://github.com/lowerquality/gentle
python gentle/align.py synthesized.wav transcript.txt
```
Returns JSON with phoneme-level timestamps.

**Option C: Aeneas (Python-only, good for audiobooks)**
```bash
pip install aeneas
python -m aeneas.tools.execute_task \
    synthesized.wav transcript.txt \
    "task_language=eng|is_text_type=plain|os_task_file_format=json" \
    alignment.json
```

#### Step 2: Calculate Stretch Ratios
```python
def calculate_stretch_ratio(synthesized_duration, target_duration, tolerance=0.05):
    """
    Determine if/how much to stretch audio
    
    Args:
        synthesized_duration: How long Edge TTS made it
        target_duration: How long the subtitle says it should be
        tolerance: Don't stretch if within 5% of target
    
    Returns:
        stretch_ratio: 1.0 = no change, 0.9 = slow down 10%, 1.1 = speed up 10%
    """
    ratio = target_duration / synthesized_duration
    
    # If it's close enough, don't stretch
    if abs(ratio - 1.0) < tolerance:
        return 1.0
    
    # Clamp to reasonable limits (don't make it sound too weird)
    return max(0.8, min(ratio, 1.25))  # Max 20% slower or 25% faster
```

#### Step 3: Apply Phase-Vocoder Time-Stretching

**Option A: librosa (Pure Python, slower but no deps)**
```python
import librosa
import soundfile as sf

# Load audio
y, sr = librosa.load(synthesized_audio_path, sr=None)

# Stretch time WITHOUT changing pitch
y_stretched = librosa.effects.time_stretch(y, rate=stretch_ratio)

# Save
sf.write(output_path, y_stretched, sr)
```

**Option B: pyrubberband (C++ library, MUCH faster & higher quality)**
```bash
# Install Rubber Band Library first
# Ubuntu: sudo apt-get install librubberband-dev
# Mac: brew install rubberband
pip install pyrubberband
```

```python
import pyrubberband as pyrb
import soundfile as sf

# Load
y, sr = sf.read(synthesized_audio_path)

# Stretch (can also do pitch shifting separately!)
y_stretched = pyrb.time_stretch(y, sr, rate=stretch_ratio, rbargs={'--fine': ''})

# Save
sf.write(output_path, y_stretched, sr)
```

### Implementation in Your Code

Add to `core.py`:

```python
def align_segment_duration_smart(
    audio_segment: AudioSegment,
    target_duration_ms: int,
    tolerance_ms: int = 150,
    use_time_stretch: bool = True,
    aligner: str = "whisper"  # or "gentle", "aeneas"
) -> AudioSegment:
    """
    Align synthesized audio to target duration using smart time-stretching
    """
    current_duration_ms = len(audio_segment)
    diff = abs(current_duration_ms - target_duration_ms)
    
    # Within tolerance? Return as-is
    if diff <= tolerance_ms:
        return audio_segment
    
    # Should we stretch?
    if not use_time_stretch:
        # Fall back to old padding/trimming method
        return align_segment_duration(audio_segment, target_duration_ms, tolerance_ms)
    
    # Calculate stretch ratio
    stretch_ratio = target_duration_ms / current_duration_ms
    
    # Don't stretch if ratio is too extreme
    if stretch_ratio < 0.8 or stretch_ratio > 1.25:
        print(f"  [WARNING] Stretch ratio {stretch_ratio:.2f} too extreme, using fallback")
        return align_segment_duration(audio_segment, target_duration_ms, tolerance_ms)
    
    # Export to temp file for processing
    import tempfile
    with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as tmp:
        audio_segment.export(tmp.name, format='wav')
        temp_path = tmp.name
    
    try:
        # Apply time-stretch
        import librosa
        import soundfile as sf
        
        y, sr = librosa.load(temp_path, sr=None)
        y_stretched = librosa.effects.time_stretch(y, rate=stretch_ratio)
        
        # Save back
        stretched_path = temp_path.replace('.wav', '_stretched.wav')
        sf.write(stretched_path, y_stretched, sr)
        
        # Load back into pydub
        stretched_segment = AudioSegment.from_wav(stretched_path)
        
        # Cleanup
        os.unlink(temp_path)
        os.unlink(stretched_path)
        
        return stretched_segment
        
    except Exception as e:
        print(f"  [ERROR] Time-stretch failed: {e}, using fallback")
        os.unlink(temp_path)
        return align_segment_duration(audio_segment, target_duration_ms, tolerance_ms)
```

### When to Use This

**Use smart timing alignment when:**
- Dubbing video content where lip-sync matters
- Creating localized versions of training videos
- Professional ADR (Automated Dialogue Replacement)

**Skip it when:**
- Just making podcast voiceovers (no visual sync needed)
- Users want fastest possible processing
- Dealing with non-speech audio (music, sound effects)

### Performance Impact

- **librosa**: Adds ~0.5-2 seconds per subtitle (CPU-bound)
- **pyrubberband**: Adds ~0.1-0.3 seconds per subtitle (C++ optimized)
- Both are negligible compared to Edge TTS network latency

---

## 2. Voice Style Metadata & Emotion Extraction

### What Edge TTS Supports

Microsoft Edge TTS has hidden parameters beyond just `voice`, `rate`, `volume`, `pitch`:

```python
# Current usage (what you do now)
communicate = edge_tts.Communicate(
    text="Hello world",
    voice="en-US-EmmaMultilingualNeural"
)

# Extended usage (what's possible)
communicate = edge_tts.Communicate(
    text="Hello world",
    voice="en-US-EmmaMultilingualNeural",
    rate="+0%",
    volume="+0%",
    pitch="+0Hz",
    # NEW: Emotion/style controls
    style="angry",           # "angry", "cheerful", "sad", "excited", "friendly", etc.
    styledegree="2",         # 0.01 to 2.0 (how intense the emotion is)
    roleplay="YoungAdultFemale"  # Character persona
)
```

### Which Voices Support Styles?

Not all voices support all styles. Check with:

```python
import asyncio
import edge_tts

async def get_voice_styles():
    voices = await edge_tts.list_voices()
    
    for voice in voices:
        if 'StyleList' in voice and voice['StyleList']:
            print(f"{voice['ShortName']}:")
            print(f"  Styles: {', '.join(voice['StyleList'])}")

asyncio.run(get_voice_styles())
```

Common English voices with rich style support:
- `en-US-AriaNeural`: chat, cheerful, empathetic, newscast, angry, sad, excited, friendly
- `en-US-GuyNeural`: newscast, angry, cheerful, sad, whispering, terrified, shouting, unfriendly
- `en-US-JennyMultilingualNeural`: chat, customerservice, newscast-casual, assistant, cheerful

### How to Extract Style from Original Audio

Since SRT files don't contain emotion labels, you need to **infer** them from the original audio:

#### Method 1: Audio-Based Emotion Recognition

**Using HuggingFace Transformers:**
```python
from transformers import pipeline
import librosa

# Load emotion recognition model
emotion_classifier = pipeline(
    "audio-classification",
    model="superb/hubert-large-superb-er"  # Emotion Recognition
)

def detect_emotion_from_audio(audio_path, start_time, end_time):
    """
    Detect emotion from an audio segment
    
    Returns: {"emotion": "angry", "confidence": 0.87}
    """
    # Load segment
    y, sr = librosa.load(audio_path, offset=start_time, duration=end_time-start_time)
    
    # Classify
    result = emotion_classifier({"array": y, "sampling_rate": sr})
    
    # Map to Edge TTS style
    emotion_map = {
        "ang": "angry",
        "hap": "cheerful",
        "sad": "sad",
        "neu": "neutral",
        "exc": "excited",
        "fea": "terrified"
    }
    
    top_emotion = result[0]
    edge_style = emotion_map.get(top_emotion['label'], "neutral")
    
    return {
        "emotion": edge_style,
        "confidence": top_emotion['score'],
        "styledegree": str(min(2.0, top_emotion['score'] * 2))  # Scale to 0-2
    }
```

**Using OpenSMILE (Feature Extraction) + Custom Classifier:**
```bash
pip install opensmile
```

```python
import opensmile

smile = opensmile.Smile(
    feature_set=opensmile.FeatureSet.ComParE_2016,
    feature_level=opensmile.FeatureLevel.Functionals,
)

def extract_prosody_features(audio_path, start_time, end_time):
    """Extract acoustic features that correlate with emotion"""
    features = smile.process_file(audio_path)
    
    # Features include:
    # - F0 (pitch) mean, std, range
    # - Energy/loudness mean, std
    # - Spectral features
    # - Voice quality metrics
    
    # Simple heuristic rules (you'd train ML model for production):
    if features['F0semitoneFrom27.5Hz_sma3nz_amean'] > 300:  # High pitch
        if features['loudness_sma3_amean'] > 1.5:  # Loud
            return "angry" or "excited"
    elif features['loudness_sma3_amean'] < 0.5:  # Quiet
        return "sad" or "whispering"
    
    return "neutral"
```

#### Method 2: Text-Based Sentiment Analysis

**Using HuggingFace Transformers:**
```python
from transformers import pipeline

sentiment_analyzer = pipeline(
    "text-classification",
    model="j-hartmann/emotion-english-distilroberta-base"
)

def detect_emotion_from_text(subtitle_text):
    """
    Analyze text sentiment/emotion
    
    Returns: List[{"label": "joy", "score": 0.95}]
    """
    result = sentiment_analyzer(subtitle_text)
    
    # Map to Edge TTS styles
    text_emotion_map = {
        "joy": "cheerful",
        "anger": "angry",
        "sadness": "sad",
        "fear": "terrified",
        "surprise": "excited",
        "disgust": "unfriendly",
        "neutral": "neutral"
    }
    
    top_emotion = result[0]
    return text_emotion_map.get(top_emotion['label'], "neutral")
```

#### Method 3: Hybrid Approach (Best Results)

```python
def determine_speaking_style(
    audio_path,
    subtitle_text,
    start_time,
    end_time,
    speaker_name="Unknown",
    context_window=[]  # Previous 2-3 subtitles for context
):
    """
    Combine audio prosody + text sentiment + context to pick style
    """
    # Get audio emotion
    audio_result = detect_emotion_from_audio(audio_path, start_time, end_time)
    audio_emotion = audio_result['emotion']
    audio_confidence = audio_result['confidence']
    
    # Get text sentiment
    text_emotion = detect_emotion_from_text(subtitle_text)
    
    # Check for textual cues
    text_lower = subtitle_text.lower()
    if '!!!' in subtitle_text or text_lower.count('!') >= 2:
        text_emotion = "excited" if audio_confidence < 0.7 else audio_emotion
    if subtitle_text.isupper() and len(subtitle_text) > 5:
        text_emotion = "shouting"
    if '...' in subtitle_text and len(subtitle_text) < 30:
        text_emotion = "sad"
    
    # Weighted combination
    if audio_confidence > 0.75:
        # Trust audio more
        final_style = audio_emotion
        styledegree = audio_result['styledegree']
    elif audio_emotion == text_emotion:
        # Both agree - high confidence
        final_style = audio_emotion
        styledegree = "2.0"
    else:
        # Conflict - use text as tiebreaker or default
        final_style = text_emotion if audio_confidence < 0.5 else audio_emotion
        styledegree = "1.0"
    
    # Context smoothing: don't flip-flop emotions too fast
    if context_window:
        recent_styles = [ctx['style'] for ctx in context_window[-2:]]
        if all(s == recent_styles[0] for s in recent_styles):
            # Last 2 were same style - probably continuing
            if final_style != recent_styles[0] and audio_confidence < 0.8:
                final_style = recent_styles[0]  # Keep consistent
    
    return {
        "style": final_style,
        "styledegree": styledegree,
        "confidence": "high" if audio_confidence > 0.75 else "medium"
    }
```

### Integration into Your Code

Update `core.py`:

```python
def build_voiceover_from_srt(
    srt_path: str,
    output_audio_path: str,
    speaker_voices: Optional[Dict[str, Dict[str, str]]] = None,  # NOW ACCEPTS DICTS!
    default_voice: str = "en-US-AndrewMultilingualNeural",
    rate: str = "+0%",
    volume: str = "+0%",
    pitch: str = "+0Hz",
    # NEW PARAMETERS
    enable_style_detection: bool = False,
    original_audio_path: Optional[str] = None,  # For emotion extraction
    style_confidence_threshold: float = 0.7,
    verbose: bool = True,
):
    """
    Build voiceover with optional style/emotion detection
    
    Example speaker_voices (backward compatible):
        # Old way (still works)
        {"Nathan": "en-US-GuyNeural"}
        
        # New way (with styles)
        {
            "Nathan": {
                "voice": "en-US-GuyNeural",
                "style": "angry",  # Fixed style
                "styledegree": "1.5"
            },
            "Nicole": {
                "voice": "en-US-AriaNeural",
                # No style = auto-detect if enable_style_detection=True
            }
        }
    """
    # ... existing code ...
    
    for subtitle in subtitles:
        speaker, text = parse_speaker_and_text(subtitle.text)
        
        # Get voice config
        if speaker in speaker_voices:
            voice_config = speaker_voices[speaker]
            if isinstance(voice_config, str):
                # Old format: just voice name
                voice = voice_config
                style = None
                styledegree = None
            else:
                # New format: dict with voice + style
                voice = voice_config.get('voice', default_voice)
                style = voice_config.get('style')  # May be None
                styledegree = voice_config.get('styledegree')
        else:
            voice = default_voice
            style = None
            styledegree = None
        
        # Auto-detect style if enabled and not manually set
        if enable_style_detection and style is None and original_audio_path:
            detected = determine_speaking_style(
                audio_path=original_audio_path,
                subtitle_text=text,
                start_time=subtitle.start.ordinal / 1000.0,
                end_time=subtitle.end.ordinal / 1000.0,
                speaker_name=speaker
            )
            
            if detected['confidence'] == "high" or \
               (detected['confidence'] == "medium" and not speaker):
                style = detected['style']
                styledegree = detected['styledegree']
        
        # Synthesize with style
        audio_chunk = synthesize_speech_segment(
            text=text,
            voice=voice,
            rate=rate,
            volume=volume,
            pitch=pitch,
            style=style,  # NEW
            styledegree=styledegree,  # NEW
            verbose=verbose
        )
        
        # ... rest of synthesis ...
```

### Configuration Example

```yaml
# config.yaml
default_voice: "en-US-AndrewMultilingualNeural"

# Enable automatic emotion detection
enable_style_detection: true
style_confidence_threshold: 0.7  # Only apply if 70%+ confident

# Speaker-specific style overrides
speaker_voices:
  Narrator:
    voice: "en-US-GuyNeural"
    style: "narration-professional"  # Fixed style
    styledegree: "1.0"
  
  Alice:
    voice: "en-US-AriaNeural"
    # No style = auto-detect from audio
  
  Bob:
    voice: "en-US-GuyNeural"
    style: "angry"  # Bob is always angry!
    styledegree: "1.8"
```

### CLI Usage

```bash
# Auto-detect emotions from original audio
srt-voiceover revoice video.mp4 -o dubbed.mp3 \
    --enable-style-detection \
    --style-threshold 0.75 \
    -c config.yaml

# Force specific style for all speakers
srt-voiceover input.srt -o output.mp3 \
    --style cheerful \
    --styledegree 1.5
```

---

## Performance & Complexity Trade-offs

### Smart Timing Alignment
- **Complexity**: Medium (librosa is ~200 lines to integrate)
- **Performance Impact**: +20-30% processing time
- **User Value**: High for video dubbing, Low for audio-only
- **Recommendation**: **Implement as optional flag** `--enable-time-stretch`

### Style Detection
- **Complexity**: High (ML models, feature extraction, context management)
- **Performance Impact**: +50-100% processing time (if analyzing audio)
- **User Value**: Medium (nice-to-have for professional work)
- **Recommendation**: **Phase 2 feature**. Start with:
  1. Manual style config (easy, immediate value)
  2. Text-based sentiment (medium effort, decent results)
  3. Audio emotion detection (hard, best results)

---

## Recommended Implementation Order

### Phase 1 (Easy Wins):
1. ✅ Fix pyproject.toml duplicate `all`
2. ✅ Fix temp file collisions
3. ✅ Fix CLI `--model` default
4. Manual style support in config (extend `speaker_voices` to accept dicts)
5. Add `--style` and `--styledegree` CLI flags

### Phase 2 (Medium Effort):
6. Optimize asyncio loop (batch Edge TTS calls)
7. Text-based sentiment analysis for style hints
8. Add basic time-stretching with librosa

### Phase 3 (Advanced):
9. Audio-based emotion recognition
10. Hybrid style detection (audio + text + context)
11. Forced alignment + fine-grained time-stretching

---

## Questions to Consider

1. **Is your primary use case video dubbing or audio content?**
   - Video → prioritize timing alignment
   - Audio → prioritize style/emotion

2. **Will users have the original audio/video?**
   - Yes → can extract emotion
   - No → rely on text sentiment only

3. **Do users care about processing speed?**
   - Batch processing → can afford ML models
   - Real-time → keep it simple

4. **Target audience skill level?**
   - Technical users → expose all knobs
   - Non-technical → auto-detect everything

Let me know which features you want to tackle first!

