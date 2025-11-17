"""
Translation module using Ollama for multi-language support.

Handles SRT translation while preserving:
- Speaker labels
- Timestamps
- Formatting
"""

import json
import requests
import logging
from typing import Optional, Dict, List, Tuple
from pathlib import Path
import pysrt

# Set up logging
logger = logging.getLogger(__name__)


# Default Ollama configuration
OLLAMA_DEFAULT_BASE_URL = "http://localhost:11434"
OLLAMA_TIMEOUT = 300  # seconds
OLLAMA_DEFAULT_MODEL = "gpt-oss:20b"  # New high-quality model (July 2025)

# Language code mappings
LANGUAGE_NAMES = {
    "es": "Spanish",
    "fr": "French",
    "de": "German",
    "it": "Italian",
    "pt": "Portuguese",
    "ru": "Russian",
    "ja": "Japanese",
    "zh": "Chinese",
    "ko": "Korean",
    "ar": "Arabic",
    "hi": "Hindi",
    "nl": "Dutch",
    "pl": "Polish",
    "tr": "Turkish",
    "th": "Thai",
    "vi": "Vietnamese",
}

# Recommended models by language
RECOMMENDED_MODELS = {
    "fast": ["mistral", "neural-chat", "tinyllama"],
    "balanced": ["llama2", "openhermes2.5", "dolphin-mixtral"],
    "quality": ["neural-chat", "openhermes2.5", "dolphin-mixtral"],
}


class OllamaConnectionError(Exception):
    """Raised when Ollama connection fails."""
    pass


class OllamaConfig:
    """Configuration for Ollama translation."""

    def __init__(
        self,
        base_url: str = OLLAMA_DEFAULT_BASE_URL,
        model: str = OLLAMA_DEFAULT_MODEL,
        timeout: int = OLLAMA_TIMEOUT,
    ):
        """
        Initialize Ollama configuration.

        Args:
            base_url: Ollama API base URL (default: http://localhost:11434)
            model: Model to use (default: mistral)
            timeout: Request timeout in seconds
        """
        self.base_url = base_url.rstrip("/")  # Remove trailing slash
        self.model = model
        self.timeout = timeout

    def validate(self, verbose: bool = True) -> bool:
        """
        Check if Ollama is accessible.

        Args:
            verbose: Print status messages

        Returns:
            True if Ollama is accessible, False otherwise
        """
        try:
            if verbose:
                print(f"[Validating] Connecting to Ollama at {self.base_url}...")
            logger.debug(f"Validating Ollama connection at {self.base_url}")

            response = requests.get(
                f"{self.base_url}/api/tags",
                timeout=10,
            )
            response.raise_for_status()
            logger.debug(f"Successfully connected to Ollama")

            if verbose:
                print(f"[OK] Ollama connected at {self.base_url}")
                print(f"[OK] Using model: {self.model}")
            logger.info(f"Ollama connection successful - will use model '{self.model}'")

            return True

        except requests.ConnectionError as e:
            if verbose:
                print(f"[ERROR] Cannot connect to Ollama at {self.base_url}")
                print(f"        Make sure Ollama is running or check the base URL")
            logger.error(f"Connection error: {e}")
            return False
        except Exception as e:
            if verbose:
                print(f"[ERROR] Failed to validate Ollama: {e}")
            logger.error(f"Validation failed: {e}")
            return False


def translate_text(
    text: str,
    target_language: str,
    config: OllamaConfig,
    verbose: bool = False,
) -> str:
    """
    Translate text using Ollama.

    Args:
        text: Text to translate
        target_language: Target language code (e.g., 'es' for Spanish)
        config: OllamaConfig instance
        verbose: Print progress messages

    Returns:
        Translated text

    Raises:
        OllamaConnectionError: If Ollama is not accessible
    """
    language_name = LANGUAGE_NAMES.get(target_language, target_language)

    # Create translation prompt
    prompt = f"""You are a professional translator. Translate this text to {language_name}.
Return ONLY the translated text. Do not add any explanations, notes, or commentary.
Do not translate technical terms like proper nouns.

Text to translate: {text}

Translated text:"""

    try:
        if verbose:
            print(f"  Translating to {language_name}...", end=" ", flush=True)

        logger.debug(f"Translating text to {language_name}")
        logger.debug(f"Sending request to {config.base_url}/api/generate with model={config.model}")

        response = requests.post(
            f"{config.base_url}/api/generate",
            json={
                "model": config.model,
                "prompt": prompt,
                "stream": False,
                "temperature": 0.3,  # Lower temp for more consistent translations
            },
            timeout=config.timeout,
        )

        response.raise_for_status()
        logger.debug(f"Received response from Ollama: status={response.status_code}")

        data = response.json()
        logger.debug(f"Ollama response: {data.get('response', '')[:100]}...")

        translated = data.get("response", "").strip()

        if verbose:
            print("[OK]")

        logger.debug(f"Translation complete: {translated[:50]}...")

        return translated

    except requests.ConnectionError as e:
        logger.error(f"Connection error during translation: {e}")
        raise OllamaConnectionError(
            f"Cannot connect to Ollama at {config.base_url}: {e}"
        )
    except requests.Timeout:
        raise OllamaConnectionError(
            f"Ollama request timed out after {config.timeout} seconds"
        )
    except Exception as e:
        raise OllamaConnectionError(f"Translation failed: {e}")


