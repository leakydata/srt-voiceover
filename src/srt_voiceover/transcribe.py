"""
Audio transcription to SRT with speaker diarization support
"""

import io
import os
import tempfile
from pathlib import Path
from typing import Optional, List, Dict, Tuple
from pydub import AudioSegment
import pysrt

try:
    import whisper
    WHISPER_AVAILABLE = True
except ImportError:
    WHISPER_AVAILABLE = False

try:
    import requests
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False

try:
    from pyannote.audio import Pipeline
    PYANNOTE_AVAILABLE = True
except ImportError:
    PYANNOTE_AVAILABLE = False


def transcribe_audio_to_srt(
    audio_path: str,
    output_srt_path: str,
    model: str = "base",
    language: Optional[str] = None,
    enable_speaker_detection: bool = False,
    verbose: bool = True,
    # API mode (optional - for OpenAI API or compatible servers)
    use_api: bool = False,
    api_url: Optional[str] = None,
    api_key: Optional[str] = None,
    # Professional diarization (optional - requires pyannote.audio)
    use_pyannote: bool = False,
    device: str = "cpu",
    # Word-level timing for dynamic rate matching (optional)
    use_word_timing: bool = False,
):
    """
    Transcribe audio file to SRT format with timestamps using OpenAI Whisper.
    
    TWO MODES:
    1. Local Mode (default): Uses openai-whisper library directly
    2. API Mode: Uses OpenAI API or compatible server (like openai-whisper-api)
    
    Args:
        audio_path: Path to input audio file (mp3, wav, m4a, etc.)
        output_srt_path: Path for output SRT file
        model: Whisper model size - "tiny", "base", "small", "medium", "large"
               (Local mode) or "whisper-1" (API mode)
        language: Optional language code (en, es, fr, etc.)
        enable_speaker_detection: Attempt to detect different speakers (default: False = single speaker)
        verbose: Print progress information
        use_api: If True, use API mode instead of local Whisper
        api_url: API endpoint URL (for API mode)
        api_key: API key (for API mode)
        use_pyannote: Use pyannote.audio for professional speaker diarization (default: False)
                      Requires HF_TOKEN environment variable to be set
        device: Device to use for processing ("cpu" or "cuda", default: "cpu")
        
    Returns:
        Path to created SRT file
        
    Raises:
        ImportError: If required dependencies not installed
        FileNotFoundError: If audio file not found
    """
    
    if verbose:
        print(f"Loading audio file: {audio_path}")
    
    # Check if file exists
    audio_file = Path(audio_path)
    if not audio_file.exists():
        raise FileNotFoundError(f"Audio file not found: {audio_path}")
    
    # Choose transcription method
    if use_api:
        if not REQUESTS_AVAILABLE:
            raise ImportError("requests library required for API mode. Install: pip install requests")
        result = _transcribe_via_api(audio_path, model, language, api_url, api_key, verbose)
    else:
        if not WHISPER_AVAILABLE:
            raise ImportError(
                "openai-whisper not installed. Install it with:\n"
                "pip install openai-whisper\n\n"
                "Or use API mode with use_api=True if you have access to OpenAI API"
            )
        result = _transcribe_local(audio_path, model, language, verbose, device, word_timestamps=use_word_timing)
    
    if verbose:
        print(f"[OK] Transcription complete!")
    
    # Extract word timings if requested
    word_timings = None
    if use_word_timing and not use_api:
        word_timings = extract_word_timings(result)
        if verbose and word_timings:
            print(f"[OK] Extracted {len(word_timings)} word-level timestamps")
    
    # Convert to SRT format
    subs = pysrt.SubRipFile()
    
    # Handle different response formats
    if 'segments' in result:
        segments = result['segments']
    elif 'words' in result:
        # Group words into segments
        segments = _group_words_into_segments(result['words'])
    else:
        # Fallback: create one segment from full text
        segments = [{
            'start': 0,
            'end': 10,
            'text': result.get('text', '')
        }]
    
    # Get speaker diarization if using pyannote
    speaker_map = {}
    if use_pyannote:
        speaker_map = _get_pyannote_speakers(audio_path, device, verbose)
    
    for i, segment in enumerate(segments):
        start_time = segment.get('start', 0)
        end_time = segment.get('end', start_time + 5)
        text = segment.get('text', '').strip()
        
        if not text:
            continue
        
        # Convert seconds to SubRipTime
        start = _seconds_to_srt_time(start_time)
        end = _seconds_to_srt_time(end_time)
        
        # Add speaker detection if enabled
        if use_pyannote and speaker_map:
            # Use pyannote speaker for this time segment
            speaker = _get_speaker_at_time(speaker_map, start_time, end_time)
            if speaker:
                text = f"{speaker}: {text}"
        elif enable_speaker_detection:
            # Use basic heuristic
            speaker = _detect_speaker_heuristic(text, i)
            if speaker:
                text = f"{speaker}: {text}"
        
        sub = pysrt.SubRipItem(
            index=i + 1,
            start=start,
            end=end,
            text=text
        )
        subs.append(sub)
    
    # Save SRT file
    subs.save(output_srt_path, encoding='utf-8')
    
    if verbose:
        print(f"[OK] SRT file saved: {output_srt_path}")
        print(f"   Total segments: {len(subs)}")
    
    # Return SRT path and optionally word timings
    if use_word_timing:
        return output_srt_path, word_timings
    else:
        return output_srt_path


