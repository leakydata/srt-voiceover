# Verbose Testing Guide - Translation with Debug Logging

## One-Liner Test Command

```bash
srt-voiceover revoice "C:\Users\njones\Videos\2025-11-16 20-27-42.mp4" -o output_fr.mp3 --translate-to fr --use-word-timing --elastic-timing -v
```

### What Each Flag Does:
- `revoice` - Complete workflow: transcribe → translate → voiceover
- `"C:\Users\njones\Videos\2025-11-16 20-27-42.mp4"` - Your test video
- `-o output_fr.mp3` - Output audio file
- `--translate-to fr` - Translate to French
- `--use-word-timing` - Use word-level timing for accuracy
- `--elastic-timing` - Smooth timing adjustments
- `-v` or `--verbose` - Enable debug logging (NEW!)

---

## What Verbose Mode Will Show

When you run with `-v`, you'll see detailed logging for every step:

### 1. Transcription Step
```
[transcribe] INFO: Transcribing audio with Whisper model base
[transcribe] DEBUG: Using device: cuda
```

### 2. Translation Step - Ollama Connection
```
[Validating] Connecting to Ollama at http://localhost:11434...
[srt_voiceover.translation] DEBUG: Validating Ollama connection at http://localhost:11434
[srt_voiceover.translation] DEBUG: Successfully connected to Ollama
[srt_voiceover.translation] DEBUG: Available models: ['gpt-oss:20b']
✓ Ollama connected at http://localhost:11434
✓ Using model: gpt-oss:20b
```

### 3. Translation Step - Starting Translation
```
[srt_voiceover.translation] INFO: Starting SRT translation from transcript.srt
[srt_voiceover.translation] DEBUG: Target language: fr, Ollama: http://localhost:11434, Model: gpt-oss:20b
Translating SRT to French...
[srt_voiceover.translation] INFO: Loaded SRT file with 5 segments
```

### 4. Translation Step - Each Segment
```
[srt_voiceover.translation] DEBUG: Translating segment 1/5: Hello, how are you?...
[srt_voiceover.translation] DEBUG: Sending request to http://localhost:11434/api/generate with model=gpt-oss:20b
[srt_voiceover.translation] DEBUG: Received response from Ollama: status=200
[srt_voiceover.translation] DEBUG: Ollama response: Bonjour, comment allez-vous?...
[srt_voiceover.translation] DEBUG: Translation complete: Bonjour, comment allez-...
  [1/5] ✓
```

(Repeats for segments 2-5)

### 5. Translation Step - Completion
```
[srt_voiceover.translation] INFO: Translated SRT saved to transcript_french.srt
[OK] Translation complete: transcript_french.srt
```

### 6. Voiceover Generation
```
[core] INFO: Building voiceover from SRT file
[core] DEBUG: Processing 5 segments with French voice
```

### 7. Final Output
```
[OK] Re-voicing complete: output_fr.mp3
```

---

## Expected Ollama Response

When translation works correctly, you'll see Ollama responses like:

```
DEBUG: Sending request to http://localhost:11434/api/generate with model=gpt-oss:20b
{
  "model": "gpt-oss:20b",
  "created_at": "2025-11-16T22:45:30Z",
  "response": "Bonjour, comment allez-vous?",
  "done": true,
  "total_duration": 1250000000,
  "load_duration": 45000000,
  "prompt_eval_count": 45,
  "prompt_eval_duration": 200000000,
  "eval_count": 12,
  "eval_duration": 1000000000
}
```

---

## Troubleshooting with Verbose Mode

### If Ollama Connection Fails
```
[ERROR] Cannot connect to Ollama at http://localhost:11434
        Make sure Ollama is running or check the base URL
```

**Solution:** Make sure Ollama is running:
```bash
ollama serve
```

### If Model Not Found
```
[WARNING] Model 'gpt-oss:20b' not found in Ollama
Available models: ['mistral']
```

**Solution:** Pull the model:
```bash
ollama pull gpt-oss:20b
```

### If Translation Times Out
```
[ERROR] Ollama request timed out after 300 seconds
```

**Solution:** Increase timeout or use a faster model:
```bash
srt-voiceover revoice video.mp4 --translate-to fr -v --translation-model mistral
```

### If Network Error
```
[ERROR] Connection error during translation: <error details>
```

