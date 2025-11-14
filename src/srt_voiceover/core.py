"""
Core functionality for SRT to voiceover conversion
"""

import io
import requests
import pysrt
from pydub import AudioSegment
from typing import Optional, Dict, Tuple


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
    edge_tts_url: str,
    api_key: str,
    response_format: str = "mp3",
    speed: float = 1.0,
) -> AudioSegment:
    """
    Call your local OpenAI-EdgeTTS style server and return a pydub AudioSegment.
    
    Args:
        text: Text to synthesize
        voice: Voice ID to use
        edge_tts_url: URL of the Edge TTS API
        api_key: API key for authentication
        response_format: Audio format (mp3 or wav)
        speed: Speech speed multiplier
        
    Returns:
        AudioSegment containing the synthesized speech
        
    Raises:
        requests.HTTPError: If the API request fails
    """

    payload = {
        "input": text,
        "voice": voice,
        "response_format": response_format,
        "speed": speed,
    }

    headers = {
        "Content-Type": "application/json",
        "Authorization": "Bearer " + api_key,
    }

    resp = requests.post(edge_tts_url, headers=headers, json=payload)
    resp.raise_for_status()

    audio_bytes = io.BytesIO(resp.content)
    segment = AudioSegment.from_file(audio_bytes, format=response_format)
    return segment


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


def build_voiceover_from_srt(
    srt_path: str,
    output_audio_path: str,
    edge_tts_url: str,
    api_key: str,
    speaker_voices: Optional[Dict[str, str]] = None,
    default_voice: str = "en-US-AndrewMultilingualNeural",
    response_format: str = "mp3",
    speed: float = 1.0,
    timing_tolerance_ms: int = 150,
    verbose: bool = True,
) -> None:
    """
    Build a complete voiceover audio file from an SRT subtitle file.
    
    Args:
        srt_path: Path to input SRT file
        output_audio_path: Path for output audio file
        edge_tts_url: URL of the Edge TTS API
        api_key: API key for authentication
        speaker_voices: Dictionary mapping speaker names to voice IDs
        default_voice: Default voice for unlabeled speakers
        response_format: Output audio format (mp3 or wav)
        speed: Speech speed multiplier
        timing_tolerance_ms: Tolerance for timing alignment in milliseconds
        verbose: Print progress information
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
            edge_tts_url=edge_tts_url,
            api_key=api_key,
            response_format=response_format,
            speed=speed,
        )

        if target_duration > 0:
            segment = align_segment_duration(segment, target_duration, timing_tolerance_ms)

        final_audio += segment
        current_position_ms += len(segment)

    final_audio.export(output_audio_path, format=response_format)
    if verbose:
        print(f"✓ Saved final voiceover to: {output_audio_path}")