def translate_srt_segment(
    segment: pysrt.SubRipItem,
    target_language: str,
    config: OllamaConfig,
    verbose: bool = False,
) -> pysrt.SubRipItem:
    """
    Translate a single SRT segment while preserving structure.

    Preserves:
    - Timestamps
    - Speaker labels (e.g., "Nathan:")
    - Formatting

    Args:
        segment: pysrt.SubRipItem to translate
        target_language: Target language code
        config: OllamaConfig instance
        verbose: Print progress

    Returns:
        New segment with translated text

    Raises:
        OllamaConnectionError: If translation fails
    """
    from .speaker_detection import parse_speaker_and_text_advanced

    raw_text = segment.text.strip()

    # Extract speaker and text
    speaker, text = parse_speaker_and_text_advanced(raw_text)

    if not text:
        # Empty segment, return as-is
        return segment

    # Translate the text
    translated_text = translate_text(text, target_language, config, verbose=verbose)

    # Reconstruct with speaker label if present
    if speaker:
        translated_full = f"{speaker}: {translated_text}"
    else:
        translated_full = translated_text

    # Create new segment with translated text, same timing
    new_segment = pysrt.SubRipItem(
        index=segment.index,
        start=segment.start,
        end=segment.end,
        text=translated_full,
    )

    return new_segment


def translate_srt(
    srt_path: str,
    target_language: str,
    config: OllamaConfig,
    output_path: Optional[str] = None,
    verbose: bool = True,
) -> str:
    """
    Translate an entire SRT file using Ollama.

    Preserves all timing and speaker labels.

    Args:
        srt_path: Path to input SRT file
        target_language: Target language code (e.g., 'es' for Spanish)
        config: OllamaConfig instance
        output_path: Path to save translated SRT (optional)
        verbose: Print progress messages

    Returns:
        Path to translated SRT file

    Raises:
        OllamaConnectionError: If Ollama is not accessible
        FileNotFoundError: If input SRT not found
    """
    # Load original SRT
    srt_file = Path(srt_path)
    if not srt_file.exists():
        raise FileNotFoundError(f"SRT file not found: {srt_path}")

    logger.info(f"Starting SRT translation from {srt_path}")
    logger.debug(f"Target language: {target_language}, Ollama: {config.base_url}, Model: {config.model}")

    if verbose:
        print(f"\nTranslating SRT to {LANGUAGE_NAMES.get(target_language, target_language)}...")

    subs = pysrt.open(srt_path, encoding="utf-8")
    logger.info(f"Loaded SRT file with {len(subs)} segments")

    # Translate each segment
    translated_subs = pysrt.SubRipFile()

    for i, segment in enumerate(subs, 1):
        if verbose:
            print(f"  [{i}/{len(subs)}]", end=" ")
        logger.debug(f"Translating segment {i}/{len(subs)}: {segment.text[:50]}...")

        translated_segment = translate_srt_segment(
            segment, target_language, config, verbose=verbose
        )
        translated_subs.append(translated_segment)

    # Determine output path
    if output_path is None:
        # Generate output filename
        language_name = LANGUAGE_NAMES.get(target_language, target_language).lower()
        output_path = str(
            srt_file.parent / f"{srt_file.stem}_{language_name}.srt"
        )

    # Save translated SRT
    translated_subs.save(output_path, encoding="utf-8")
    logger.info(f"Translated SRT saved to {output_path}")

    if verbose:
        print(f"\n[OK] Translated SRT saved: {output_path}")

    return output_path


def get_available_ollama_models(
    config: OllamaConfig,
    verbose: bool = False,
) -> List[str]:
    """
    Get list of available Ollama models.

    Args:
        config: OllamaConfig instance
        verbose: Print status messages

    Returns:
        List of available model names

    Raises:
        OllamaConnectionError: If Ollama is not accessible
    """
    try:
        response = requests.get(
            f"{config.base_url}/api/tags",
            timeout=10,
        )
        response.raise_for_status()

        data = response.json()
        models = [m["name"] for m in data.get("models", [])]

        if verbose:
            print(f"Available Ollama models ({len(models)}):")
            for model in models:
                print(f"  - {model}")

        return models

    except requests.ConnectionError as e:
        raise OllamaConnectionError(
            f"Cannot connect to Ollama at {config.base_url}: {e}"
        )
    except Exception as e:
        raise OllamaConnectionError(f"Failed to get models: {e}")


def create_translation_prompt_examples() -> Dict[str, str]:
    """
    Create example prompts for different languages.

    Useful for understanding translation quality expectations.

    Returns:
        Dictionary of language -> example prompt
    """
    return {
        "es": "Translate the following text to Spanish. Provide ONLY the translation.",
        "fr": "Translate the following text to French. Provide ONLY the translation.",
        "de": "Translate the following text to German. Provide ONLY the translation.",
        "it": "Translate the following text to Italian. Provide ONLY the translation.",
        "pt": "Translate the following text to Portuguese. Provide ONLY the translation.",
        "ru": "Translate the following text to Russian. Provide ONLY the translation.",
        "ja": "翻訳してください (Translate the following text to Japanese. Provide ONLY the translation.)",
        "zh": "翻译以下文本为中文。仅提供翻译。 (Translate to Simplified Chinese. Provide ONLY the translation.)",
        "ko": "다음 텍스트를 한국어로 번역하세요. (Translate to Korean. Provide ONLY the translation.)",
    }