def _transcribe_local(audio_path: str, model: str, language: Optional[str], verbose: bool, device: str = "cpu", word_timestamps: bool = False) -> Dict:
    """Transcribe using local Whisper model."""
    if verbose:
        print(f"Loading Whisper model '{model}'... (first run will download the model)")
    
    # Load model
    whisper_model = whisper.load_model(model, device=device)
    
    if verbose:
        device_msg = f"on {device.upper()}" if device == "cuda" else "on CPU"
        print(f"Transcribing audio {device_msg}... (this may take a while)")
    
    # Transcribe with optional word timestamps
    transcribe_options = {'word_timestamps': word_timestamps}
    if language:
        transcribe_options['language'] = language
    
    result = whisper_model.transcribe(audio_path, **transcribe_options)
    
    return result


def extract_word_timings(whisper_result: Dict) -> List[Dict]:
    """
    Extract word-level timing data from Whisper result.
    
    Args:
        whisper_result: Result from Whisper transcribe() with word_timestamps=True
        
    Returns:
        List of word timing dicts with 'word', 'start', 'end' keys
    """
    word_timings = []
    
    for segment in whisper_result.get('segments', []):
        if 'words' in segment:
            for word_info in segment['words']:
                word_timings.append({
                    'word': word_info.get('word', '').strip(),
                    'start': word_info.get('start', 0.0),
                    'end': word_info.get('end', 0.0)
                })
    
    return word_timings


