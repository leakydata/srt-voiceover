"""
Core functionality for SRT to voiceover conversion
"""

import io
import os
import asyncio
import tempfile
import pysrt
from pydub import AudioSegment
from typing import Optional, Dict, Tuple, List

try:
    import edge_tts
    EDGE_TTS_AVAILABLE = True
except ImportError:
    EDGE_TTS_AVAILABLE = False

try:
    import librosa
    import soundfile as sf
    LIBROSA_AVAILABLE = True
except ImportError:
    LIBROSA_AVAILABLE = False

# Import new modules
from .speaker_detection import parse_speaker_and_text_advanced, SpeakerContext, get_speaker_statistics
from .word_alignment import match_words_to_segment, get_timing_strategy
from .voice_profiles import get_voice_profile, calculate_segment_rate_with_voice_profile
from .quality import SyncQualityReport, SegmentQualityMetrics


def srt_time_to_milliseconds(t) -> int:
    """
    Convert pysrt.SubRipTime to milliseconds.
    
    Args:
        t: pysrt.SubRipTime object
        
    Returns:
        Total time in milliseconds
    """
    total_ms = (
        (t.hours * 3600 + t.minutes * 60 + t.seconds) * 1000
        + t.milliseconds
    )
    return total_ms


def parse_speaker_and_text(raw_text: str) -> Tuple[Optional[str], str]:
    """
    Given the subtitle text, extract speaker name (if present)
    and cleaned text without the "Speaker:" prefix.

    Example input:
        "Nathan: Essentially, there aren't really..."
    Returns:
        ("Nathan", "Essentially, there aren't really...")

    If no speaker prefix is found, returns (None, cleaned_text).
    
    Args:
        raw_text: Raw subtitle text
        
    Returns:
        Tuple of (speaker_name, cleaned_text)
    """

    if not raw_text:
        return None, ""

    lines = [ln.strip() for ln in raw_text.splitlines() if ln.strip()]
    if not lines:
        return None, ""

    first_line = lines[0]
    speaker = None
    content_lines = lines

    # Look for "Name: text" pattern on the first line
    if ":" in first_line:
        possible_speaker, rest = first_line.split(":", 1)
        possible_speaker = possible_speaker.strip()

        # Simple heuristic: name is alphabetic and starts with uppercase
        if possible_speaker and possible_speaker[0].isupper() and possible_speaker.replace(" ", "").isalpha():
            speaker = possible_speaker
            first_content = rest.lstrip()
            content_lines = []
            if first_content:
                content_lines.append(first_content)
            # Add remaining lines (without speaker label)
            if len(lines) > 1:
                content_lines.extend(lines[1:])

    # Join remaining text lines into one line
    text = " ".join(content_lines).strip()
    return speaker, text


def get_voice_for_speaker(
    speaker_name: Optional[str],
    speaker_voices: Dict[str, str],
    default_voice: str
) -> str:
    """
    Return the TTS voice name for a given speaker.
    Falls back to default_voice if speaker not found or None.
    
    Args:
        speaker_name: Name of the speaker
        speaker_voices: Dictionary mapping speaker names to voice IDs
        default_voice: Default voice to use if speaker not found
        
    Returns:
        Voice ID string
    """
    if speaker_name and speaker_name in speaker_voices:
        return speaker_voices[speaker_name]
    return default_voice


def synthesize_speech_segment(
    text: str,
    voice: str,
    rate: str = "+0%",
    volume: str = "+0%",
    pitch: str = "+0Hz",
) -> AudioSegment:
    """
    Synthesize speech using Edge TTS and return a pydub AudioSegment.
    
    Args:
        text: Text to synthesize
        voice: Voice ID to use (e.g., "en-US-AndrewMultilingualNeural")
        rate: Speech rate adjustment (e.g., "+0%", "-50%", "+100%")
        volume: Volume adjustment (e.g., "+0%", "-50%", "+100%")
        pitch: Pitch adjustment (e.g., "+0Hz", "-50Hz", "+100Hz")
        
    Returns:
        AudioSegment containing the synthesized speech
        
    Raises:
        ImportError: If edge_tts is not installed
    """
    if not EDGE_TTS_AVAILABLE:
        raise ImportError(
            "edge-tts not installed. Install it with:\n"
            "pip install edge-tts"
        )
    
    # Create communicate object
    communicate = edge_tts.Communicate(text, voice, rate=rate, volume=volume, pitch=pitch)
    
    # Run async synthesis
    audio_data = asyncio.run(_synthesize_async(communicate))
    
    # Convert to AudioSegment
    audio_bytes = io.BytesIO(audio_data)
    segment = AudioSegment.from_file(audio_bytes, format="mp3")
    return segment


