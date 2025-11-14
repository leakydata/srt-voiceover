"""
Command-line interface for srt-voiceover
"""

import argparse
import sys
import json
import yaml
from pathlib import Path
from typing import Optional, Dict

from .core import build_voiceover_from_srt
from .transcribe import (
    transcribe_audio_to_srt,
    audio_to_voiceover_workflow,
    extract_audio_from_video,
    convert_audio_format,
)
from . import __version__


def load_config(config_path: str) -> Dict:
    """
    Load configuration from JSON or YAML file.
    
    Args:
        config_path: Path to config file
        
    Returns:
        Configuration dictionary
    """
    config_file = Path(config_path)
    
    if not config_file.exists():
        print(f"Error: Config file not found: {config_path}")
        sys.exit(1)
    
    with open(config_file, 'r', encoding='utf-8') as f:
        if config_path.endswith('.json'):
            return json.load(f)
        elif config_path.endswith(('.yaml', '.yml')):
            return yaml.safe_load(f)
        else:
            print("Error: Config file must be .json, .yaml, or .yml")
            sys.exit(1)


def create_sample_config(output_path: str, format: str = 'yaml') -> None:
    """
    Create a sample configuration file.
    
    Args:
        output_path: Path to save the sample config
        format: Format to use ('yaml' or 'json')
    """
    sample_config = {
        "edge_tts_url": "http://localhost:5050/v1/audio/speech",
        "api_key": "your_api_key_here",
        "default_voice": "en-US-AndrewMultilingualNeural",
        "response_format": "mp3",
        "speed": 1.0,
        "timing_tolerance_ms": 150,
        "speaker_voices": {
            "Nathan": "en-US-AndrewMultilingualNeural",
            "Nicole": "en-US-EmmaMultilingualNeural",
            "John": "en-US-GuyNeural",
            "Sarah": "en-US-JennyNeural",
        }
    }
    
    with open(output_path, 'w', encoding='utf-8') as f:
        if format == 'json':
            json.dump(sample_config, f, indent=2)
        else:
            yaml.dump(sample_config, f, default_flow_style=False, sort_keys=False)
    
    print(f"✓ Sample config created: {output_path}")


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Convert SRT subtitle files to synchronized voiceover audio using Edge TTS, or transcribe audio to SRT",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Generate voiceover from SRT
  srt-voiceover input.srt -o output.mp3 --config config.yaml
  
  # Transcribe audio to SRT
  srt-voiceover transcribe audio.mp3 -o output.srt --config config.yaml
  
  # Complete workflow: Audio → Transcribe → Re-voice
  srt-voiceover revoice input.mp3 -o output.mp3 --config config.yaml
  
  # Extract audio from video
  srt-voiceover extract-audio video.mp4 -o audio.wav
  
  # Create a sample configuration file
  srt-voiceover --init-config config.yaml
        """
    )
    
    # Subcommands
    subparsers = parser.add_subparsers(dest='command', help='Command to run')
    
    # Default command (no subcommand) - SRT to voiceover
    parser.add_argument('input', nargs='?', help='Input SRT file')
    parser.add_argument('-o', '--output', help='Output audio file (default: output.mp3)')
    parser.add_argument('-c', '--config', help='Configuration file (YAML or JSON)')
    parser.add_argument('--url', help='Edge TTS API URL')
    parser.add_argument('--api-key', help='API key for authentication')
    parser.add_argument('--default-voice', help='Default voice for unlabeled speakers')
    parser.add_argument('--format', choices=['mp3', 'wav'], help='Output audio format')
    parser.add_argument('--speed', type=float, help='Speech speed multiplier (default: 1.0)')
    parser.add_argument('--tolerance', type=int, help='Timing tolerance in milliseconds (default: 150)')
    parser.add_argument('-q', '--quiet', action='store_true', help='Suppress progress output')
    parser.add_argument('--init-config', metavar='FILE', help='Create a sample configuration file')
    parser.add_argument('--version', action='version', version=f'srt-voiceover {__version__}')
    
    # Transcribe subcommand
    transcribe_parser = subparsers.add_parser('transcribe', help='Transcribe audio to SRT file')
    transcribe_parser.add_argument('input', help='Input audio file (mp3, wav, m4a, etc.)')
    transcribe_parser.add_argument('-o', '--output', help='Output SRT file (default: output.srt)')
    transcribe_parser.add_argument('-c', '--config', help='Configuration file (YAML or JSON)')
    transcribe_parser.add_argument('--whisper-url', help='Whisper API URL')
    transcribe_parser.add_argument('--api-key', help='API key for authentication')
    transcribe_parser.add_argument('--language', help='Language code (en, es, fr, etc.)')
    transcribe_parser.add_argument('--model', default='whisper-1', help='Whisper model name')
    transcribe_parser.add_argument('--no-speaker-detection', action='store_true', help='Disable speaker detection')
    transcribe_parser.add_argument('-q', '--quiet', action='store_true', help='Suppress progress output')
    
    # Revoice subcommand (complete workflow)
    revoice_parser = subparsers.add_parser('revoice', help='Complete workflow: transcribe + re-voice audio')
    revoice_parser.add_argument('input', help='Input audio file')
    revoice_parser.add_argument('-o', '--output', help='Output audio file (default: revoiced.mp3)')
    revoice_parser.add_argument('-c', '--config', help='Configuration file (YAML or JSON)')
    revoice_parser.add_argument('--whisper-url', help='Whisper API URL')
    revoice_parser.add_argument('--tts-url', help='Edge TTS API URL')
    revoice_parser.add_argument('--api-key', help='API key for authentication')
    revoice_parser.add_argument('--language', help='Language code for transcription')
    revoice_parser.add_argument('--speed', type=float, help='Speech speed multiplier')
    revoice_parser.add_argument('--keep-srt', action='store_true', help='Keep temporary SRT file')
    revoice_parser.add_argument('-q', '--quiet', action='store_true', help='Suppress progress output')
    
    # Extract audio subcommand
    extract_parser = subparsers.add_parser('extract-audio', help='Extract audio from video file')
    extract_parser.add_argument('input', help='Input video file')
    extract_parser.add_argument('-o', '--output', help='Output audio file (default: extracted.wav)')
    extract_parser.add_argument('--format', choices=['mp3', 'wav'], default='wav', help='Output audio format')
    extract_parser.add_argument('-q', '--quiet', action='store_true', help='Suppress progress output')
    
    args = parser.parse_args()
    
    # Handle --init-config
    if hasattr(args, 'init_config') and args.init_config:
        format_type = 'json' if args.init_config.endswith('.json') else 'yaml'
        create_sample_config(args.init_config, format_type)
        return
    
    # Route to appropriate command handler
    if args.command == 'transcribe':
        handle_transcribe_command(args)
    elif args.command == 'revoice':
        handle_revoice_command(args)
    elif args.command == 'extract-audio':
        handle_extract_audio_command(args)
    else:
        handle_voiceover_command(args, parser)
    
def handle_voiceover_command(args, parser):
    """Handle the default voiceover command (SRT to audio)."""
    # Check if input file is provided
    if not args.input:
        parser.error("the following arguments are required: input")
    
    # Load config if provided
    config = {}
    if args.config:
        config = load_config(args.config)
    
    # Get parameters (CLI args override config)
    edge_tts_url = args.url or config.get('edge_tts_url')
    api_key = args.api_key or config.get('api_key')
    default_voice = args.default_voice or config.get('default_voice', 'en-US-AndrewMultilingualNeural')
    response_format = args.format or config.get('response_format', 'mp3')
    speed = args.speed if args.speed is not None else config.get('speed', 1.0)
    timing_tolerance_ms = args.tolerance if args.tolerance is not None else config.get('timing_tolerance_ms', 150)
    speaker_voices = config.get('speaker_voices', {})
    
    # Validate required parameters
    if not edge_tts_url:
        print("Error: Edge TTS URL is required. Use --url or provide it in config file.")
        sys.exit(1)
    
    if not api_key:
        print("Error: API key is required. Use --api-key or provide it in config file.")
        sys.exit(1)
    
    # Set output path
    output_path = args.output or f"output.{response_format}"
    
    # Check if input file exists
    if not Path(args.input).exists():
        print(f"Error: Input file not found: {args.input}")
        sys.exit(1)
    
    # Run the conversion
    try:
        print(f"Converting {args.input} to {output_path}...")
        build_voiceover_from_srt(
            srt_path=args.input,
            output_audio_path=output_path,
            edge_tts_url=edge_tts_url,
            api_key=api_key,
            speaker_voices=speaker_voices,
            default_voice=default_voice,
            response_format=response_format,
            speed=speed,
            timing_tolerance_ms=timing_tolerance_ms,
            verbose=not args.quiet,
        )
        print("✓ Conversion complete!")
    except Exception as e:
        print(f"Error during conversion: {e}")
        sys.exit(1)


def handle_transcribe_command(args):
    """Handle the transcribe command (audio to SRT)."""
    config = {}
    if args.config:
        config = load_config(args.config)
    
    # Check for optional API usage
    use_api = config.get('use_whisper_api', False)
    api_url = args.whisper_url or config.get('whisper_api_url')
    api_key = args.api_key or config.get('whisper_api_key', '')
    
    language = args.language or config.get('language')
    model = args.model  # Model name/size
    
    output_path = args.output or "output.srt"
    
    if not Path(args.input).exists():
        print(f"Error: Input file not found: {args.input}")
        sys.exit(1)
    
    try:
        transcribe_audio_to_srt(
            audio_path=args.input,
            output_srt_path=output_path,
            model=model,
            language=language,
            enable_speaker_detection=not args.no_speaker_detection,
            verbose=not args.quiet,
            use_api=use_api or (api_url is not None),
            api_url=api_url,
            api_key=api_key,
        )
        print(f"✓ Transcription complete: {output_path}")
    except ImportError as e:
        print(f"\n❌ {e}")
        print("\nTo use transcription features, install:")
        print("  pip install openai-whisper")
        print("\nOr install with transcription support:")
        print("  pip install srt-voiceover[transcription]")
        sys.exit(1)
    except Exception as e:
        print(f"Error during transcription: {e}")
        sys.exit(1)


def handle_revoice_command(args):
    """Handle the revoice command (complete workflow)."""
    config = {}
    if args.config:
        config = load_config(args.config)
    
    # Transcription settings
    use_whisper_api = config.get('use_whisper_api', False)
    whisper_api_url = args.whisper_url or config.get('whisper_api_url')
    whisper_api_key = args.api_key or config.get('whisper_api_key')
    whisper_model = config.get('whisper_model', 'base')
    
    # TTS settings
    tts_url = args.tts_url or config.get('edge_tts_url')
    tts_api_key = args.api_key or config.get('api_key', '')
    
    language = args.language or config.get('language')
    speed = args.speed if args.speed is not None else config.get('speed', 1.0)
    speaker_voices = config.get('speaker_voices', {})
    default_voice = config.get('default_voice', 'en-US-AndrewMultilingualNeural')
    
    if not tts_url:
        print("Error: Edge TTS URL is required. Use --tts-url or provide edge_tts_url in config file.")
        sys.exit(1)
    
    output_path = args.output or "revoiced.mp3"
    temp_srt = "temp_transcription.srt" if not args.keep_srt else output_path.replace('.mp3', '.srt').replace('.wav', '.srt')
    
    if not Path(args.input).exists():
        print(f"Error: Input file not found: {args.input}")
        sys.exit(1)
    
    try:
        srt_path, audio_path = audio_to_voiceover_workflow(
            input_audio=args.input,
            output_audio=output_path,
            edge_tts_url=tts_url,
            edge_tts_api_key=tts_api_key,
            speaker_voices=speaker_voices,
            default_voice=default_voice,
            temp_srt=temp_srt,
            language=language,
            speed=speed,
            whisper_model=whisper_model,
            verbose=not args.quiet,
            use_whisper_api=use_whisper_api or (whisper_api_url is not None),
            whisper_api_url=whisper_api_url,
            whisper_api_key=whisper_api_key,
        )
        
        # Clean up temp SRT if not keeping it
        if not args.keep_srt and srt_path == "temp_transcription.srt":
            try:
                Path(srt_path).unlink()
            except:
                pass
        
        print(f"\n✓ Re-voicing complete: {audio_path}")
    except ImportError as e:
        print(f"\n❌ {e}")
        print("\nTo use re-voicing features, install:")
        print("  pip install openai-whisper")
        print("\nOr install with all features:")
        print("  pip install srt-voiceover[all]")
        sys.exit(1)
    except Exception as e:
        print(f"Error during re-voicing: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


def handle_extract_audio_command(args):
    """Handle the extract-audio command."""
    output_path = args.output or f"extracted.{args.format}"
    
    if not Path(args.input).exists():
        print(f"Error: Input file not found: {args.input}")
        sys.exit(1)
    
    try:
        extract_audio_from_video(
            video_path=args.input,
            output_audio_path=output_path,
            audio_format=args.format,
            verbose=not args.quiet,
        )
        print(f"✓ Audio extracted: {output_path}")
    except Exception as e:
        print(f"Error during audio extraction: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()

