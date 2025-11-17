"""
Per-voice rate adjustment profiles for natural-sounding speech.

Each voice has different baseline speaking rates and comfort zones
for speed adjustment. This module provides voice-specific optimization.
"""

from typing import Dict, Optional, List


# Voice profiles with baseline WPM and rate adjustment constraints
VOICE_PROFILES = {
    # English US Male Voices
    "en-US-AndrewMultilingualNeural": {
        "display_name": "Andrew (US Male, Multilingual)",
        "baseline_wpm": 155,
        "min_rate": -35,
        "max_rate": 35,
        "natural_pause_threshold": 0.3,
        "characteristics": "Clear, professional, neutral"
    },
    "en-US-GuyNeural": {
        "display_name": "Guy (US Male)",
        "baseline_wpm": 150,
        "min_rate": -40,
        "max_rate": 40,
        "natural_pause_threshold": 0.35,
        "characteristics": "Young, professional"
    },

    # English US Female Voices
    "en-US-EmmaMultilingualNeural": {
        "display_name": "Emma (US Female, Multilingual)",
        "baseline_wpm": 160,
        "min_rate": -40,
        "max_rate": 40,
        "natural_pause_threshold": 0.25,
        "characteristics": "Clear, engaging, professional"
    },
    "en-US-JennyNeural": {
        "display_name": "Jenny (US Female)",
        "baseline_wpm": 165,
        "min_rate": -35,
        "max_rate": 35,
        "natural_pause_threshold": 0.25,
        "characteristics": "Friendly, conversational"
    },
    "en-US-AriaNeural": {
        "display_name": "Aria (US Female)",
        "baseline_wpm": 158,
        "min_rate": -38,
        "max_rate": 38,
        "natural_pause_threshold": 0.28,
        "characteristics": "Natural, expressive"
    },

    # English GB Voices
    "en-GB-RyanNeural": {
        "display_name": "Ryan (UK Male)",
        "baseline_wpm": 145,
        "min_rate": -40,
        "max_rate": 35,
        "natural_pause_threshold": 0.4,
        "characteristics": "Friendly, approachable"
    },
    "en-GB-LibbyNeural": {
        "display_name": "Libby (UK Female)",
        "baseline_wpm": 150,
        "min_rate": -40,
        "max_rate": 35,
        "natural_pause_threshold": 0.35,
        "characteristics": "Clear, friendly"
    },

    # English AU Voices
    "en-AU-DuncanNeural": {
        "display_name": "Duncan (AU Male)",
        "baseline_wpm": 152,
        "min_rate": -35,
        "max_rate": 35,
        "natural_pause_threshold": 0.32,
        "characteristics": "Casual, friendly"
    },
    "en-AU-NatashaNeural": {
        "display_name": "Natasha (AU Female)",
        "baseline_wpm": 155,
        "min_rate": -35,
        "max_rate": 35,
        "natural_pause_threshold": 0.3,
        "characteristics": "Friendly, professional"
    },

    # English IN Voices
    "en-IN-NeerjaNeural": {
        "display_name": "Neerja (India Female)",
        "baseline_wpm": 160,
        "min_rate": -30,
        "max_rate": 40,
        "natural_pause_threshold": 0.25,
        "characteristics": "Expressive, engaging"
    },
    "en-IN-PrabhatNeural": {
        "display_name": "Prabhat (India Male)",
        "baseline_wpm": 158,
        "min_rate": -35,
        "max_rate": 35,
        "natural_pause_threshold": 0.28,
        "characteristics": "Professional, clear"
    },

    # Spanish Voices
    "es-ES-AlvaroNeural": {
        "display_name": "Álvaro (Spain Male)",
        "baseline_wpm": 148,
        "min_rate": -40,
        "max_rate": 35,
        "natural_pause_threshold": 0.35,
        "characteristics": "Formal, professional"
    },
    "es-MX-JorgeNeural": {
        "display_name": "Jorge (Mexico Male)",
        "baseline_wpm": 155,
        "min_rate": -35,
        "max_rate": 40,
        "natural_pause_threshold": 0.3,
        "characteristics": "Friendly, casual"
    },

    # French Voices
    "fr-FR-HenriNeural": {
        "display_name": "Henri (France Male)",
        "baseline_wpm": 140,
        "min_rate": -40,
        "max_rate": 35,
        "natural_pause_threshold": 0.4,
        "characteristics": "Formal, educated"
    },
    "fr-FR-DeniseNeural": {
        "display_name": "Denise (France Female)",
        "baseline_wpm": 145,
        "min_rate": -40,
        "max_rate": 35,
        "natural_pause_threshold": 0.38,
        "characteristics": "Professional, clear"
    },

    # German Voices
    "de-DE-KayanNeural": {
        "display_name": "Kayan (Germany Male)",
        "baseline_wpm": 135,
        "min_rate": -40,
        "max_rate": 30,
        "natural_pause_threshold": 0.45,
        "characteristics": "Professional, formal"
    },

    # Italian Voices
    "it-IT-DiegoNeural": {
        "display_name": "Diego (Italy Male)",
        "baseline_wpm": 150,
        "min_rate": -35,
        "max_rate": 35,
        "natural_pause_threshold": 0.3,
        "characteristics": "Expressive, warm"
    },

    # Japanese Voices
    "ja-JP-KeitaNeural": {
        "display_name": "Keita (Japan Male)",
        "baseline_wpm": 130,  # Japanese is faster but counted differently
        "min_rate": -30,
        "max_rate": 40,
        "natural_pause_threshold": 0.4,
        "characteristics": "Clear, professional"
    },

    # Mandarin Chinese Voices
    "zh-CN-YunxiNeural": {
        "display_name": "Yunxi (China Male)",
        "baseline_wpm": 125,  # Mandarin syllables
        "min_rate": -30,
        "max_rate": 40,
        "natural_pause_threshold": 0.35,
        "characteristics": "Clear, professional"
    },
}


