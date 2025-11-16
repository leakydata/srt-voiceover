"""
Core functionality for SRT to voiceover conversion
"""

import io
import os
import asyncio
import tempfile
import pysrt
from pydub import AudioSegment
from typing import Optional, Dict, Tuple

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
    max_stretch_ratio: float = 1.25,
    min_stretch_ratio: float = 0.80,
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
    verbose: bool = True,
) -> None:
    """
    Build a complete voiceover audio file from an SRT subtitle file using Edge TTS.
    
    Args:
        srt_path: Path to input SRT file
        output_audio_path: Path for output audio file
        speaker_voices: Dictionary mapping speaker names to voice IDs
        default_voice: Default voice for unlabeled speakers
        rate: Speech rate (e.g., "+0%", "-50%", "+100%")
        volume: Volume level (e.g., "+0%", "-50%", "+100%")
        pitch: Pitch adjustment (e.g., "+0Hz", "-50Hz", "+100Hz")
        timing_tolerance_ms: Tolerance for timing alignment in milliseconds
        enable_time_stretch: Use smart time-stretching for better lip-sync (requires librosa)
        verbose: Print progress information
        
    Raises:
        ImportError: If edge_tts is not installed
    """
    if speaker_voices is None:
        speaker_voices = {}
    
    subs = pysrt.open(srt_path, encoding="utf-8")

    final_audio = AudioSegment.silent(duration=0)
    current_position_ms = 0

    for idx, sub in enumerate(subs):
        raw_text = sub.text.strip()
        if not raw_text:
            continue

        speaker, cleaned_text = parse_speaker_and_text(raw_text)
        if not cleaned_text:
            continue

        voice_for_segment = get_voice_for_speaker(speaker, speaker_voices, default_voice)

        start_ms = srt_time_to_milliseconds(sub.start)
        end_ms = srt_time_to_milliseconds(sub.end)
        target_duration = end_ms - start_ms

        if start_ms > current_position_ms:
            gap = start_ms - current_position_ms
            final_audio += AudioSegment.silent(duration=gap)
            current_position_ms = start_ms

        if verbose:
            print(
                f"Processing subtitle {idx + 1}/{len(subs)} - "
                f"Speaker: {speaker} Voice: {voice_for_segment}"
            )
            print(f"   Text: {repr(cleaned_text)}")

        segment = synthesize_speech_segment(
            text=cleaned_text,
            voice=voice_for_segment,
            rate=rate,
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