def calculate_segment_rate(
    segment_start_s: float, 
    segment_end_s: float, 
    segment_text: str, 
    word_timings: List[Dict],
    elastic_timing: bool = False,
    prev_segment_end_s: Optional[float] = None,
    next_segment_start_s: Optional[float] = None
) -> Tuple[int, float, float]:
    """
    Calculate optimal TTS rate for a segment based on original word timing.
    
    Args:
        segment_start_s: Segment start time in seconds
        segment_end_s: Segment end time in seconds
        segment_text: Text of the segment
        word_timings: List of word timing dicts from extract_word_timings()
        elastic_timing: Enable elastic timing window expansion
        prev_segment_end_s: End time of previous segment (for elastic)
        next_segment_start_s: Start time of next segment (for elastic)
        
    Returns:
        Tuple of (rate_percent as int, adjusted_start, adjusted_end)
    """
    # Find words within this segment's time range
    segment_words = [
        w for w in word_timings
        if segment_start_s <= w['start'] < segment_end_s
    ]
    
    if not segment_words:
        return 0, segment_start_s, segment_end_s
    
    # Calculate speaking rate (words per minute)
    word_count = len(segment_words)
    duration_s = segment_end_s - segment_start_s
    
    if duration_s <= 0:
        return 0, segment_start_s, segment_end_s
    
    duration_minutes = duration_s / 60.0
    wpm = word_count / duration_minutes
    
    # Edge TTS baseline is approximately 150 WPM for natural speech
    baseline_wpm = 150
    rate_multiplier = wpm / baseline_wpm
    rate_percent = int((rate_multiplier - 1.0) * 100)
    
    # Elastic timing: If speed needed is high, try to expand window
    adjusted_start = segment_start_s
    adjusted_end = segment_end_s
    
    if elastic_timing and rate_percent > 30:
        # Calculate how much time we need to reduce speed to 30%
        target_multiplier = 1.30  # +30%
        needed_duration = word_count / (baseline_wpm * target_multiplier) * 60
        expansion_needed = needed_duration - duration_s
        
        # Limit expansion to max 500ms
        expansion_needed = min(expansion_needed, 0.5)
        
        if expansion_needed > 0:
            # Try to borrow time from adjacent silences
            gap_before = segment_start_s - prev_segment_end_s if prev_segment_end_s else 0
            gap_after = next_segment_start_s - segment_end_s if next_segment_start_s else 0
            
            # Distribute expansion between before/after based on available gaps
            total_gap = gap_before + gap_after
            if total_gap > expansion_needed:
                # We have enough gap space
                if total_gap > 0:
                    ratio_before = gap_before / total_gap
                    expand_before = expansion_needed * ratio_before
                    expand_after = expansion_needed * (1 - ratio_before)
                    
                    # Don't take all the gap (leave at least 100ms)
                    expand_before = min(expand_before, gap_before - 0.1) if gap_before > 0.1 else 0
                    expand_after = min(expand_after, gap_after - 0.1) if gap_after > 0.1 else 0
                    
                    adjusted_start = segment_start_s - expand_before
                    adjusted_end = segment_end_s + expand_after
                    
                    # Recalculate with expanded window
                    new_duration = adjusted_end - adjusted_start
                    new_duration_minutes = new_duration / 60.0
                    wpm = word_count / new_duration_minutes
                    rate_multiplier = wpm / baseline_wpm
                    rate_percent = int((rate_multiplier - 1.0) * 100)
    
    # Clamp to REASONABLE limits for natural-sounding speech
    rate_percent = max(-20, min(40, rate_percent))
    
    return rate_percent, adjusted_start, adjusted_end


def smooth_segment_rates(
    raw_rates: List[int],
    max_change_per_segment: int = 15
) -> List[int]:
    """
    Smooth rate changes between consecutive segments to avoid jarring transitions.
    
    This prevents sudden jumps like +29% -> -4% -> +40% by limiting how much
    the rate can change from one segment to the next.
    
    Args:
        raw_rates: List of raw rate percentages (e.g., [29, 12, -4, 40])
        max_change_per_segment: Maximum rate change allowed between consecutive segments
        
    Returns:
        List of smoothed rate percentages
    """
    if not raw_rates:
        return []
    
    smoothed = [raw_rates[0]]  # First segment keeps its rate
    
    for i in range(1, len(raw_rates)):
        prev_rate = smoothed[-1]
        desired_rate = raw_rates[i]
        
        # Limit the change from previous segment
        rate_change = desired_rate - prev_rate
        
        if abs(rate_change) > max_change_per_segment:
            # Cap the change
            if rate_change > 0:
                new_rate = prev_rate + max_change_per_segment
            else:
                new_rate = prev_rate - max_change_per_segment
        else:
            new_rate = desired_rate
        
        smoothed.append(new_rate)
    
    return smoothed


def _transcribe_via_api(
    audio_path: str,
    model: str,
    language: Optional[str],
    api_url: Optional[str],
    api_key: Optional[str],
    verbose: bool
) -> Dict:
    """Transcribe using API (OpenAI or compatible)."""
    if not api_url:
        api_url = "https://api.openai.com/v1/audio/transcriptions"
    
    if not api_key:
        raise ValueError("API key required for API mode")
    
    if verbose:
        print(f"Transcribing via API... (this may take a while)")
    
    audio_file = Path(audio_path)
    
    with open(audio_path, 'rb') as f:
        files = {
            'file': (audio_file.name, f, 'audio/mpeg'),
        }
        
        data = {
            'model': model,
            'response_format': 'verbose_json',
        }
        
        if language:
            data['language'] = language
        
        headers = {
            'Authorization': f'Bearer {api_key}'
        }
        
        response = requests.post(api_url, files=files, data=data, headers=headers)
        response.raise_for_status()
        
        return response.json()


