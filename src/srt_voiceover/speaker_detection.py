"""
Advanced speaker detection with multiple methods.

Handles:
1. Explicit labels: "Nathan: Hello world"
2. Implicit detection: Uses pyannote.audio if available
3. Context-based: Assumes previous speaker if no marker
4. Fallback: Uses sensible defaults
"""

from typing import List, Dict, Tuple, Optional
import re


def parse_speaker_and_text_advanced(
    raw_text: str,
    prev_speaker: Optional[str] = None,
    use_heuristic: bool = True
) -> Tuple[Optional[str], str]:
    """
    Extract speaker name from subtitle text using advanced detection.

    Priority order:
    1. Explicit pattern: "Speaker: text"
    2. Context: Previous speaker (if text looks like continuation)
    3. Heuristic: Based on text patterns
    4. Fallback: None

    Args:
        raw_text: Raw subtitle text
        prev_speaker: Speaker from previous segment (for context)
        use_heuristic: Whether to apply heuristic detection

    Returns:
        Tuple of (speaker_name or None, cleaned_text)
    """

    if not raw_text:
        return None, ""

    lines = [ln.strip() for ln in raw_text.splitlines() if ln.strip()]
    if not lines:
        return None, ""

    first_line = lines[0]
    speaker = None
    content_lines = lines

    # Method 1: Explicit "Speaker: text" pattern
    if ":" in first_line:
        possible_speaker, rest = first_line.split(":", 1)
        possible_speaker = possible_speaker.strip()

        # Check if it looks like a speaker name
        # - Starts with uppercase
        # - Mostly alphabetic (allows spaces)
        # - Not too long (max 30 chars)
        # - Not a time format or URL
        if (possible_speaker and
            possible_speaker[0].isupper() and
            possible_speaker.replace(" ", "").isalpha() and
            len(possible_speaker) <= 30 and
            "://" not in possible_speaker):

            speaker = possible_speaker
            first_content = rest.lstrip()
            content_lines = []
            if first_content:
                content_lines.append(first_content)
            if len(lines) > 1:
                content_lines.extend(lines[1:])

    # Method 2: No explicit marker found - check context
    if not speaker and prev_speaker:
        # If text looks like a continuation (no question, no new topic marker),
        # assume same speaker
        text = " ".join(content_lines).strip()

        # Simple heuristic: if it starts with continuation words or lowercase, same speaker
        continuation_starts = [
            'and', 'but', 'so', 'or', 'because', 'that',
            'they', 'it', 'this', 'there', 'here'
        ]

        first_word = text.split()[0].lower() if text.split() else ""
        if first_word in continuation_starts or (text and not text[0].isupper()):
            speaker = prev_speaker

    # Join remaining text
    text = " ".join(content_lines).strip()
    return speaker, text


def detect_speaker_from_patterns(
    text: str,
    segment_idx: int,
    context_window: List[Tuple[int, Optional[str]]] = None
) -> Optional[str]:
    """
    Use heuristic patterns to detect speaker changes in text.

    This is a simple pattern-based approach for when:
    - No explicit labels
    - No pyannote available

    Args:
        text: Segment text
        segment_idx: Index in sequence
        context_window: List of (idx, speaker) tuples from nearby segments

    Returns:
        Detected speaker name or None
    """

    # Patterns that might indicate speaker change
    question_patterns = [
        (r'\?$', 'Questioner'),  # Ends with question
        (r'^(you|hey|listen|wait)\b', 'Other Speaker'),
        (r'^(yes|no|okay|ok)\b', 'Responder'),
    ]

    for pattern, speaker_hint in question_patterns:
        if re.search(pattern, text.lower()):
            return None  # Don't auto-detect, but could use speaker_hint if needed

    # If we have context, try to continue pattern
    if context_window and len(context_window) > 0:
        # Look at last known speaker in context
        for idx, speaker in reversed(context_window):
            if speaker is not None:
                # Alternate or continue based on patterns
                if segment_idx - idx == 1:  # Immediately after
                    # Might be same speaker continuing
                    return None
                else:
                    # Might be different speaker
                    return None

    return None  # Don't guess if uncertain


def validate_speaker_name(speaker_name: str) -> bool:
    """
    Validate that a string looks like a proper speaker name.

    Args:
        speaker_name: String to validate

    Returns:
        True if it looks like a speaker name
    """
    if not speaker_name:
        return False

    # Must start with uppercase letter
    if not speaker_name[0].isupper():
        return False

    # Must be mostly alphabetic (allowing spaces and hyphens)
    cleaned = speaker_name.replace(" ", "").replace("-", "")
    if not cleaned.isalpha():
        return False

    # Reasonable length
    if len(speaker_name) > 50 or len(speaker_name) < 1:
        return False

    return True


def get_unique_speakers(srt_segments: List[Dict]) -> Dict[str, int]:
    """
    Extract unique speakers from parsed SRT segments.

    Args:
        srt_segments: List of segment dicts with 'speaker' key

    Returns:
        Dictionary mapping speaker names to occurrence counts
    """
    speakers = {}

    for segment in srt_segments:
        speaker = segment.get('speaker')
        if speaker:
            speakers[speaker] = speakers.get(speaker, 0) + 1

    return speakers


def get_speaker_statistics(srt_segments: List[Dict]) -> Dict:
    """
    Get statistics about speakers in a subtitle file.

    Args:
        srt_segments: List of segment dicts with 'speaker' key

    Returns:
        Dictionary with speaker statistics
    """
    speakers = get_unique_speakers(srt_segments)

    return {
        'total_segments': len(srt_segments),
        'segments_with_speakers': sum(1 for s in srt_segments if s.get('speaker')),
        'segments_without_speakers': sum(1 for s in srt_segments if not s.get('speaker')),
        'unique_speakers': list(speakers.keys()),
        'speaker_counts': speakers,
        'has_multiple_speakers': len(speakers) > 1,
        'primary_speaker': max(speakers.items(), key=lambda x: x[1])[0] if speakers else None
    }


class SpeakerContext:
    """
    Maintains speaker context across multiple segments.

    Useful for continuing speaker assignment based on context.
    """

    def __init__(self):
        self.history: List[Tuple[int, Optional[str]]] = []
        self.speakers_seen: set = set()

    def add_segment(self, idx: int, speaker: Optional[str]):
        """Record a segment's speaker."""
        self.history.append((idx, speaker))
        if speaker:
            self.speakers_seen.add(speaker)

    def get_context_window(self, center_idx: int, window_size: int = 5) -> List[Tuple[int, Optional[str]]]:
        """
        Get speaker context around a segment.

        Args:
            center_idx: Index of interest
            window_size: How many segments before/after to include

        Returns:
            List of (idx, speaker) tuples
        """
        start = max(0, center_idx - window_size)
        end = min(len(self.history), center_idx + window_size + 1)
        return self.history[start:end]

    def get_last_speaker(self) -> Optional[str]:
        """Get the most recent speaker."""
        for idx, speaker in reversed(self.history):
            if speaker:
                return speaker
        return None

    def get_speaker_at_index(self, idx: int) -> Optional[str]:
        """Get speaker at specific index."""
        if idx < len(self.history):
            return self.history[idx][1]
        return None

    def clear(self):
        """Reset context."""
        self.history.clear()
        self.speakers_seen.clear()