def get_voice_profile(voice_id: str) -> Dict:
    """
    Get the voice profile for a given voice ID.

    Falls back to a safe default if voice not found.

    Args:
        voice_id: Edge TTS voice ID

    Returns:
        Dictionary with voice profile settings
    """
    if voice_id in VOICE_PROFILES:
        return VOICE_PROFILES[voice_id].copy()

    # Default safe profile for unknown voices
    return {
        "display_name": voice_id,
        "baseline_wpm": 150,
        "min_rate": -35,
        "max_rate": 35,
        "natural_pause_threshold": 0.3,
        "characteristics": "Unknown voice (using default)"
    }


def calculate_segment_rate_with_voice_profile(
    voice_id: str,
    wpm: float,
    prev_rate: Optional[int] = None,
    max_change_per_segment: int = 15
) -> int:
    """
    Calculate rate using voice-specific baseline and constraints.

    Args:
        voice_id: Edge TTS voice ID
        wpm: Measured words-per-minute from transcription
        prev_rate: Previous segment's rate (for smoothing)
        max_change_per_segment: Maximum allowed rate change from previous segment

    Returns:
        Rate percentage for this voice (e.g., +20, -15)
    """
    profile = get_voice_profile(voice_id)
    baseline_wpm = profile['baseline_wpm']
    min_rate = profile['min_rate']
    max_rate = profile['max_rate']

    # Calculate rate multiplier
    rate_multiplier = wpm / baseline_wpm
    rate_percent = int((rate_multiplier - 1.0) * 100)

    # Clamp to voice-specific range
    rate_percent = max(min_rate, min(max_rate, rate_percent))

    # Apply smoothing if we have a previous rate
    if prev_rate is not None:
        rate_change = rate_percent - prev_rate
        if abs(rate_change) > max_change_per_segment:
            if rate_change > 0:
                rate_percent = prev_rate + max_change_per_segment
            else:
                rate_percent = prev_rate - max_change_per_segment

    return rate_percent


def list_available_voices() -> List[Dict]:
    """
    Get list of all available voice profiles.

    Returns:
        List of voice profile dictionaries with 'id' and 'display_name'
    """
    voices = []
    for voice_id, profile in VOICE_PROFILES.items():
        voices.append({
            'id': voice_id,
            'display_name': profile['display_name'],
            'baseline_wpm': profile['baseline_wpm'],
            'characteristics': profile['characteristics']
        })
    return sorted(voices, key=lambda x: x['display_name'])


def print_voice_profiles(language: Optional[str] = None):
    """
    Print available voice profiles, optionally filtered by language.

    Args:
        language: Optional language code to filter (e.g., 'en-US', 'fr-FR')
    """
    voices = list_available_voices()

    if language:
        voices = [v for v in voices if v['id'].startswith(language)]

    print("\nAvailable Voice Profiles:")
    print("=" * 80)

    current_lang = None
    for voice in voices:
        lang = voice['id'].split('-')[0:2]
        lang_code = '-'.join(lang)

        if lang_code != current_lang:
            current_lang = lang_code
            print(f"\n{lang_code}:")

        profile = VOICE_PROFILES[voice['id']]
        print(
            f"  {voice['id']:<35} "
            f"(WPM: {profile['baseline_wpm']:<3}) "
            f"Rate: [{profile['min_rate']:+3d}%, {profile['max_rate']:+3d}%]"
        )
        print(f"    → {voice['characteristics']}")

    print("\n" + "=" * 80)
