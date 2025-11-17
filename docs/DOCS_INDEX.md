# Documentation Index

Welcome! This guide will help you find the right documentation for your needs.

## 🚀 Getting Started (Pick Your Path)

### I'm completely new - Show me how to get started quickly!
→ **[QUICKSTART.md](QUICKSTART.md)** (5 minutes)
- Installation
- Your first voiceover
- Three basic commands

### I want to learn about the new advanced features
→ **[QUICK_START_ENHANCEMENTS.md](QUICK_START_ENHANCEMENTS.md)** (10 minutes)
- Overview of new features
- Speaker detection explained
- Common scenarios
- Troubleshooting

### I'm ready for the complete guide
→ **[DOCUMENTATION.md](DOCUMENTATION.md)** (30 minutes)
- Full API reference
- All command-line options
- Detailed workflow examples
- Configuration options

---

## 📚 Deep Dives (By Feature)

### Advanced Features & Capabilities
→ **[ADVANCED_FEATURES.md](ADVANCED_FEATURES.md)** (20 minutes)

Covers:
- **Speaker Detection** (3 methods)
  - Explicit labels
  - Context-based detection
  - Statistics analysis
- **Fuzzy Word Matching**
  - Confidence scoring
  - Timing strategies
  - Handling variations
- **Voice Profiles** (30+ voices)
  - Per-voice baselines
  - Rate optimization
  - Characteristics
- **Quality Metrics**
  - Confidence tracking
  - Issue detection
  - JSON reporting
- **Multi-Format Export**
  - JSON, VTT, SRT, CSV, FCPXML
  - Integration examples

### Multi-Language Translation (NEW!)
→ **[TRANSLATION_GUIDE.md](TRANSLATION_GUIDE.md)** (15 minutes)

Phase 1 & 2 Ollama integration for automatic translation:
- Translation workflow (transcribe → translate → voiceover)
- Ollama setup (local and remote with ngrok)
- Supported languages (16+)
- CLI and Python API examples
- Batch processing
- Troubleshooting

### Implementation & Architecture
→ **[IMPLEMENTATION_SUMMARY.md](IMPLEMENTATION_SUMMARY.md)** (15 minutes)

For developers interested in:
- New module descriptions
- Core enhancements
- Design decisions
- Module organization
- Testing approach

---

## 🎯 Quick Reference

### By Use Case

| Use Case | Guide | Command |
|----------|-------|---------|
| Single speaker voiceover | QUICKSTART | `srt-voiceover voiceover input.srt -o output.mp3` |
| Multi-speaker with labels | QUICK_START_ENHANCEMENTS | `srt-voiceover revoice video.mp4 -o output.mp3 -c config.yaml` |
| Perfect video sync | ADVANCED_FEATURES | `srt-voiceover revoice video.mp4 -o output.mp3 --use-word-timing --elastic-timing` |
| Multilingual dubbing | TRANSLATION_GUIDE | `srt-voiceover revoice video.mp4 -o output.mp3 --translate-to es --use-word-timing` |
| Quality analysis | ADVANCED_FEATURES | See Quality Metrics section |
| Word timing export | ADVANCED_FEATURES | See Multi-Format Export section |

### By Feature

| Feature | Guide | Section |
|---------|-------|---------|
| Speaker detection | ADVANCED_FEATURES | Speaker Detection |
| Word matching | ADVANCED_FEATURES | Fuzzy Word Matching |
| Voice selection | QUICK_START_ENHANCEMENTS | Available Voices |
| Quality reporting | ADVANCED_FEATURES | Quality Metrics & Reporting |
| Export options | ADVANCED_FEATURES | Word Timing Export |
| Configuration | DOCUMENTATION | Configuration |
| Translation | TRANSLATION_GUIDE | Ollama Integration |
| Multi-language | README | Multi-Language Support |

---

## 📖 Reading Order (Recommended)

### For Users
1. Start here: **README.md** (overview)
2. Next: **QUICKSTART.md** (basic setup)
3. Explore: **QUICK_START_ENHANCEMENTS.md** (new features)
4. Deep dive: **ADVANCED_FEATURES.md** (specific features)
5. Reference: **DOCUMENTATION.md** (complete guide)

