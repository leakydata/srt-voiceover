# Ollama Translation Guide - Multi-Language Voiceover Support

## Overview

The SRT Voiceover system now includes **Phase 1 & 2 Ollama integration** for automatic SRT translation. This enables you to:

1. **Transcribe audio** in one language
2. **Translate** the SRT to a different language
3. **Generate voiceovers** in the new language with near-perfect timing

All while preserving speaker labels and timestamps!

---

## What You Need

### Ollama Installation

You need Ollama running on your machine or accessible via network (like ngrok):

**Local installation:**
```bash
# Download from https://ollama.ai
# Then run Ollama and pull a model:
ollama pull mistral

# Ollama will start on http://localhost:11434
```

**Using ngrok for remote access:**
```bash
# Expose local Ollama to internet
ngrok http 11434

# Share the ngrok URL (e.g., https://vast-golden-wasp.ngrok-free.app)
```

### Python Dependencies

```bash
# Translation support requires:
pip install requests

# If not already installed with srt-voiceover:
pip install srt-voiceover[all]
```

---

## Quick Start: Translation Examples

### Example 1: Transcribe English → Translate to Spanish

```bash
# Transcribe and translate in one command
srt-voiceover transcribe english_video.mp4 \
  -o english.srt \
  --translate-to es \
  --save-word-timings

# Output files:
# - english.srt (original)
# - english_spanish.srt (translated)
# - english_word_timings.json (for timing)
```

### Example 2: Using Remote Ollama (ngrok)

```bash
srt-voiceover transcribe video.mp4 \
  -o output.srt \
  --translate-to fr \
  --ollama-base-url https://vast-golden-wasp.ngrok-free.app \
  --translation-model mistral
```

### Example 3: Complete Revoice Workflow with Translation

```bash
# One command: transcribe → translate → revoice
srt-voiceover revoice video.mp4 \
  -o output.mp3 \
  --translate-to es \
  --use-word-timing \
  --elastic-timing \
  --ollama-base-url http://localhost:11434 \
  --translation-model mistral
```

---

## Configuration File Method

Create `config.yaml`:

```yaml
# Ollama configuration
ollama_base_url: "https://vast-golden-wasp.ngrok-free.app"
translation_model: "mistral"

# Default voice for translated voiceover
default_voice: "es-ES-ElviraNeural"  # Spanish

# Speaker-specific voices
speaker_voices:
  Nathan: "es-ES-AlvaroNeural"
  Nicole: "es-ES-SusanaNeural"

# Timing settings
use_word_timing: true
elastic_timing: true
```

Then use it:

```bash
srt-voiceover revoice video.mp4 \
  -o output.mp3 \
  --translate-to es \
  -c config.yaml
```

**Priority:** CLI arguments > Config file > Defaults

---

## Supported Languages

| Code | Language |
|------|----------|
| es | Spanish |
| fr | French |
| de | German |
| it | Italian |
| pt | Portuguese |
| ru | Russian |
| ja | Japanese |
| zh | Chinese |
| ko | Korean |
| ar | Arabic |
| hi | Hindi |
| nl | Dutch |
| pl | Polish |
| tr | Turkish |
| th | Thai |
| vi | Vietnamese |

---

## Python API Usage

### Basic Translation

```python
import srt_voiceover as svo

# Create Ollama config
config = svo.OllamaConfig(
    base_url="http://localhost:11434",
    model="mistral"
)

# Validate connection
if config.validate():
    # Translate SRT file
    translated_path = svo.translate_srt(
        srt_path="english.srt",
        target_language="es",
        config=config,
        output_path="spanish.srt"
    )
    print(f"Translated to: {translated_path}")
```

### Translate Individual Segments

```python
import pysrt
import srt_voiceover as svo

config = svo.OllamaConfig()

subs = pysrt.open("english.srt")
for segment in subs:
    translated = svo.translate_srt_segment(
        segment,
        target_language="fr",
        config=config
    )
    print(f"{segment.text} → {translated.text}")
```

### Complete Workflow

