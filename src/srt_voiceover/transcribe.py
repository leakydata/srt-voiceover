"""
Audio transcription to SRT with speaker diarization support
"""

import io
import os
import requests
from pathlib import Path
from typing import Optional, List, Dict, Tuple
from pydub import AudioSegment
import pysrt


def transcribe_audio_to_srt(
    audio_path: str,
    output_srt_path: str,
    whisper_url: str = "http://localhost:5050/v1/audio/transcriptions",
    api_key: str = "",
    model: str = "whisper-1",
    language: Optional[str] = None,
    response_format: str = "verbose_json",
    enable_speaker_detection: bool = True,
    verbose: bool = True,
) -> str:
    """
    Transcribe audio file to SRT format with timestamps.
    
    Args:
        audio_path: Path to input audio file (mp3, wav, m4a, etc.)
        output_srt_path: Path for output SRT file
        whisper_url: URL of Whisper API endpoint
        api_key: API key for authentication
        model: Model name (whisper-1, etc.)
        language: Optional language code (en, es, fr, etc.)
        response_format: Response format from API
        enable_speaker_detection: Attempt to detect different speakers
        verbose: Print progress information
        
    Returns:
        Path to created SRT file
    """
    
    if verbose:
        print(f"📂 Loading audio file: {audio_path}")
    
    # Check if file exists
    audio_file = Path(audio_path)
    if not audio_file.exists():
        raise FileNotFoundError(f"Audio file not found: {audio_path}")
    
    # Prepare the request
    with open(audio_path, 'rb') as f:
        files = {
            'file': (audio_file.name, f, 'audio/mpeg'),
        }
        
        data = {
            'model': model,
            'response_format': response_format,
        }
        
        if language:
            data['language'] = language
        
        headers = {}
        if api_key:
            headers['Authorization'] = f'Bearer {api_key}'
        
        if verbose:
            print(f"🎤 Transcribing audio... (this may take a while)")
        
        response = requests.post(
            whisper_url,
            files=files,
            data=data,
            headers=headers
        )
        response.raise_for_status()
        
        result = response.json()
    
    if verbose:
        print(f"✓ Transcription complete!")
    
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
        if enable_speaker_detection:
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
        print(f"✓ SRT file saved: {output_srt_path}")
        print(f"   Total segments: {len(subs)}")
    
    return output_srt_path


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
        print(f"🔄 Converting audio format...")
    
    # Load audio
    audio = AudioSegment.from_file(input_path)
    
    # Convert to mono and resample
    if channels == 1:
        audio = audio.set_channels(1)
    
    audio = audio.set_frame_rate(sample_rate)
    
    # Export
    audio.export(output_path, format=output_format)
    
    if verbose:
        print(f"✓ Converted audio saved: {output_path}")
    
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
        print(f"🎬 Extracting audio from video...")
    
    try:
        # Use pydub which uses ffmpeg internally
        audio = AudioSegment.from_file(video_path)
        audio.export(output_audio_path, format=audio_format)
        
        if verbose:
            print(f"✓ Audio extracted: {output_audio_path}")
        
        return output_audio_path
    except Exception as e:
        raise RuntimeError(f"Failed to extract audio. Make sure ffmpeg is installed: {e}")


# Higher-level workflow functions

def audio_to_voiceover_workflow(
    input_audio: str,
    output_audio: str,
    whisper_url: str,
    edge_tts_url: str,
    api_key: str,
    speaker_voices: Optional[Dict[str, str]] = None,
    default_voice: str = "en-US-AndrewMultilingualNeural",
    temp_srt: str = "temp_transcription.srt",
    language: Optional[str] = None,
    speed: float = 1.0,
    verbose: bool = True,
) -> Tuple[str, str]:
    """
    Complete workflow: Audio → Transcribe → Re-voice with different speakers.
    
    This is the "magic" function that does everything in one go!
    
    Args:
        input_audio: Input audio file path
        output_audio: Output audio file path
        whisper_url: Whisper API URL
        edge_tts_url: Edge TTS API URL
        api_key: API key
        speaker_voices: Dictionary mapping detected speakers to voices
        default_voice: Default voice
        temp_srt: Temporary SRT file path
        language: Optional language for transcription
        speed: Speech speed
        verbose: Print progress
        
    Returns:
        Tuple of (srt_path, output_audio_path)
    """
    from .core import build_voiceover_from_srt
    
    if verbose:
        print("=" * 60)
        print("🎙️  AUDIO RE-VOICING WORKFLOW")
        print("=" * 60)
        print()
    
    # Step 1: Transcribe
    if verbose:
        print("Step 1/2: Transcribing audio to SRT...")
    
    srt_path = transcribe_audio_to_srt(
        audio_path=input_audio,
        output_srt_path=temp_srt,
        whisper_url=whisper_url,
        api_key=api_key,
        language=language,
        verbose=verbose,
    )
    
    if verbose:
        print()
        print("Step 2/2: Generating new voiceover...")
    
    # Step 2: Re-voice
    build_voiceover_from_srt(
        srt_path=srt_path,
        output_audio_path=output_audio,
        edge_tts_url=edge_tts_url,
        api_key=api_key,
        speaker_voices=speaker_voices or {},
        default_voice=default_voice,
        speed=speed,
        verbose=verbose,
    )
    
    if verbose:
        print()
        print("=" * 60)
        print("✅ COMPLETE! Your re-voiced audio is ready!")
        print("=" * 60)
        print(f"📄 Transcription: {srt_path}")
        print(f"🎵 New audio: {output_audio}")
    
    return srt_path, output_audio