def _seconds_to_srt_time(seconds: float) -> pysrt.SubRipTime:
    """Convert seconds to SubRipTime format."""
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    millis = int((seconds % 1) * 1000)
    
    return pysrt.SubRipTime(hours=hours, minutes=minutes, seconds=secs, milliseconds=millis)


def _group_words_into_segments(words: List[Dict], max_duration: float = 5.0) -> List[Dict]:
    """
    Group individual words into segments based on timing.
    
    Args:
        words: List of word dictionaries with 'start', 'end', 'text'
        max_duration: Maximum duration for a segment in seconds
        
    Returns:
        List of segment dictionaries
    """
    if not words:
        return []
    
    segments = []
    current_segment = {
        'start': words[0].get('start', 0),
        'end': words[0].get('end', 0),
        'text': words[0].get('word', words[0].get('text', ''))
    }
    
    for word in words[1:]:
        word_start = word.get('start', 0)
        word_end = word.get('end', word_start)
        word_text = word.get('word', word.get('text', ''))
        
        # Check if we should start a new segment
        segment_duration = word_end - current_segment['start']
        time_gap = word_start - current_segment['end']
        
        if segment_duration > max_duration or time_gap > 1.0:
            # Save current segment and start new one
            segments.append(current_segment)
            current_segment = {
                'start': word_start,
                'end': word_end,
                'text': word_text
            }
        else:
            # Add to current segment
            current_segment['end'] = word_end
            current_segment['text'] += ' ' + word_text
    
    # Add last segment
    if current_segment['text']:
        segments.append(current_segment)
    
    return segments


def _detect_speaker_heuristic(text: str, segment_index: int) -> Optional[str]:
    """
    Simple heuristic to detect potential speaker changes.
    
    This is a basic implementation. For production use, consider:
    - pyannote.audio for speaker diarization
    - Azure Speaker Recognition
    - Custom ML models
    
    Args:
        text: Segment text
        segment_index: Index of the segment
        
    Returns:
        Speaker name or None
    """
    # This is a placeholder - real speaker detection would use audio analysis
    # For now, we alternate between Speaker A and B based on simple patterns
    
    # Check for question (might indicate different speaker)
    if '?' in text:
        return "Speaker B" if segment_index % 2 == 0 else "Speaker A"
    
    # Default alternating pattern
    return "Speaker A" if segment_index % 2 == 0 else "Speaker B"


def _get_pyannote_speakers(audio_path: str, device: str = "cpu", verbose: bool = True) -> Dict:
    """
    Use pyannote.audio for professional speaker diarization.
    
    Args:
        audio_path: Path to audio file
        device: Device to use ("cpu" or "cuda")
        verbose: Print progress messages
        
    Returns:
        Dictionary mapping time ranges to speaker labels
        
    Note:
        Requires HF_TOKEN environment variable to be set with a valid
        HuggingFace token that has access to pyannote models.
    """
    if not PYANNOTE_AVAILABLE:
        raise ImportError(
            "pyannote.audio not installed. Install it with:\n"
            "pip install pyannote.audio\n\n"
            "Also requires HuggingFace token with access to pyannote models:\n"
            "https://huggingface.co/pyannote/speaker-diarization"
        )
    
    # Get token from environment
    import os
    hf_token = os.getenv('HF_TOKEN') or os.getenv('HUGGINGFACE_TOKEN')
    
    if not hf_token:
        raise ValueError(
            "HuggingFace token required for pyannote speaker diarization.\n\n"
            "Set the HF_TOKEN environment variable:\n"
            "  Windows (PowerShell): $env:HF_TOKEN = \"hf_your_token_here\"\n"
            "  Windows (cmd):        set HF_TOKEN=hf_your_token_here\n"
            "  Linux/Mac:            export HF_TOKEN=hf_your_token_here\n\n"
            "Get your token at: https://huggingface.co/settings/tokens\n"
            "Accept license at: https://huggingface.co/pyannote/speaker-diarization-3.1"
        )
    
    if verbose:
        device_msg = f" on {device.upper()}" if device == "cuda" else " on CPU"
        print(f"Loading pyannote speaker diarization pipeline{device_msg}...")
        print("(This may take a minute on first run)")
    
    try:
        # Load the pipeline
        import torch
        pipeline = Pipeline.from_pretrained(
            "pyannote/speaker-diarization-3.1",
            use_auth_token=hf_token
        )
        
        # Move to device (GPU or CPU)
        pipeline.to(torch.device(device))
        
        # Run diarization
        if verbose:
            device_msg = "This will be faster on GPU" if device == "cpu" else "Using GPU acceleration"
            print(f"Running speaker diarization... ({device_msg})")
        
        diarization = pipeline(audio_path)
        
        # Convert to speaker map
        speaker_map = {}
        for turn, _, speaker in diarization.itertracks(yield_label=True):
            speaker_map[(turn.start, turn.end)] = speaker
        
        if verbose:
            unique_speakers = len(set(speaker_map.values()))
            print(f"[OK] Detected {unique_speakers} speaker(s)")
        
        return speaker_map
        
    except Exception as e:
        if "401" in str(e) or "authentication" in str(e).lower():
            raise ValueError(
                f"Authentication failed with HuggingFace.\n"
                f"Make sure you have:\n"
                f"1. Valid HF token\n"
                f"2. Accepted model license at: https://huggingface.co/pyannote/speaker-diarization-3.1\n"
                f"Error: {e}"
            )
        raise


