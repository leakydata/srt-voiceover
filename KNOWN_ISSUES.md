# Known Issues & Performance Improvements

## Critical Issues (Fixed ✅)

### 1. ✅ Duplicate `all` extras in pyproject.toml
**Status**: FIXED  
**Impact**: pip install srt-voiceover[all] was missing torch/torchaudio  
**Solution**: Removed duplicate definition, kept correct version with all dependencies

### 2. ✅ CLI --model defaulted to 'whisper-1' (API model)
**Status**: FIXED  
**Impact**: Local Whisper mode failed with "model whisper-1 not found"  
**Solution**: Changed default to 'base' (local model name)

### 3. ✅ Temp file collisions in parallel runs
**Status**: FIXED  
**Impact**: Multiple revoice commands would overwrite temp_transcription.srt  
**Solution**: Use tempfile.mkstemp() to generate unique paths

---

## Performance Issues

### 4. ⚠️ asyncio.run() called for every subtitle
**Status**: NEEDS OPTIMIZATION  
**Location**: `src/srt_voiceover/core.py:141`  
**Impact**: 
- Creates/destroys event loop for each subtitle (expensive)
- Large SRT files process slowly
- May leak warnings about event loop cleanup

**Current Code**:
```python
def synthesize_speech_segment(...):
    communicate = edge_tts.Communicate(text, voice, ...)
    audio_data = asyncio.run(_synthesize_async(communicate))  # ← CALLED 100+ TIMES!
    return AudioSegment.from_file(...)
```

**Better Approach**:
```python
async def build_voiceover_from_srt_async(...):
    """Async version that reuses one event loop"""
    # Create all synthesis tasks
    tasks = []
    for subtitle in subtitles:
        communicate = edge_tts.Communicate(...)
        tasks.append(_synthesize_async(communicate))
    
    # Run all in parallel (batch processing!)
    audio_results = await asyncio.gather(*tasks)
    
    # Assemble final audio
    for audio_data, subtitle in zip(audio_results, subtitles):
        segment = AudioSegment.from_file(io.BytesIO(audio_data))
        # ... alignment logic ...
```

**Recommendation**: Implement in Phase 2 after core functionality is stable. Requires:
1. Make `build_voiceover_from_srt` async
2. Batch subtitles into groups (e.g., 10 at a time) to limit concurrent connections
3. Update CLI to handle async properly

**Expected Performance Gain**: 2-5x faster for files with 20+ subtitles

---

## Documentation Issues

### 5. ✅ Missing edgetts_voices_list.md
**Status**: RESOLVED  
**Impact**: README references broken link  
**Solution**: 
- File was removed to reduce markdown clutter
- CLI now has `--list-voices` command (better approach)
- All references updated to point to `srt-voiceover --list-voices` command

**Files Updated**:
- README.md - Updated "Available Voices" section
- QUICKSTART.md - Updated "Next Steps" section
- examples/config.yaml - Updated comment
- MANIFEST.in - Removed include statement

---

## Feature Limitations

### 6. ℹ️ Basic multi-speaker detection is heuristic-based
**Status**: BY DESIGN (not a bug)  
**Clarification**:
- `--multi-speaker` uses pause detection to alternate Speaker A/B
- This is intentionally a **fast, simple heuristic** for 2-person conversations
- For real diarization, users should use `--use-pyannote`

**Documentation Update Needed**:
README should clarify:
```markdown
### Speaker Detection Modes

1. **Single speaker** (default, fastest)
   - All subtitles use same voice
   - Best for: narration, podcasts, audiobooks

2. **Basic multi-speaker** `--multi-speaker` (fast, heuristic)
   - Detects pauses and alternates Speaker A ↔ Speaker B
   - Best for: two-person interviews, simple dialogues
   - **Note**: This is NOT ML-based diarization, just a smart guess!

3. **Professional pyannote** `--use-pyannote` (best quality, slower)
   - ML-based speaker identification
   - Detects 2+ speakers with high accuracy
   - Best for: multi-person panels, complex conversations
   - Requires: HF_TOKEN env var + pyannote.audio installed
```

---

## Enhancement Roadmap

### Phase 1 (Easy Wins - Can Implement Now)
- [ ] Add manual style support (extend speaker_voices to accept dicts)
- [ ] Add `--style` and `--styledegree` CLI flags
- [ ] Update README to clarify speaker detection modes
- [x] Remove edgetts_voices_list.md references (replaced with --list-voices command)

### Phase 2 (Medium Effort - 1-2 weeks)
- [ ] Optimize asyncio loop (batch Edge TTS calls)
- [ ] Add text-based sentiment analysis for style hints
- [ ] Implement basic time-stretching with librosa (optional flag)
- [ ] Add logging instead of print statements
- [ ] Add `--max-concurrent` flag to limit parallel synthesis

### Phase 3 (Advanced - 1-2 months)
- [ ] Audio-based emotion recognition
- [ ] Forced alignment + fine-grained time-stretching
- [ ] Integrated translation pipeline
- [ ] REST API service (FastAPI wrapper)
- [ ] Direct video muxing (`--mux` flag)
- [ ] Caching for repeated TTS requests
- [ ] `--resume` flag for interrupted long-form processing

See `ADVANCED_FEATURES_EXPLAINED.md` for detailed implementation guides.

---

## Testing Needed

### Before Next Release:
1. Test `pip install -e .[all]` on fresh Python environment
2. Verify local Whisper works with default `--model base`
3. Run parallel revoice commands to confirm no temp file collisions
4. Test GPU auto-detection on both CPU and CUDA systems
5. Verify `--list-voices` handles Unicode properly on Windows

### Integration Tests to Add:
- [ ] SRT → voiceover with multiple speakers
- [ ] Audio → SRT with single speaker (default)
- [ ] Audio → SRT with `--multi-speaker` (heuristic)
- [ ] Audio → SRT with `--use-pyannote` (ML diarization)
- [ ] Complete `revoice` workflow with video input
- [ ] Error handling when HF_TOKEN missing but pyannote requested
- [ ] Graceful fallback when Whisper not installed

---

## Won't Fix (By Design)

### asyncio warnings in verbose mode
**Why**: Edge TTS library may emit warnings about SSL contexts or event loops. These are harmless and come from the underlying library, not our code.

**Mitigation**: Users can suppress with:
```bash
export PYTHONWARNINGS="ignore::DeprecationWarning"
srt-voiceover revoice input.mp3 -o output.mp3
```

### Windows console Unicode limitations
**Why**: Windows PowerShell/CMD use legacy cp1252 encoding by default.

**Mitigation**: We already handle this with try/except in `list_available_voices()`. Users can also:
```powershell
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
```