```python
import srt_voiceover as svo

# Step 1: Transcribe with word timing
print("Transcribing...")
srt_path, word_timings = svo.transcribe_audio_to_srt(
    audio_path="video.mp4",
    output_srt_path="original.srt",
    use_word_timing=True
)

# Step 2: Translate
print("Translating to Spanish...")
config = svo.OllamaConfig(model="mistral")
translated_srt = svo.translate_srt(
    srt_path=srt_path,
    target_language="es",
    config=config
)

# Step 3: Generate voiceover
print("Generating Spanish voiceover...")
quality_report = svo.build_voiceover_from_srt(
    srt_path=translated_srt,
    output_audio_path="spanish_voiceover.mp3",
    word_timings=word_timings,  # Use original timing
    default_voice="es-ES-ElviraNeural",
    elastic_timing=True,
    verbose=True
)

# Step 4: Check quality
print(quality_report.get_summary())

# Step 5: Merge with original video
import subprocess
subprocess.run([
    "ffmpeg", "-i", "video.mp4", "-i", "spanish_voiceover.mp3",
    "-c:v", "copy", "-map", "0:v:0", "-map", "1:a:0",
    "spanish_video.mp4"
])
```

---

## Translator Selection by Use Case

### Fast Translation (Low-Resource)
```bash
srt-voiceover transcribe video.mp4 \
  -o output.srt \
  --translate-to es \
  --translation-model tinyllama  # Smallest model
```

### Balanced (Recommended)
```bash
srt-voiceover transcribe video.mp4 \
  -o output.srt \
  --translate-to es \
  --translation-model mistral  # Default
```

### High Quality
```bash
srt-voiceover transcribe video.mp4 \
  -o output.srt \
  --translate-to es \
  --translation-model neural-chat  # Best quality
```

---

## Advanced Features

### Custom Translation Prompts

For better results with specific terminology, modify the translation prompt in `translation.py`:

```python
# In translate_text() function around line 143:
prompt = f"""Translate the following subtitle text to {language_name}.
Keep technical terms intact. Preserve speaker names.
Provide ONLY the translation, nothing else.

Text: {text}

Translation:"""
```

### Batch Processing Multiple Files

```bash
#!/bin/bash
for video in *.mp4; do
  echo "Processing $video..."
  srt-voiceover revoice "$video" \
    -o "${video%.mp4}_es.mp3" \
    --translate-to es \
    --use-word-timing \
    --elastic-timing
done
```

### Quality Control

```python
import srt_voiceover as svo

# Check translation before generating voiceover
config = svo.OllamaConfig()
translated_srt = svo.translate_srt(
    "english.srt", "es", config
)

# Manually review the translation
with open(translated_srt) as f:
    print(f.read())

# Only proceed if satisfied
if input("Proceed? [y/n]: ") == "y":
    # Generate voiceover...
```

---

## Troubleshooting

### Error: "Cannot connect to Ollama"

**Problem:** Ollama is not running or base URL is wrong

**Solutions:**
1. Make sure Ollama is running: `ollama serve`
2. Check base URL: `--ollama-base-url http://localhost:11434`
3. For remote: test ngrok URL with `curl https://your-ngrok-url/api/tags`

### Error: "Model not found"

**Problem:** The specified model isn't pulled in Ollama

**Solutions:**
```bash
# List available models
curl http://localhost:11434/api/tags

# Pull a model
ollama pull mistral
ollama pull neural-chat
ollama pull tinyllama
```

### Translation is slow

**Problem:** Model is too large or network is slow

**Solutions:**
1. Use smaller model: `--translation-model tinyllama`
2. Increase timeout: Modify `OLLAMA_TIMEOUT` in `translation.py`
3. Use local Ollama instead of ngrok for faster response

### Translation quality is poor

**Problem:** Model selected is not appropriate for language

**Solutions:**
1. Try different models: `mistral`, `neural-chat`, `openhermes2.5`
2. Use dedicated language models if available
3. Manually edit translated SRT before generating voiceover

---

## Performance Tips

1. **First run is slow** - Ollama downloads/loads model (~30s-2m depending on model)
2. **Reuse word timings** - Extract once, use for multiple translations
3. **Batch small translations** - Process multiple short videos faster than one long video
4. **Use ngrok for offloading** - Run Ollama on powerful machine, access from laptop