def _get_speaker_at_time(speaker_map: Dict, start_time: float, end_time: float) -> Optional[str]:
    """
    Get the speaker for a given time segment.
    
    Args:
        speaker_map: Dictionary from _get_pyannote_speakers
        start_time: Segment start time in seconds
        end_time: Segment end time in seconds
        
    Returns:
        Speaker label (e.g., "SPEAKER_00") or None
    """
    # Find which speaker has the most overlap with this segment
    mid_time = (start_time + end_time) / 2
    
    for (seg_start, seg_end), speaker in speaker_map.items():
        if seg_start <= mid_time <= seg_end:
            return speaker
    
    # If no exact match, find closest
    closest_speaker = None
    min_distance = float('inf')
    
    for (seg_start, seg_end), speaker in speaker_map.items():
        distance = min(abs(start_time - seg_start), abs(end_time - seg_end))
        if distance < min_distance:
            min_distance = distance
            closest_speaker = speaker
    
    return closest_speaker


def convert_audio_format(
    input_path: str,
    output_path: Optional[str] = None,
    output_format: str = "wav",
    sample_rate: int = 16000,
    channels: int = 1,
    verbose: bool = True,
) -> str:
    """
    Convert audio file to different format (useful for preprocessing).
    
    Args:
        input_path: Path to input audio file
        output_path: Path for output file (auto-generated if None)
        output_format: Output format (wav, mp3, etc.)
        sample_rate: Sample rate in Hz (16000 is good for speech recognition)
        channels: Number of channels (1 = mono, 2 = stereo)
        verbose: Print progress information
        
    Returns:
        Path to converted file
    """
    if output_path is None:
        input_file = Path(input_path)
        output_path = str(input_file.with_suffix(f'.{output_format}'))
    
    if verbose:
        print(f"Converting audio format...")
    
    # Load audio
    audio = AudioSegment.from_file(input_path)
    
    # Convert to mono and resample
    if channels == 1:
        audio = audio.set_channels(1)
    
    audio = audio.set_frame_rate(sample_rate)
    
    # Export
    audio.export(output_path, format=output_format)
    
    if verbose:
        print(f"[OK] Converted audio saved: {output_path}")
    
    return output_path


def extract_audio_from_video(
    video_path: str,
    output_audio_path: Optional[str] = None,
    audio_format: str = "wav",
    verbose: bool = True,
) -> str:
    """
    Extract audio track from video file.
    
    Note: Requires ffmpeg to be installed.
    
    Args:
        video_path: Path to input video file
        output_audio_path: Path for output audio (auto-generated if None)
        audio_format: Output audio format
        verbose: Print progress information
        
    Returns:
        Path to extracted audio file
    """
    if output_audio_path is None:
        video_file = Path(video_path)
        output_audio_path = str(video_file.with_suffix(f'.{audio_format}'))
    
    if verbose:
        print(f"Extracting audio from video...")
    
    try:
        # Use pydub which uses ffmpeg internally
        audio = AudioSegment.from_file(video_path)
        audio.export(output_audio_path, format=audio_format)
        
        if verbose:
            print(f"[OK] Audio extracted: {output_audio_path}")
        
        return output_audio_path
    except Exception as e:
        raise RuntimeError(f"Failed to extract audio. Make sure ffmpeg is installed: {e}")


