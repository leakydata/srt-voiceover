# Quick Start Guide

Get up and running with srt-voiceover in 5 minutes!

## Step 1: Install Prerequisites

### Install FFmpeg

**Windows:**
1. Download from https://ffmpeg.org/download.html
2. Extract to `C:\ffmpeg`
3. Add `C:\ffmpeg\bin` to your PATH environment variable

**macOS:**
```bash
brew install ffmpeg
```

**Linux (Ubuntu/Debian):**
```bash
sudo apt-get update
sudo apt-get install ffmpeg
```

### Install Edge TTS Server

```bash
# Clone the server
git clone https://github.com/travisvn/openai-edge-tts.git
cd openai-edge-tts

# Install dependencies
npm install

# Start the server (keep this running)
npm start
```

The server will run on `http://localhost:5050`

## Step 2: Install srt-voiceover

```bash
# Install from source
git clone https://github.com/leakydata/srt-voiceover.git
cd srt-voiceover
pip install -e .
```

Or once published to PyPI:
```bash
pip install srt-voiceover
```

## Step 3: Create Configuration

```bash
# Generate a sample config file
srt-voiceover --init-config config.yaml
```

Edit `config.yaml`:
```yaml
edge_tts_url: "http://localhost:5050/v1/audio/speech"
api_key: "your_api_key_here"  # Change this to your actual key
default_voice: "en-US-AndrewMultilingualNeural"
response_format: "mp3"
speed: 1.0

speaker_voices:
  Nathan: "en-US-AndrewMultilingualNeural"
  Nicole: "en-US-EmmaMultilingualNeural"
  # Add your speakers here
```

## Step 4: Prepare Your SRT File

Create or edit your SRT file with speaker labels:

**example.srt:**
```srt
1
00:00:00,000 --> 00:00:03,500
Nathan: Welcome to this tutorial.

2
00:00:03,500 --> 00:00:07,000
Nicole: Let's get started with the basics.

3
00:00:07,500 --> 00:00:10,000
Nathan: First, we'll cover installation.
```

## Step 5: Generate Voiceover

```bash
srt-voiceover example.srt -o output.mp3 --config config.yaml
```

That's it! Your voiceover will be saved as `output.mp3`

## Troubleshooting

### "Edge TTS server not responding"
- Make sure the server is running: `npm start` in the openai-edge-tts directory
- Check it's accessible: Open http://localhost:5050 in your browser

### "FFmpeg not found"
- Verify FFmpeg is installed: `ffmpeg -version`
- Add FFmpeg to your PATH environment variable

### "Invalid API key"
- Check your config.yaml has the correct API key
- If using the default openai-edge-tts server, any non-empty string works

### Voice doesn't match speaker
- Verify speaker names in SRT match those in config.yaml (case-sensitive)
- Use the default_voice for unlabeled dialogue

## Next Steps

- Check out [edgetts_voices_list.md](edgetts_voices_list.md) for all available voices
- See [README.md](README.md) for advanced usage
- Try different speed settings (0.8-1.2 works well for most content)
- Experiment with timing tolerance for faster processing

## Common Use Cases

### Video Dubbing
```bash
srt-voiceover video_subs.srt -o dubbed_audio.mp3 -c config.yaml
# Then merge with video using video editing software
```

### Podcast Creation
```bash
srt-voiceover script.srt -o podcast.mp3 -c config.yaml --speed 0.95
```

### Quick Test
```bash
# Use the included sample
srt-voiceover examples/sample.srt -o test.mp3 -c examples/config.yaml
```

Need help? Open an issue on [GitHub](https://github.com/leakydata/srt-voiceover/issues)!