### For Contributors/Developers
1. Start here: **README.md** (project overview)
2. Next: **CONTRIBUTING.md** (development setup)
3. Architecture: **IMPLEMENTATION_SUMMARY.md** (technical details)
4. Code: **src/srt_voiceover/** (source code)
5. Reference: **DOCUMENTATION.md** (API reference)

---

## 🔗 Document Map

```
README.md (START HERE)
├── Overview & features
├── Installation
├── Basic examples
└── Links to guides

QUICKSTART.md (FIRST TIME?)
├── 30-second setup
├── 5-minute tutorial
├── Three basic commands
└── Common issues

QUICK_START_ENHANCEMENTS.md (NEW FEATURES)
├── 5-minute overview
├── Speaker handling
├── Voice optimization
├── Troubleshooting
└── Available voices

ADVANCED_FEATURES.md (DEEP DIVE)
├── Speaker detection (3 methods)
├── Fuzzy word matching
├── Voice profiles (30+)
├── Quality metrics
├── Export formats
└── Complete examples

TRANSLATION_GUIDE.md (MULTILINGUAL)
├── Ollama setup (local & remote)
├── Translation workflow
├── Supported languages (16+)
├── CLI & Python API
├── Batch processing
└── Troubleshooting

DOCUMENTATION.md (REFERENCE)
├── Full CLI reference
├── All options explained
├── Workflows explained
├── Configuration guide
└── Complete examples

IMPLEMENTATION_SUMMARY.md (TECHNICAL)
├── Module descriptions
├── Design decisions
├── Architecture overview
└── Testing examples

CONTRIBUTING.md (DEVELOPERS)
├── Development setup
├── Code style
├── Testing
└── Contribution process
```

---

## 📱 Cheat Sheets

### Common Commands

```bash
# Transcribe only
srt-voiceover transcribe audio.mp3 -o subs.srt

# SRT to voiceover
srt-voiceover voiceover subs.srt -o output.mp3

# Complete revoice (recommended)
srt-voiceover revoice video.mp4 -o output.mp3 --use-word-timing --elastic-timing

# With custom voices
srt-voiceover revoice video.mp4 -o output.mp3 -c config.yaml --use-word-timing

# Transcribe and translate to Spanish
srt-voiceover transcribe video.mp4 -o subs.srt --translate-to es

# Revoice with translation (complete workflow)
srt-voiceover revoice video.mp4 -o output.mp3 --translate-to es --use-word-timing

# With remote Ollama (ngrok)
srt-voiceover revoice video.mp4 -o output.mp3 --translate-to fr --ollama-base-url https://ngrok-url

# List voices
srt-voiceover --list-voices

# Create config
srt-voiceover --init-config config.yaml
```

### Key Features

| Feature | Flag | Docs |
|---------|------|------|
| Word-level timing | `--use-word-timing` | ADVANCED_FEATURES |
| Elastic timing | `--elastic-timing` | ADVANCED_FEATURES |
| Time stretching | `--enable-time-stretch` | DOCUMENTATION |
| Speaker detection | `--multi-speaker` | QUICK_START_ENHANCEMENTS |
| Translation (Ollama) | `--translate-to LANG` | TRANSLATION_GUIDE |
| Custom Ollama URL | `--ollama-base-url URL` | TRANSLATION_GUIDE |
| Professional diarization | `--use-pyannote` | DOCUMENTATION |
| GPU acceleration | `--device cuda` | README |
| Quality report | `verbose=True` | ADVANCED_FEATURES |

---

## ❓ FAQ

### Which guide should I read?
- **Just want to start?** → QUICKSTART.md
- **Want to understand features?** → QUICK_START_ENHANCEMENTS.md
- **Need complete reference?** → DOCUMENTATION.md
- **Interested in architecture?** → IMPLEMENTATION_SUMMARY.md

### What's new in this version?
→ See "Advanced Features (NEW!)" section in README.md

### How do I handle different subtitle types?
→ See "Handling Different Subtitle Types" in QUICK_START_ENHANCEMENTS.md

### How do I check if my voiceover is good quality?
→ See "Quality Metrics & Reporting" in ADVANCED_FEATURES.md

### Where are the Python examples?
→ See "Complete Example" sections in ADVANCED_FEATURES.md and DOCUMENTATION.md

---

## 📞 Getting Help

- **General questions?** → See QUICKSTART.md or DOCUMENTATION.md
- **Feature questions?** → See ADVANCED_FEATURES.md
- **Still stuck?** → Check CONTRIBUTING.md for support info
- **Bug report?** → See README.md "Support" section

---

## 🎓 Learning Path by Experience Level

### Beginner
Time: ~30 minutes
1. README.md (5 min) - Overview
2. QUICKSTART.md (5 min) - Get set up
3. QUICK_START_ENHANCEMENTS.md (10 min) - Learn basics
4. Run first command (10 min) - Try it yourself

### Intermediate
Time: ~60 minutes
1. QUICK_START_ENHANCEMENTS.md (10 min) - Features overview
2. ADVANCED_FEATURES.md (30 min) - Deep dive
3. DOCUMENTATION.md (20 min) - Reference

### Advanced
Time: ~90 minutes
1. IMPLEMENTATION_SUMMARY.md (20 min) - Architecture
2. Source code (30 min) - Read implementation
3. DOCUMENTATION.md (20 min) - API details
4. Experiment (20 min) - Build something custom

---

**Ready to start?** Go to [README.md](README.md) or [QUICKSTART.md](QUICKSTART.md)!