Example optimized workflow:
```bash
# Step 1: Transcribe all videos and save word timings
for video in *.mp4; do
  srt-voiceover transcribe "$video" -o "${video%.mp4}.srt" --save-word-timings
done

# Step 2: Translate all at once (model stays loaded)
for srt in *.srt; do
  srt-voiceover transcribe "$srt" --translate-to es
done

# Step 3: Generate voiceovers in parallel
for srt in *_spanish.srt; do
  srt-voiceover voiceover "$srt" -o "${srt%.srt}.mp3" --default-voice "es-ES-ElviraNeural"
done
```

---

## What's Working (Phase 1 & 2)

- ✓ **Phase 1: Foundation**
  - OllamaConfig class for managing connection
  - Translation functions for SRT and individual segments
  - Support for 16+ languages
  - Preserves speaker labels and timestamps

- ✓ **Phase 2: CLI Integration**
  - `--translate-to` argument for transcribe and revoice commands
  - `--ollama-base-url` for remote Ollama (ngrok support)
  - `--translation-model` for model selection
  - Config file support for persistent settings
  - Proper error handling and validation

---

## Future Enhancements (Phase 3 & 4)

- **Phase 3: Caching & Optimization**
  - Cache translated segments to speed up re-runs
  - Batch processing optimization
  - Quality metrics for translations

- **Phase 4: Extended LLM Support**
  - OpenAI GPT integration
  - Anthropic Claude integration
  - DeepSeek integration
  - Pluggable LLM architecture

---

## Integration with Video Editors

Export translations for use in video editors:

```python
import srt_voiceover as svo

# Translate
config = svo.OllamaConfig()
translated_srt = svo.translate_srt("english.srt", "fr", config)

# Export for Final Cut Pro
svo.export_word_timings_multi(
    word_timings,
    "translations",
    formats=['fcpxml', 'vtt', 'csv']
)

# Use in FCPXML for automatic subtitle creation
```

---

## Common Workflows

### Workflow 1: Simple Single-Language Conversion

```bash
# English video → Spanish audio
srt-voiceover revoice video.mp4 \
  -o spanish.mp3 \
  --translate-to es \
  --use-word-timing --elastic-timing

ffmpeg -i video.mp4 -i spanish.mp3 -c:v copy -map 0:v:0 -map 1:a:0 spanish_video.mp4
```

### Workflow 2: Multi-Language Batch

```bash
# Generate 5 language versions from one source
for lang in es fr de it ja; do
  srt-voiceover revoice video.mp4 \
    -o "output_${lang}.mp3" \
    --translate-to $lang \
    --use-word-timing
done
```

### Workflow 3: Review Before Publishing

```bash
# Transcribe and translate first
srt-voiceover transcribe video.mp4 \
  -o english.srt \
  --translate-to es

# Review translation
nano english_spanish.srt

# If satisfied, generate voiceover
srt-voiceover voiceover english_spanish.srt \
  -o spanish.mp3 \
  --default-voice "es-ES-ElviraNeural" \
  --use-word-timing
```

---

## API Reference

### OllamaConfig

```python
class OllamaConfig:
    def __init__(
        self,
        base_url: str = "http://localhost:11434",
        model: str = "mistral",
        timeout: int = 300
    )

    def validate(self, verbose: bool = True) -> bool
        """Check Ollama connection and model availability"""
```

### Translation Functions

```python
# Translate plain text
def translate_text(
    text: str,
    target_language: str,
    config: OllamaConfig,
    verbose: bool = False
) -> str

# Translate SRT segment (preserves speaker labels)
def translate_srt_segment(
    segment: pysrt.SubRipItem,
    target_language: str,
    config: OllamaConfig,
    verbose: bool = False
) -> pysrt.SubRipItem

# Translate entire SRT file
def translate_srt(
    srt_path: str,
    target_language: str,
    config: OllamaConfig,
    output_path: Optional[str] = None,
    verbose: bool = True
) -> str

# List available models
def get_available_ollama_models(
    config: OllamaConfig,
    verbose: bool = False
) -> List[str]
```

---

## Support & Feedback

- Issues: [GitHub Issues](https://github.com/leakydata/srt-voiceover/issues)
- Discussions: [GitHub Discussions](https://github.com/leakydata/srt-voiceover/discussions)
- For translation-specific issues, include:
  - Ollama version
  - Model used
  - Language pair
  - Sample text that failed

---

**Made with care for the open-source community** 🌍
