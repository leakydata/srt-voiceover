"""
Command-line interface for srt-voiceover
"""

import argparse
import sys
import json
import yaml
import logging
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


def detect_device():
    """Detect if CUDA GPU is available and return device."""
    try:
        import torch
        if torch.cuda.is_available():
            device = "cuda"
            gpu_name = torch.cuda.get_device_name(0)
            return device, gpu_name
        else:
            return "cpu", None
    except ImportError:
        return "cpu", None


def list_available_voices():
    """List all available Edge TTS voices using the edge-tts module."""
    import asyncio
    import edge_tts
    
    async def _list_voices():
        print("Fetching available Edge TTS voices...\n")
        voices = await edge_tts.list_voices()
        
        # Group by language
        by_language = {}
        for voice in voices:
            lang = voice['Locale']
            if lang not in by_language:
                by_language[lang] = []
            by_language[lang].append(voice)
        
        # Print organized list
        for lang in sorted(by_language.keys()):
            print(f"\n{lang}:")
            print("-" * 80)
            for voice in sorted(by_language[lang], key=lambda v: v['ShortName']):
                gender = voice.get('Gender', 'Unknown')
                name = voice['ShortName']
                friendly_name = voice.get('FriendlyName', voice.get('LocalName', name))
                
                # Handle Unicode characters in voice names for Windows console
                try:
                    print(f"  {name:50s} [{gender}] - {friendly_name}")
                except UnicodeEncodeError:
                    # Fallback: encode with errors='replace' or use ASCII-only friendly name
                    friendly_name_safe = friendly_name.encode('ascii', errors='replace').decode('ascii')
                    print(f"  {name:50s} [{gender}] - {friendly_name_safe}")
        
        print(f"\n\nTotal voices available: {len(voices)}")
        print("\nUsage: Specify voice in config.yaml or with --default-voice flag")
    
    asyncio.run(_list_voices())


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
        "default_voice": "en-US-AndrewMultilingualNeural",
        "rate": "+0%",
        "volume": "+0%",
        "pitch": "+0Hz",
        "timing_tolerance_ms": 150,
        "enable_time_stretch": False,
        "whisper_model": "base",
        "speaker_voices": {
            "Nathan": "en-US-AndrewMultilingualNeural",
            "Nicole": "en-US-EmmaMultilingualNeural",
            "John": "en-US-GuyNeural",
            "Sarah": "en-US-JennyNeural",
            "Speaker A": "en-US-AndrewMultilingualNeural",
            "Speaker B": "en-US-EmmaMultilingualNeural",
        }
    }
    
    with open(output_path, 'w', encoding='utf-8') as f:
        if format == 'json':
            json.dump(sample_config, f, indent=2)
        else:
            yaml.dump(sample_config, f, default_flow_style=False, sort_keys=False)
    
    print(f"Sample config created: {output_path}")


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Convert SRT subtitle files to synchronized voiceover audio using Edge TTS, or transcribe audio to SRT",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Generate voiceover from SRT (default command)
  srt-voiceover input.srt -o output.mp3 -c config.yaml
  
  # Or explicitly use voiceover command
  srt-voiceover voiceover input.srt -o output.mp3 -c config.yaml
  
  # Transcribe audio to SRT
  srt-voiceover transcribe audio.mp3 -o output.srt -c config.yaml
  
  # Complete workflow: Audio -> Transcribe -> Re-voice
  srt-voiceover revoice input.mp3 -o output.mp3 -c config.yaml
  
  # Extract audio from video
  srt-voiceover extract-audio video.mp4 -o audio.wav
  
  # Create a sample configuration file
  srt-voiceover --init-config config.yaml
        """
    )
    
    # Global options
    parser.add_argument('--init-config', metavar='FILE', help='Create a sample configuration file')
    parser.add_argument('--list-voices', action='store_true', help='List all available Edge TTS voices')
    parser.add_argument('-v', '--verbose', action='store_true', help='Enable verbose logging (show debug messages)')
    parser.add_argument('--version', action='version', version=f'srt-voiceover {__version__}')
    
    # Subcommands
    subparsers = parser.add_subparsers(dest='command', help='Command to run')
    
    # Default/voiceover command - SRT to voiceover
    voiceover_parser = subparsers.add_parser('voiceover', help='Convert SRT -> voiceover (default if no command)', add_help=False)
    voiceover_parser.add_argument('input', help='Input SRT file')
    voiceover_parser.add_argument('-o', '--output', help='Output audio file (default: output.mp3)')
    voiceover_parser.add_argument('-c', '--config', help='Configuration file (YAML or JSON)')
    voiceover_parser.add_argument('--default-voice', help='Default voice for unlabeled speakers')
    voiceover_parser.add_argument('--rate', help='Speech rate (e.g., "+0%%", "-50%%", "+100%%")')
    voiceover_parser.add_argument('--volume', help='Volume level (e.g., "+0%%", "-50%%", "+100%%")')
    voiceover_parser.add_argument('--pitch', help='Pitch adjustment (e.g., "+0Hz", "-50Hz", "+100Hz")')
    voiceover_parser.add_argument('--tolerance', type=int, help='Timing tolerance in milliseconds (default: 150)')
    voiceover_parser.add_argument('--enable-time-stretch', action='store_true',
                                    help='Use smart time-stretching for better lip-sync (requires: pip install librosa soundfile)')
    voiceover_parser.add_argument('--word-timings', help='Path to word timings JSON file (from transcribe --save-word-timings)')
    voiceover_parser.add_argument('--elastic-timing', action='store_true',
                                    help='Enable elastic timing with rate smoothing (requires --word-timings)')
    voiceover_parser.add_argument('-q', '--quiet', action='store_true', help='Suppress progress output')
    
    # Transcribe subcommand
    transcribe_parser = subparsers.add_parser('transcribe', help='Transcribe audio to SRT file')
    transcribe_parser.add_argument('input', help='Input audio file (mp3, wav, m4a, etc.)')
    transcribe_parser.add_argument('-o', '--output', help='Output SRT file (default: output.srt)')
    transcribe_parser.add_argument('-c', '--config', help='Configuration file (YAML or JSON)')
    transcribe_parser.add_argument('--whisper-url', help='Whisper API URL')
    transcribe_parser.add_argument('--api-key', help='API key for authentication')
    transcribe_parser.add_argument('--language', help='Language code (en, es, fr, etc.)')
    transcribe_parser.add_argument('--model', default='base', help='Whisper model name (base, small, medium, large for local; whisper-1 for API)')
    transcribe_parser.add_argument('--multi-speaker', action='store_true', 
                                    help='Enable basic multi-speaker detection (default: single speaker)')
    transcribe_parser.add_argument('--use-pyannote', action='store_true',
                                    help='Use pyannote.audio for professional speaker diarization (requires HF_TOKEN env var)')
    transcribe_parser.add_argument('--device', choices=['auto', 'cpu', 'cuda'], default='auto',
                                    help='Device to use for transcription/diarization (default: auto)')
    transcribe_parser.add_argument('--save-word-timings', action='store_true',
                                    help='Save word-level timings to JSON file for later use (enables two-step workflow)')
    transcribe_parser.add_argument('--translate-to', metavar='LANG',
                                    help='Translate transcribed SRT to target language (e.g., es, fr, de) using Ollama')
    transcribe_parser.add_argument('--ollama-base-url',
                                    help='Ollama API base URL (default: http://localhost:11434)')
    transcribe_parser.add_argument('--translation-model', default='gpt-oss:20b',
                                    help='Ollama model for translation (default: gpt-oss:20b)')
    transcribe_parser.add_argument('-q', '--quiet', action='store_true', help='Suppress progress output')
    
    # Revoice subcommand (complete workflow)
    revoice_parser = subparsers.add_parser('revoice', help='Complete workflow: transcribe + re-voice audio')
    revoice_parser.add_argument('input', help='Input audio file')
    revoice_parser.add_argument('-o', '--output', help='Output audio file (default: revoiced.mp3)')
    revoice_parser.add_argument('-c', '--config', help='Configuration file (YAML or JSON)')
    revoice_parser.add_argument('--default-voice', help='Default voice for unlabeled speakers')
    revoice_parser.add_argument('--whisper-url', help='Whisper API URL (for API mode)')
    revoice_parser.add_argument('--api-key', help='API key for Whisper API (if using API mode)')
    revoice_parser.add_argument('--language', help='Language code for transcription')
    revoice_parser.add_argument('--rate', help='Speech rate (e.g., "+0%%", "-50%%")')
    revoice_parser.add_argument('--volume', help='Volume level (e.g., "+0%%", "-50%%")')
    revoice_parser.add_argument('--pitch', help='Pitch adjustment (e.g., "+0Hz", "-50Hz")')
    revoice_parser.add_argument('--multi-speaker', action='store_true',
                                 help='Enable basic multi-speaker detection (default: single speaker)')
    revoice_parser.add_argument('--use-pyannote', action='store_true',
                                 help='Use pyannote.audio for professional speaker diarization (requires HF_TOKEN env var)')
    revoice_parser.add_argument('--device', choices=['auto', 'cpu', 'cuda'], default='auto',
                                 help='Device to use for transcription/diarization (default: auto)')
    revoice_parser.add_argument('--enable-time-stretch', action='store_true',
                                 help='Use smart time-stretching for better lip-sync (requires: pip install librosa soundfile)')
    revoice_parser.add_argument('--use-word-timing', action='store_true',
                                 help='Use word-level timing for dynamic rate matching (recommended for best quality)')
    revoice_parser.add_argument('--elastic-timing', action='store_true',
                                 help='Enable elastic timing windows - adjusts subtitle timing to reduce speed changes (requires --use-word-timing)')
    revoice_parser.add_argument('--translate-to', metavar='LANG',
                                 help='Translate transcribed SRT to target language (e.g., es, fr, de) using Ollama')
    revoice_parser.add_argument('--ollama-base-url',
                                 help='Ollama API base URL (default: http://localhost:11434)')
    revoice_parser.add_argument('--translation-model', default='gpt-oss:20b',
                                 help='Ollama model for translation (default: gpt-oss:20b)')
    revoice_parser.add_argument('--keep-srt', action='store_true', help='Keep temporary SRT file')
    revoice_parser.add_argument('-q', '--quiet', action='store_true', help='Suppress progress output')
    
    # Extract audio subcommand
    extract_parser = subparsers.add_parser('extract-audio', help='Extract audio from video file')
    extract_parser.add_argument('input', help='Input video file')
    extract_parser.add_argument('-o', '--output', help='Output audio file (default: extracted.wav)')
    extract_parser.add_argument('--format', choices=['mp3', 'wav'], default='wav', help='Output audio format')
    extract_parser.add_argument('-q', '--quiet', action='store_true', help='Suppress progress output')
    
    # Check if first arg is a subcommand or looks like a file
    if len(sys.argv) > 1:
        first_arg = sys.argv[1]
        # If first arg is not a known command and not a flag, assume it's voiceover command
        if not first_arg.startswith('-') and first_arg not in ['voiceover', 'transcribe', 'revoice', 'extract-audio']:
            # Insert 'voiceover' command
            sys.argv.insert(1, 'voiceover')
    
    args = parser.parse_args()

    # Configure logging based on verbose flag
    log_level = logging.DEBUG if args.verbose else logging.INFO
    logging.basicConfig(
        level=log_level,
        format='[%(name)s] %(levelname)s: %(message)s'
    )

    if args.verbose:
        print("[DEBUG] Verbose logging enabled\n")

    # Handle --init-config
    if args.init_config:
        format_type = 'json' if args.init_config.endswith('.json') else 'yaml'
        create_sample_config(args.init_config, format_type)
        return
    
    # Handle --list-voices
    if args.list_voices:
        list_available_voices()
        return
    
    # Route to appropriate command handler
    if args.command == 'transcribe':
        handle_transcribe_command(args)
    elif args.command == 'revoice':
        handle_revoice_command(args)
    elif args.command == 'extract-audio':
        handle_extract_audio_command(args)
    elif args.command == 'voiceover':
        handle_voiceover_command(args, parser)
    else:
        parser.print_help()
        sys.exit(1)
    
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
    default_voice = args.default_voice or config.get('default_voice', 'en-US-AndrewMultilingualNeural')
    rate = args.rate or config.get('rate', '+0%')
    volume = args.volume or config.get('volume', '+0%')
    pitch = args.pitch or config.get('pitch', '+0Hz')
    timing_tolerance_ms = args.tolerance if args.tolerance is not None else config.get('timing_tolerance_ms', 150)
    enable_time_stretch = args.enable_time_stretch or config.get('enable_time_stretch', False)
    elastic_timing = args.elastic_timing or config.get('elastic_timing', False)
    speaker_voices = config.get('speaker_voices', {})
    
    # Load word timings from JSON if provided
    word_timings = None
    if args.word_timings:
        word_timings_path = args.word_timings
        if not Path(word_timings_path).exists():
            print(f"Error: Word timings file not found: {word_timings_path}")
            sys.exit(1)
        
        try:
            with open(word_timings_path, 'r', encoding='utf-8') as f:
                word_timings = json.load(f)
            if not args.quiet:
                print(f"Loaded word timings from: {word_timings_path}")
                print(f"  Total words: {len(word_timings)}")
        except Exception as e:
            print(f"Error loading word timings: {e}")
            sys.exit(1)
    
    # Validate: elastic timing requires word timings
    if elastic_timing and not word_timings:
        print("Error: --elastic-timing requires --word-timings to be provided")
        print("Tip: Use 'srt-voiceover transcribe --save-word-timings' to generate word timings")
        sys.exit(1)
    
    # Set output path
    output_path = args.output or "output.mp3"
    
    # Check if input file exists
    if not Path(args.input).exists():
        print(f"Error: Input file not found: {args.input}")
        sys.exit(1)
    
    # Run the conversion
    try:
        print(f"Converting {args.input} to {output_path}...")
        if word_timings:
            print(f"Using word-level timing with {len(word_timings)} word timestamps")
        if elastic_timing:
            print(f"Elastic timing with rate smoothing enabled")
        
        build_voiceover_from_srt(
            srt_path=args.input,
            output_audio_path=output_path,
            speaker_voices=speaker_voices,
            default_voice=default_voice,
            rate=rate,
            volume=volume,
            pitch=pitch,
            timing_tolerance_ms=timing_tolerance_ms,
            enable_time_stretch=enable_time_stretch,
            word_timings=word_timings,
            elastic_timing=elastic_timing,
            verbose=not args.quiet,
        )
        print("[OK] Conversion complete!")
    except ImportError as e:
        print(f"\n[ERROR] {e}")
        print("\nTo use voiceover features, install:")
        print("  pip install edge-tts")
        sys.exit(1)
    except Exception as e:
        print(f"Error during conversion: {e}")
        sys.exit(1)


def handle_transcribe_command(args):
    """Handle the transcribe command (audio to SRT)."""
    config = {}
    if args.config:
        config = load_config(args.config)
    
    # Detect/set device
    if args.device == 'auto':
        device, gpu_name = detect_device()
        if not args.quiet and device == 'cuda':
            print(f"GPU detected: {gpu_name}")
            print(f"Using device: {device}")
    else:
        device = args.device
        if not args.quiet:
            print(f"Using device: {device}")
    
    # Check for optional API usage
    use_api = config.get('use_whisper_api', False)
    api_url = args.whisper_url or config.get('whisper_api_url')
    api_key = args.api_key or config.get('whisper_api_key', '')
    
    language = args.language or config.get('language')
    model = args.model  # Model name/size
    
    output_path = args.output or "output.srt"
    
    # Generate word timings path if requested
    save_word_timings_path = None
    if args.save_word_timings:
        # Create path like: output.srt -> output_word_timings.json
        base_name = output_path.replace('.srt', '')
        save_word_timings_path = f"{base_name}_word_timings.json"
    
    if not Path(args.input).exists():
        print(f"Error: Input file not found: {args.input}")
        sys.exit(1)
    
    try:
        transcribe_audio_to_srt(
            audio_path=args.input,
            output_srt_path=output_path,
            model=model,
            language=language,
            enable_speaker_detection=args.multi_speaker,
            verbose=not args.quiet,
            use_api=use_api or (api_url is not None),
            api_url=api_url,
            api_key=api_key,
            use_pyannote=args.use_pyannote,
            device=device,
            use_word_timing=args.save_word_timings,  # Enable word timing if saving
            save_word_timings_path=save_word_timings_path,
        )
        print(f"[OK] Transcription complete: {output_path}")

        # Handle translation if requested
        if args.translate_to:
            try:
                from .translation import OllamaConfig, translate_srt, OllamaConnectionError

                # Create Ollama config with CLI or config file settings
                ollama_base_url = args.ollama_base_url or config.get('ollama_base_url', 'http://localhost:11434')
                translation_model = args.translation_model or config.get('translation_model', 'mistral')

                ollama_config = OllamaConfig(
                    base_url=ollama_base_url,
                    model=translation_model,
                )

                # Validate Ollama connection
                if not args.quiet:
                    print(f"\nValidating Ollama connection...")
                if not ollama_config.validate(verbose=not args.quiet):
                    print("[ERROR] Ollama validation failed. Translation skipped.")
                    if not args.quiet:
                        print(f"Tip: Make sure Ollama is running at {ollama_base_url}")
                else:
                    # Translate the SRT
                    translated_path = translate_srt(
                        srt_path=output_path,
                        target_language=args.translate_to,
                        config=ollama_config,
                        verbose=not args.quiet,
                    )
                    print(f"[OK] Translation complete: {translated_path}")
                    # Update output_path to point to translated file for workflow tip
                    output_path = translated_path

            except ImportError:
                print("[ERROR] Translation requires: pip install requests")
                sys.exit(1)
            except OllamaConnectionError as e:
                print(f"[ERROR] {e}")
                sys.exit(1)
            except Exception as e:
                print(f"[ERROR] Translation failed: {e}")
                sys.exit(1)

        if save_word_timings_path:
            print(f"\n[WORKFLOW TIP] You can now:")
            print(f"  1. Edit '{output_path}' to fix any transcription errors")
            print(f"  2. Generate voiceover: srt-voiceover voiceover {output_path} -o output.mp3 --word-timings {save_word_timings_path}")
    except ImportError as e:
        print(f"\n[ERROR] {e}")
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
    
    # Detect/set device
    if args.device == 'auto':
        device, gpu_name = detect_device()
        if not args.quiet and device == 'cuda':
            print(f"GPU detected: {gpu_name}")
            print(f"Using device: {device}")
    else:
        device = args.device
        if not args.quiet:
            print(f"Using device: {device}")
    
    # Transcription settings
    use_whisper_api = config.get('use_whisper_api', False)
    whisper_api_url = args.whisper_url or config.get('whisper_api_url')
    whisper_api_key = args.api_key or config.get('whisper_api_key')
    whisper_model = config.get('whisper_model', 'base')
    
    # Get pyannote setting from config or CLI
    use_pyannote = args.use_pyannote or config.get('use_pyannote', False)
    
    # TTS settings
    language = args.language or config.get('language')
    rate = args.rate or config.get('rate', '+0%')
    volume = args.volume or config.get('volume', '+0%')
    pitch = args.pitch or config.get('pitch', '+0Hz')
    enable_time_stretch = args.enable_time_stretch or config.get('enable_time_stretch', False)
    use_word_timing = args.use_word_timing or config.get('use_word_timing', False)
    elastic_timing = args.elastic_timing or config.get('elastic_timing', False)
    
    # Validate: elastic timing requires word timing
    if elastic_timing and not use_word_timing:
        print("Error: --elastic-timing requires --use-word-timing to be enabled")
        print("Try: srt-voiceover revoice input.mp4 --use-word-timing --elastic-timing")
        sys.exit(1)
    
    speaker_voices = config.get('speaker_voices', {})
    default_voice = args.default_voice or config.get('default_voice', 'en-US-AndrewMultilingualNeural')
    
    output_path = args.output or "revoiced.mp3"
    temp_srt = "temp_transcription.srt" if not args.keep_srt else output_path.replace('.mp3', '.srt').replace('.wav', '.srt')
    
    if not Path(args.input).exists():
        print(f"Error: Input file not found: {args.input}")
        sys.exit(1)
    
    # Check if input is a video file - if so, extract audio first
    input_file = Path(args.input)
    video_extensions = ['.mp4', '.avi', '.mkv', '.mov', '.wmv', '.flv', '.webm']
    
    if input_file.suffix.lower() in video_extensions:
        print(f"Detected video file. Extracting audio first...")
        temp_audio = f"temp_extracted_audio_{input_file.stem}.wav"
        try:
            extract_audio_from_video(
                video_path=args.input,
                output_audio_path=temp_audio,
                audio_format='wav',
                verbose=not args.quiet
            )
            audio_input = temp_audio
        except Exception as e:
            print(f"Error extracting audio from video: {e}")
            sys.exit(1)
    else:
        audio_input = args.input
    
    try:
        # First transcribe the audio to get the original SRT
        from .transcribe import transcribe_audio_to_srt

        transcribe_result = transcribe_audio_to_srt(
            audio_path=audio_input,
            output_srt_path=temp_srt,
            model=whisper_model,
            language=language,
            enable_speaker_detection=args.multi_speaker,
            verbose=not args.quiet,
            use_api=use_whisper_api or (whisper_api_url is not None),
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

        # Handle translation if requested
        srt_for_voiceover = srt_path

        if args.translate_to:
            try:
                from .translation import OllamaConfig, translate_srt, OllamaConnectionError

                # Create Ollama config with CLI or config file settings
                ollama_base_url = args.ollama_base_url or config.get('ollama_base_url', 'http://localhost:11434')
                translation_model = args.translation_model or config.get('translation_model', 'gpt-oss:20b')

                ollama_config = OllamaConfig(
                    base_url=ollama_base_url,
                    model=translation_model,
                )

                # Validate Ollama connection
                if not args.quiet:
                    print()
                    print("[Validating] Connecting to Ollama at " + ollama_base_url + "...")
                if not ollama_config.validate(verbose=not args.quiet):
                    print("[ERROR] Ollama validation failed. Translation skipped.")
                    if not args.quiet:
                        print("Tip: Make sure Ollama is running at " + ollama_base_url)
                else:
                    # Translate the SRT
                    print()
                    srt_for_voiceover = translate_srt(
                        srt_path=srt_path,
                        target_language=args.translate_to,
                        config=ollama_config,
                        verbose=not args.quiet,
                    )
                    print("[OK] Translation complete: " + srt_for_voiceover)

            except ImportError:
                print("[ERROR] Translation requires: pip install requests")
                sys.exit(1)
            except OllamaConnectionError as e:
                print("[ERROR] " + str(e))
                sys.exit(1)
            except Exception as e:
                print("[ERROR] Translation failed: " + str(e))
                sys.exit(1)

        # Now generate voiceover from the appropriate SRT (translated or original)
        if not args.quiet:
            print()
            print("Step 2/2: Generating new voiceover...")
            if use_word_timing:
                print("Using word-level timing for dynamic rate matching...")

        # Build voiceover from the SRT (translated or original)
        quality_report = build_voiceover_from_srt(
            srt_path=srt_for_voiceover,
            output_audio_path=output_path,
            default_voice=default_voice,
            speaker_voices=speaker_voices,
            rate=rate,
            volume=volume,
            pitch=pitch,
            word_timings=word_timings,
            use_word_timing=use_word_timing,
            elastic_timing=elastic_timing,
            verbose=not args.quiet,
        )

        audio_path = output_path

        # Clean up temp files
        if not args.keep_srt and srt_path == "temp_transcription.srt":
            try:
                Path(srt_path).unlink()
            except:
                pass

        # Also clean up translated SRT if translation was done and keep_srt is False
        if not args.keep_srt and translated_srt_path != srt_path:
            try:
                Path(translated_srt_path).unlink()
            except:
                pass

        # Clean up temp extracted audio if we extracted it
        if input_file.suffix.lower() in video_extensions:
            try:
                Path(audio_input).unlink()
                if not args.quiet:
                    print(f"Cleaned up temporary audio file")
            except:
                pass

        print(f"\n[OK] Re-voicing complete: {audio_path}")
        
        # If input was video, offer to merge back
        if input_file.suffix.lower() in video_extensions and not args.quiet:
            output_video = output_path.replace('.mp3', '_dubbed.mp4').replace('.wav', '_dubbed.mp4')
            print(f"\nTo merge with original video, run:")
            print(f'  ffmpeg -i "{args.input}" -i "{audio_path}" -c:v copy -map 0:v:0 -map 1:a:0 "{output_video}"')
    except ImportError as e:
        print(f"\n[ERROR] {e}")
        print("\nTo use re-voicing features, install:")
        print("  pip install edge-tts openai-whisper")
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
        print(f"[OK] Audio extracted: {output_path}")
    except Exception as e:
        print(f"Error during audio extraction: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()