async def _synthesize_async(communicate) -> bytes:
    """Helper to run edge_tts synthesis asynchronously."""
    audio_data = b""
    async for chunk in communicate.stream():
        if chunk["type"] == "audio":
            audio_data += chunk["data"]
    return audio_data


def align_segment_duration(
    segment: AudioSegment,
    target_duration_ms: int,
    tolerance_ms: int = 150
) -> AudioSegment:
    """
    Align segment length to target_duration_ms WITHOUT changing pitch.
    Only pads with silence or trims the end.

    If the difference is within tolerance_ms, do nothing.
    
    Args:
        segment: AudioSegment to align
        target_duration_ms: Target duration in milliseconds
        tolerance_ms: Tolerance for timing differences
        
    Returns:
        Aligned AudioSegment
    """

    if target_duration_ms <= 0:
        return segment

    current_duration = len(segment)
    if current_duration == 0:
        return segment

    diff = target_duration_ms - current_duration

    if abs(diff) <= tolerance_ms:
        return segment

    if diff > 0:
        # Segment is too short -> pad with silence at the end
        return segment + AudioSegment.silent(duration=diff)
    else:
        # Segment is too long -> trim the tail
        return segment[:target_duration_ms]


def align_segment_duration_smart(
    segment: AudioSegment,
    target_duration_ms: int,
    tolerance_ms: int = 150,
    enable_time_stretch: bool = True,
    max_stretch_ratio: float = 1.05,  # ULTRA conservative - only 5% faster
    min_stretch_ratio: float = 0.95,  # ULTRA conservative - only 5% slower
    verbose: bool = False
) -> AudioSegment:
    """
    Align segment using smart time-stretching to preserve natural speech.
    Falls back to padding/trimming if stretching isn't available or appropriate.
    
    Time-stretching changes duration WITHOUT changing pitch, making speech
    sound natural at different speeds. Better for video dubbing/lip-sync.
    
    Works on both CPU and GPU systems (CPU-only processing).
    
    Args:
        segment: AudioSegment to align
        target_duration_ms: Target duration in milliseconds
        tolerance_ms: Tolerance - within this, no adjustment needed
        enable_time_stretch: Whether to use time-stretching (requires librosa)
        max_stretch_ratio: Maximum speedup (1.25 = 25% faster)
        min_stretch_ratio: Maximum slowdown (0.80 = 20% slower)
        verbose: Print stretch info
        
    Returns:
        Aligned AudioSegment
    """
    if target_duration_ms <= 0:
        return segment
    
    current_duration_ms = len(segment)
    if current_duration_ms == 0:
        return segment
    
    diff = target_duration_ms - current_duration_ms
    
    # Within tolerance? Return as-is
    if abs(diff) <= tolerance_ms:
        return segment
    
    # Calculate stretch ratio
    stretch_ratio = target_duration_ms / current_duration_ms
    
    # Check if time-stretching is appropriate
    should_stretch = (
        enable_time_stretch and 
        LIBROSA_AVAILABLE and
        min_stretch_ratio <= stretch_ratio <= max_stretch_ratio
    )
    
    if not should_stretch:
        # Fall back to padding/trimming
        if verbose and enable_time_stretch and not LIBROSA_AVAILABLE:
            print("  [INFO] librosa not installed, using padding/trimming")
        elif verbose and stretch_ratio > max_stretch_ratio:
            print(f"  [INFO] Stretch ratio {stretch_ratio:.2f} too high, using padding")
        elif verbose and stretch_ratio < min_stretch_ratio:
            print(f"  [INFO] Stretch ratio {stretch_ratio:.2f} too low, using trimming")
        
        return align_segment_duration(segment, target_duration_ms, tolerance_ms)
    
    # Apply time-stretching with librosa
    try:
        # Export to temporary WAV file
        with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as tmp_in:
            segment.export(tmp_in.name, format='wav')
            temp_input = tmp_in.name
        
        try:
            # Load audio
            y, sr = librosa.load(temp_input, sr=None)
            
            # Apply time-stretch (rate > 1.0 = faster, < 1.0 = slower)
            # librosa uses 'rate' parameter opposite to our stretch_ratio
            # Our ratio: target/current - librosa rate: current/target
            librosa_rate = 1.0 / stretch_ratio
            y_stretched = librosa.effects.time_stretch(y, rate=librosa_rate)
            
            # Save stretched audio
            with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as tmp_out:
                temp_output = tmp_out.name
            
            sf.write(temp_output, y_stretched, sr)
            
            # Load back into pydub
            stretched_segment = AudioSegment.from_wav(temp_output)
            
            # Cleanup temp files
            os.unlink(temp_input)
            os.unlink(temp_output)
            
            if verbose:
                stretch_pct = (stretch_ratio - 1.0) * 100
                direction = "faster" if stretch_ratio > 1.0 else "slower"
                print(f"  [STRETCH] {abs(stretch_pct):.1f}% {direction} "
                      f"({current_duration_ms}ms -> {len(stretched_segment)}ms)")
            
            return stretched_segment
            
        except Exception as e:
            # Cleanup on error
            if os.path.exists(temp_input):
                os.unlink(temp_input)
            if 'temp_output' in locals() and os.path.exists(temp_output):
                os.unlink(temp_output)
            raise e
            
    except Exception as e:
        if verbose:
            print(f"  [WARNING] Time-stretch failed: {e}")
            print(f"  [INFO] Falling back to padding/trimming")
        
        # Fallback to simple method
        return align_segment_duration(segment, target_duration_ms, tolerance_ms)


