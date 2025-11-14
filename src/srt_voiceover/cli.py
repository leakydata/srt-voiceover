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
        description="Convert SRT subtitle files to synchronized voiceover audio using Edge TTS",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Generate voiceover using a config file
  srt-voiceover input.srt -o output.mp3 --config config.yaml
  
  # Generate voiceover with direct parameters
  srt-voiceover input.srt -o output.mp3 --url http://localhost:5050/v1/audio/speech --api-key YOUR_KEY
  
  # Create a sample configuration file
  srt-voiceover --init-config config.yaml
  
  # List available voices (if your server supports it)
  srt-voiceover --list-voices --url http://localhost:5050
        """
    )
    
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
    
    args = parser.parse_args()
    
    # Handle --init-config
    if args.init_config:
        format_type = 'json' if args.init_config.endswith('.json') else 'yaml'
        create_sample_config(args.init_config, format_type)
        return
    
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


if __name__ == '__main__':
    main()