# Higher-level workflow functions

def audio_to_voiceover_workflow(
    input_audio: str,
    output_audio: str,
    speaker_voices: Optional[Dict[str, str]] = None,
    default_voice: str = "en-US-AndrewMultilingualNeural",
    temp_srt: Optional[str] = None,
    language: Optional[str] = None,
    rate: str = "+0%",
    volume: str = "+0%",
    pitch: str = "+0Hz",
    whisper_model: str = "base",
    verbose: bool = True,
    # Optional: Use API for transcription instead of local
    use_whisper_api: bool = False,
    whisper_api_url: Optional[str] = None,
    whisper_api_key: Optional[str] = None,
    enable_speaker_detection: bool = False,
    # Professional diarization (optional - requires HF_TOKEN env var)
    use_pyannote: bool = False,
    device: str = "cpu",
    enable_time_stretch: bool = False,
    use_word_timing: bool = False,
    elastic_timing: bool = False,
) -> Tuple[str, str]:
    """
    Complete workflow: Audio → Transcribe → Re-voice with different speakers.
    
    This is the "magic" function that does everything in one go!
    
    Args:
        input_audio: Input audio file path
        output_audio: Output audio file path
        speaker_voices: Dictionary mapping detected speakers to voices
        default_voice: Default voice
        temp_srt: Temporary SRT file path (auto-generated if None)
        language: Optional language for transcription
        rate: Speech rate (e.g., "+0%", "-50%", "+100%")
        volume: Volume level (e.g., "+0%", "-50%", "+100%")
        pitch: Pitch adjustment (e.g., "+0Hz", "-50Hz", "+100Hz")
        whisper_model: Whisper model size (tiny/base/small/medium/large)
        verbose: Print progress
        use_whisper_api: Use API instead of local Whisper
        whisper_api_url: API URL (if using API)
        whisper_api_key: API key (if using API)
        
    Returns:
        Tuple of (srt_path, output_audio_path)
    """
    from .core import build_voiceover_from_srt
    
    # Generate unique temp file if not provided
    if temp_srt is None:
        # Create temp file in system temp directory with unique name
        temp_fd, temp_srt = tempfile.mkstemp(suffix='.srt', prefix='srt_voiceover_')
        os.close(temp_fd)  # Close the file descriptor, we just need the path
    
    if verbose:
        print("=" * 60)
        print("AUDIO RE-VOICING WORKFLOW")
        print("=" * 60)
        print()
    
    # Step 1: Transcribe
    if verbose:
        print("Step 1/2: Transcribing audio to SRT...")
    
    # Transcribe with optional word timing
    transcribe_result = transcribe_audio_to_srt(
        audio_path=input_audio,
        output_srt_path=temp_srt,
        model=whisper_model,
        language=language,
        enable_speaker_detection=enable_speaker_detection,
        verbose=verbose,
        use_api=use_whisper_api,
        api_url=whisper_api_url,
        api_key=whisper_api_key,
        use_pyannote=use_pyannote,
        device=device,
        use_word_timing=use_word_timing,
    )
    
    # Handle return value (string or tuple)
    if use_word_timing:
        srt_path, word_timings = transcribe_result
    else:
        srt_path = transcribe_result
        word_timings = None
    
    if verbose:
        print()
        print("Step 2/2: Generating new voiceover...")
        if use_word_timing:
            print("Using word-level timing for dynamic rate matching...")
    
    # Step 2: Re-voice
    build_voiceover_from_srt(
        srt_path=srt_path,
        output_audio_path=output_audio,
        speaker_voices=speaker_voices or {},
        default_voice=default_voice,
        rate=rate,
        volume=volume,
        pitch=pitch,
        enable_time_stretch=enable_time_stretch,
        word_timings=word_timings,
        elastic_timing=elastic_timing,
        verbose=verbose,
    )
    
    if verbose:
        print()
        print("=" * 60)
        print("[COMPLETE] Your re-voiced audio is ready!")
        print("=" * 60)
        print(f"Transcription: {srt_path}")
        print(f"New audio: {output_audio}")
    
    return srt_path, output_audio