def build_voiceover_from_srt(
    srt_path: str,
    output_audio_path: str,
    speaker_voices: Optional[Dict[str, str]] = None,
    default_voice: str = "en-US-AndrewMultilingualNeural",
    rate: str = "+0%",
    volume: str = "+0%",
    pitch: str = "+0Hz",
    timing_tolerance_ms: int = 150,
    enable_time_stretch: bool = False,
    word_timings: Optional[list] = None,
    elastic_timing: bool = False,
    verbose: bool = True,
    quality_report: Optional[SyncQualityReport] = None,
    enable_voice_profiles: bool = True,
) -> SyncQualityReport:
    """
    Build a complete voiceover audio file from an SRT subtitle file using Edge TTS.

    This function integrates advanced features:
    - Fuzzy word matching for confidence scoring
    - Per-voice rate profiles for natural sound
    - Quality metrics and reporting
    - Support for both pre-labeled and auto-detected speakers

    Args:
        srt_path: Path to input SRT file
        output_audio_path: Path for output audio file
        speaker_voices: Dictionary mapping speaker names to voice IDs
        default_voice: Default voice for unlabeled speakers
        rate: Speech rate (e.g., "+0%", "-50%", "+100%") - ignored if word_timings provided
        volume: Volume level (e.g., "+0%", "-50%", "+100%")
        pitch: Pitch adjustment (e.g., "+0Hz", "-50Hz", "+100Hz")
        timing_tolerance_ms: Tolerance for timing alignment in milliseconds
        enable_time_stretch: Use smart time-stretching for better lip-sync (requires librosa)
        word_timings: Optional word-level timing data for dynamic rate matching
        elastic_timing: Enable elastic timing windows (requires word_timings)
        verbose: Print progress information
        quality_report: Optional pre-existing report to add to (creates new if None)
        enable_voice_profiles: Use per-voice rate profiles (default True)

    Returns:
        SyncQualityReport with detailed metrics

    Raises:
        ImportError: If edge_tts is not installed
    """
    if speaker_voices is None:
        speaker_voices = {}

    # Create quality report if not provided
    if quality_report is None:
        quality_report = SyncQualityReport(verbose=verbose)

    # Import word timing functions if needed
    if word_timings:
        from .transcribe import calculate_segment_rate, smooth_segment_rates

    subs = pysrt.open(srt_path, encoding="utf-8")

    # Analyze subtitle structure for speaker information
    if verbose:
        print("\n[INFO] Analyzing subtitle structure...")
    speaker_stats = get_speaker_statistics(
        [{'speaker': parse_speaker_and_text(sub.text)[0]} for sub in subs]
    )
    if speaker_stats['unique_speakers']:
        print(f"[INFO] Found speakers: {', '.join(speaker_stats['unique_speakers'])}")
    elif speaker_stats['segments_with_speakers'] > 0:
        print(f"[INFO] Some segments have speaker labels")
    else:
        print(f"[INFO] No explicit speaker labels found - using default voice")

    # ==============================================================
    # PHASE 1: Calculate raw rates for all segments (if using word timing)
    # ==============================================================
    segment_data = []  # Store all segment info for two-pass processing
    speaker_context = SpeakerContext()

    if word_timings:
        raw_rates = []
        prev_rate = None

        for idx, sub in enumerate(subs):
            raw_text = sub.text.strip()
            if not raw_text:
                continue

            # Use advanced speaker detection (handles both explicit and implicit)
            speaker, cleaned_text = parse_speaker_and_text_advanced(
                raw_text,
                prev_speaker=speaker_context.get_last_speaker(),
                use_heuristic=True
            )

            if not cleaned_text:
                continue

            speaker_context.add_segment(idx, speaker)

            start_ms = srt_time_to_milliseconds(sub.start)
            end_ms = srt_time_to_milliseconds(sub.end)
            segment_start_s = start_ms / 1000.0
            segment_end_s = end_ms / 1000.0

            # Get adjacent segment times for elastic timing
            prev_segment_end_s = None
            next_segment_start_s = None
            if elastic_timing:
                if idx > 0:
                    prev_segment_end_s = srt_time_to_milliseconds(subs[idx-1].end) / 1000.0
                if idx < len(subs) - 1:
                    next_segment_start_s = srt_time_to_milliseconds(subs[idx+1].start) / 1000.0

            # Try to match words with confidence scoring
            matched_words, confidence, unmatched = match_words_to_segment(
                cleaned_text,
                word_timings,
                segment_start_s,
                segment_end_s,
                fuzzy_threshold=0.7,
                verbose=False
            )

            # Determine timing strategy based on confidence
            strategy = get_timing_strategy(confidence)

            # Calculate rate using original method
            rate_percent, adjusted_start_s, adjusted_end_s = calculate_segment_rate(
                segment_start_s,
                segment_end_s,
                cleaned_text,
                word_timings,
                elastic_timing=elastic_timing,
                prev_segment_end_s=prev_segment_end_s,
                next_segment_start_s=next_segment_start_s
            )

            # Apply voice-specific profile if enabled
            voice_for_segment = get_voice_for_speaker(speaker, speaker_voices, default_voice)
            if enable_voice_profiles:
                rate_percent = calculate_segment_rate_with_voice_profile(
                    voice_for_segment,
                    wpm=150,  # Placeholder - would need to extract actual WPM
                    prev_rate=prev_rate,
                    max_change_per_segment=15
                )

            raw_rates.append(rate_percent)
            prev_rate = rate_percent

            segment_data.append({
                'idx': idx,
                'sub': sub,
                'speaker': speaker,
                'cleaned_text': cleaned_text,
                'start_ms': start_ms,
                'end_ms': end_ms,
                'adjusted_start_s': adjusted_start_s,
                'adjusted_end_s': adjusted_end_s,
                'raw_rate': rate_percent,
                'confidence': confidence,
                'matched_words': len(matched_words),
                'total_words': len(matched_words) + len(unmatched),
                'timing_strategy': strategy['level']
            })
        
        # Apply smoothing to prevent jarring rate changes
        smoothed_rates = smooth_segment_rates(raw_rates, max_change_per_segment=15)
        
        # Update segment data with smoothed rates
        for i, seg_data in enumerate(segment_data):
            seg_data['rate_percent'] = smoothed_rates[i]
        
        if verbose:
            # Show smoothing summary
            changes = sum(1 for i in range(len(raw_rates)) if raw_rates[i] != smoothed_rates[i])
            if changes > 0:
                print(f"\n[SMOOTHING] Applied rate smoothing to {changes}/{len(raw_rates)} segments for natural transitions")
                print(f"            Max rate change per segment: 15%\n")
    
    # ==============================================================
    # PHASE 2: Generate audio with (smoothed) rates
    # ==============================================================
    final_audio = AudioSegment.silent(duration=0)
    current_position_ms = 0

    # If not using word timings, build segment_data on the fly
    if not word_timings:
        for idx, sub in enumerate(subs):
            raw_text = sub.text.strip()
            if not raw_text:
                continue
            
            speaker, cleaned_text = parse_speaker_and_text(raw_text)
            if not cleaned_text:
                continue
            
            start_ms = srt_time_to_milliseconds(sub.start)
            end_ms = srt_time_to_milliseconds(sub.end)
            
            segment_data.append({
                'idx': idx,
                'sub': sub,
                'speaker': speaker,
                'cleaned_text': cleaned_text,
                'start_ms': start_ms,
                'end_ms': end_ms,
                'adjusted_start_s': start_ms / 1000.0,
                'adjusted_end_s': end_ms / 1000.0,
                'rate_percent': None  # Use global rate
            })
    
    # Now process all segments
    for seg_data in segment_data:
        idx = seg_data['idx']
        speaker = seg_data['speaker']
        cleaned_text = seg_data['cleaned_text']
        start_ms = seg_data['start_ms']
        end_ms = seg_data['end_ms']
        
        voice_for_segment = get_voice_for_speaker(speaker, speaker_voices, default_voice)
        
        # Determine rate and timing
        if word_timings:
            rate_percent = seg_data['rate_percent']
            segment_rate = f"+{rate_percent}%" if rate_percent >= 0 else f"{rate_percent}%"
            adjusted_start_ms = int(seg_data['adjusted_start_s'] * 1000)
            adjusted_end_ms = int(seg_data['adjusted_end_s'] * 1000)
            target_duration = adjusted_end_ms - adjusted_start_ms
        else:
            segment_rate = rate
            adjusted_start_ms = start_ms
            adjusted_end_ms = end_ms
            target_duration = end_ms - start_ms
        
        # Handle gap/overlap with elastic timing adjustments
        if adjusted_start_ms > current_position_ms:
            gap = adjusted_start_ms - current_position_ms
            final_audio += AudioSegment.silent(duration=gap)
            current_position_ms = adjusted_start_ms
        elif adjusted_start_ms < current_position_ms:
            # Overlap - trim previous audio slightly
            overlap = current_position_ms - adjusted_start_ms
            if overlap > 0 and len(final_audio) >= overlap:
                final_audio = final_audio[:-overlap]
                current_position_ms = adjusted_start_ms
        
        if verbose:
            total_segments = len(segment_data)
            segment_num = segment_data.index(seg_data) + 1
            print(
                f"Processing subtitle {segment_num}/{total_segments} - "
                f"Speaker: {speaker} Voice: {voice_for_segment}"
            )
            print(f"   Text: {repr(cleaned_text)}")
            if word_timings:
                # Show smoothed rate (and raw if different)
                if 'raw_rate' in seg_data and seg_data['raw_rate'] != seg_data['rate_percent']:
                    raw_rate_str = f"+{seg_data['raw_rate']}%" if seg_data['raw_rate'] >= 0 else f"{seg_data['raw_rate']}%"
                    print(f"   Dynamic rate: {segment_rate} (smoothed from {raw_rate_str})")
                else:
                    print(f"   Dynamic rate: {segment_rate}")

        segment = synthesize_speech_segment(
            text=cleaned_text,
            voice=voice_for_segment,
            rate=segment_rate,  # Use calculated rate
            volume=volume,
            pitch=pitch,
        )

        if target_duration > 0:
            if enable_time_stretch:
                segment = align_segment_duration_smart(
                    segment, 
                    target_duration, 
                    timing_tolerance_ms,
                    enable_time_stretch=True,
                    verbose=verbose
                )
            else:
                segment = align_segment_duration(segment, target_duration, timing_tolerance_ms)

        final_audio += segment
        current_position_ms += len(segment)

    # Determine output format from file extension
    output_format = "mp3"  # default
    if output_audio_path.lower().endswith('.wav'):
        output_format = "wav"
    
    final_audio.export(output_audio_path, format=output_format)
    if verbose:
        print(f"[OK] Saved final voiceover to: {output_audio_path}")

