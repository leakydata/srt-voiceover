"""
Advanced word-level timing alignment with fuzzy matching and confidence scoring.

Handles both explicit speaker labels (e.g., "Nathan: text") and
implicit speaker detection from word timing data.
"""

from difflib import SequenceMatcher
from typing import List, Dict, Tuple, Optional
import re


def fuzzy_match_word(
    segment_word: str,
    candidate_words: List[Dict],
    threshold: float = 0.7
) -> Tuple[Optional[Dict], float]:
    """
    Find best matching word from candidates using fuzzy matching.

    Args:
        segment_word: Word to match (from SRT text)
        candidate_words: List of word timing dicts with 'word', 'start', 'end'
        threshold: Minimum similarity score (0.0 to 1.0)

    Returns:
        Tuple of (matched_word_dict or None, similarity_score)
    """
    best_match = None
    best_score = 0.0

    segment_word_lower = segment_word.lower().strip()

    for word in candidate_words:
        candidate_word = word.get('word', '').lower().strip()

        if not candidate_word:
            continue

        # Calculate similarity using SequenceMatcher
        similarity = SequenceMatcher(
            None,
            segment_word_lower,
            candidate_word
        ).ratio()

        if similarity > best_score:
            best_score = similarity
            best_match = word

    # Return match only if above threshold
    if best_score >= threshold:
        return best_match, best_score

    return None, best_score


def match_words_to_segment(
    segment_text: str,
    word_timings: List[Dict],
    segment_start_s: float,
    segment_end_s: float,
    fuzzy_threshold: float = 0.7,
    verbose: bool = False
) -> Tuple[List[Dict], float, List[str]]:
    """
    Match word timings to segment text using fuzzy matching.

    Handles variations like:
    - "it's" vs "its"
    - "don't" vs "dont"
    - Extra punctuation
    - Minor transcription errors

    Args:
        segment_text: Text from SRT segment
        word_timings: List of word timing dicts from transcription
        segment_start_s: Segment start time in seconds
        segment_end_s: Segment end time in seconds
        fuzzy_threshold: Minimum fuzzy match score (0.7 = 70% similar)
        verbose: Print debugging information

    Returns:
        Tuple of:
        - matched_words: List of successfully matched word timing dicts
        - overall_confidence: Confidence score (0.0 to 1.0)
        - unmatched_words: List of words that couldn't be matched
    """

    # Find words in time range
    candidate_words = [
        w for w in word_timings
        if segment_start_s <= w.get('start', 0) <= segment_end_s
    ]

    if not candidate_words:
        if verbose:
            print(f"  [WARN] No words found in time range [{segment_start_s:.2f}s - {segment_end_s:.2f}s]")
        return [], 0.0, []

    # Split segment text into words, preserving some structure
    # Remove punctuation but keep contractions
    text_words = _split_text_into_words(segment_text)

    if not text_words:
        return [], 0.0, []

    # Match words
    matched_words = []
    unmatched_words = []
    match_scores = []
    used_indices = set()

    for text_word in text_words:
        # Find unused candidates
        available_candidates = [
            (i, w) for i, w in enumerate(candidate_words)
            if i not in used_indices
        ]

        if not available_candidates:
            unmatched_words.append(text_word)
            continue

        # Extract just the word dicts for matching
        candidate_dicts = [w for _, w in available_candidates]

        # Find best match
        best_match, score = fuzzy_match_word(
            text_word,
            candidate_dicts,
            threshold=fuzzy_threshold
        )

        if best_match:
            matched_words.append(best_match)
            match_scores.append(score)

            # Mark this candidate as used
            for i, (idx, w) in enumerate(available_candidates):
                if w == best_match:
                    used_indices.add(idx)
                    break
        else:
            unmatched_words.append(text_word)

    # Calculate overall confidence
    total_words = len(text_words)
    matched_count = len(matched_words)

    if total_words > 0:
        # Confidence is: (matched words / total words) * (average match score)
        avg_match_score = sum(match_scores) / len(match_scores) if match_scores else 0.0
        overall_confidence = (matched_count / total_words) * avg_match_score
    else:
        overall_confidence = 0.0

    if verbose:
        print(f"  [MATCH] Matched {matched_count}/{total_words} words (confidence: {overall_confidence:.1%})")
        if unmatched_words:
            print(f"  [WARN] Unmatched: {', '.join(unmatched_words[:3])}")

    return matched_words, overall_confidence, unmatched_words


def _split_text_into_words(text: str) -> List[str]:
    """
    Split text into words, handling contractions and punctuation.

    Examples:
        "Don't do it!" -> ["Don't", "do", "it"]
        "It's a test (example)" -> ["It's", "a", "test", "example"]

    Args:
        text: Text to split

    Returns:
        List of words
    """
    if not text:
        return []

    # Remove parenthetical asides and brackets
    text = re.sub(r'\([^)]*\)', '', text)
    text = re.sub(r'\[[^\]]*\]', '', text)

    # Split on whitespace and common punctuation (but keep contractions)
    # This regex splits on whitespace and punctuation except apostrophes
    words = re.findall(r"[a-zA-Z']+", text)

    return [w for w in words if w]  # Filter empty


def get_timing_strategy(confidence: float) -> Dict:
    """
    Recommend synchronization strategy based on word matching confidence.

    Args:
        confidence: Confidence score from match_words_to_segment (0.0 to 1.0)

    Returns:
        Dictionary with strategy recommendations
    """
    if confidence > 0.9:
        # Excellent match - aggressive timing
        return {
            'level': 'HIGH',
            'use_word_timing': True,
            'elastic_timing': True,
            'rate_smoothing': True,
            'max_rate_change': 10,
            'enable_time_stretch': True,
            'description': 'High confidence - using aggressive timing optimization'
        }
    elif confidence > 0.7:
        # Good match - moderate timing
        return {
            'level': 'MEDIUM',
            'use_word_timing': True,
            'elastic_timing': True,
            'rate_smoothing': True,
            'max_rate_change': 15,
            'enable_time_stretch': False,
            'description': 'Medium confidence - using conservative timing'
        }
    elif confidence > 0.5:
        # Partial match - very conservative
        return {
            'level': 'LOW',
            'use_word_timing': False,
            'elastic_timing': False,
            'rate_smoothing': True,
            'max_rate_change': 20,
            'enable_time_stretch': False,
            'description': 'Low confidence - minimal dynamic adjustment'
        }
    else:
        # Poor match - no dynamic timing
        return {
            'level': 'NONE',
            'use_word_timing': False,
            'elastic_timing': False,
            'rate_smoothing': True,
            'max_rate_change': 30,
            'enable_time_stretch': False,
            'description': 'No confidence - using static timing only'
        }