**Solution:** Check network connectivity and Ollama URL:
```bash
# Test Ollama connection
curl http://localhost:11434/api/tags

# Or with ngrok
curl https://your-ngrok-url/api/tags
```

---

## Testing Different Scenarios

### Test 1: Verify Ollama Connection Only
```bash
srt-voiceover revoice video.mp4 -o /dev/null --translate-to es -v
```

### Test 2: Fast Translation (Use Mistral)
```bash
srt-voiceover revoice video.mp4 -o output.mp3 --translate-to fr -v --translation-model mistral
```

### Test 3: Remote Ollama (ngrok)
```bash
srt-voiceover revoice video.mp4 -o output.mp3 --translate-to de -v --ollama-base-url https://vast-golden-wasp.ngrok-free.app
```

### Test 4: Config File with Verbose
```bash
srt-voiceover revoice video.mp4 -o output.mp3 -c config.yaml -v
```

---

## Log Levels

### INFO Level (Default)
Shows:
- Start/completion of major operations
- File paths and configuration
- Success/error messages

### DEBUG Level (With `-v` flag)
Shows (in addition to INFO):
- Connection details
- Request/response bodies (first 100 chars)
- Model availability checks
- Segment-by-segment progress
- Configuration details
- Timing information

---

## Logging Configuration

The logging system now supports:

- **Format:** `[module] LEVEL: message`
- **Modules:**
  - `srt_voiceover.translation` - Translation operations
  - `srt_voiceover.transcribe` - Transcription operations
  - `srt_voiceover.core` - Core voiceover generation

### Example Output Parsing
```
[srt_voiceover.translation] DEBUG: Successfully connected to Ollama
                             ^^^^^
                         Log Level
```

---

## Complete Workflow with Verbose Logging

```bash
# This single command will show you everything:
srt-voiceover revoice "C:\Users\njones\Videos\2025-11-16 20-27-42.mp4" \
  -o output_fr.mp3 \
  --translate-to fr \
  --use-word-timing \
  --elastic-timing \
  -v
```

### What You'll See:

1. **Initialization**
   - `[DEBUG] Verbose logging enabled`

2. **Transcription**
   - Whisper model loading
   - Audio processing
   - SRT generation

3. **Translation Validation**
   - Ollama connection check
   - Model availability
   - Configuration summary

4. **Translation Execution**
   - Per-segment translation progress
   - Ollama requests/responses
   - File saving confirmation

5. **Voiceover Generation**
   - Voice selection
   - Audio synthesis
   - Final output

---

## Reading the Output

### Success Indicators
- ✓ symbols appear for completed steps
- `[OK]` messages for finished operations
- No `[ERROR]` or `[WARNING]` messages (unless expected)

### Error Indicators
- `[ERROR]` messages require action
- `[WARNING]` messages indicate issues to address
- Connection failures show at the start

### Debug Info Patterns
- `DEBUG: Sending request to...` - Request being sent
- `DEBUG: Received response...` - Response received
- `DEBUG: Translation complete:` - Segment finished

---

## Performance Monitoring

With verbose mode, you can see:

1. **Model Load Time**
```
load_duration: 45000000 (45ms)
```

2. **Prompt Evaluation**
```
prompt_eval_duration: 200000000 (200ms)
```

3. **Token Generation**
```
eval_duration: 1000000000 (1 second for 12 tokens)
```

Total time per segment ≈ load + eval = ~1.2 seconds

---

## Best Practices

1. **Always use `-v` for first run** to verify Ollama connection
2. **Check Ollama logs separately** in another terminal:
   ```bash
   # In another terminal window
   ollama logs
   ```
3. **Save logs to file** for debugging:
   ```bash
   srt-voiceover revoice video.mp4 -o output.mp3 --translate-to fr -v 2>&1 | tee translation_debug.log
   ```
4. **Test with small file first** before large videos
5. **Monitor Ollama separately** during translation

---

## Quick Reference

| Command | Purpose |
|---------|---------|
| `-v` | Enable verbose logging |
| `-q` | Suppress progress (opposite of verbose) |
| `--verbose` | Long form of `-v` |
| `--translation-model mistral` | Fast model |
| `--translation-model gpt-oss:20b` | Default (high quality) |
| `--ollama-base-url URL` | Custom Ollama address |

---

**Ready to test!** Run that one-liner command with `-v` to see everything in action. 🚀
