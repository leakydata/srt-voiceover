"""
Synchronization quality metrics and detailed logging.

Tracks confidence scores, timing accuracy, and potential issues
for debugging and quality assessment.
"""

from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass, field
from datetime import datetime
import json


@dataclass
class SegmentQualityMetrics:
    """Metrics for a single segment."""

    segment_idx: int
    speaker: Optional[str]
    text: str
    confidence: float  # 0.0 to 1.0
    rate: int  # percentage
    prev_rate: Optional[int] = None
    rate_change: Optional[int] = None
    timing_strategy: str = "NONE"  # HIGH, MEDIUM, LOW, NONE
    word_match_count: int = 0
    total_words: int = 0
    has_issues: bool = False
    issues: List[str] = field(default_factory=list)

    def add_issue(self, issue_description: str):
        """Record an issue found with this segment."""
        self.issues.append(issue_description)
        self.has_issues = True

    def to_dict(self) -> Dict:
        """Convert to dictionary for JSON serialization."""
        return {
            'segment_idx': self.segment_idx,
            'speaker': self.speaker,
            'text': self.text[:100],  # Truncate for brevity
            'confidence': round(self.confidence, 3),
            'rate': self.rate,
            'rate_change': self.rate_change,
            'timing_strategy': self.timing_strategy,
            'word_match': f"{self.word_match_count}/{self.total_words}",
            'issues': self.issues
        }


class SyncQualityReport:
    """
    Comprehensive report on voiceover synchronization quality.

    Tracks metrics across all segments and identifies problematic areas.
    """

    def __init__(self, verbose: bool = False):
        self.verbose = verbose
        self.segments: List[SegmentQualityMetrics] = []
        self.total_segments = 0
        self.start_time = datetime.now()

    def add_segment(
        self,
        segment_idx: int,
        speaker: Optional[str],
        text: str,
        confidence: float,
        rate: int,
        prev_rate: Optional[int] = None,
        timing_strategy: str = "NONE",
        word_match_count: int = 0,
        total_words: int = 0
    ) -> SegmentQualityMetrics:
        """
        Add metrics for a segment.

        Args:
            segment_idx: Index of segment
            speaker: Speaker name or None
            text: Segment text
            confidence: Word matching confidence (0.0 to 1.0)
            rate: Speech rate adjustment percentage
            prev_rate: Previous segment's rate (for change calculation)
            timing_strategy: Quality strategy applied
            word_match_count: Number of successfully matched words
            total_words: Total words in segment

        Returns:
            SegmentQualityMetrics object
        """
        self.total_segments += 1

        # Calculate rate change
        rate_change = None
        if prev_rate is not None:
            rate_change = rate - prev_rate

        metrics = SegmentQualityMetrics(
            segment_idx=segment_idx,
            speaker=speaker,
            text=text,
            confidence=confidence,
            rate=rate,
            prev_rate=prev_rate,
            rate_change=rate_change,
            timing_strategy=timing_strategy,
            word_match_count=word_match_count,
            total_words=total_words
        )

        # Check for common issues
        self._check_for_issues(metrics)

        self.segments.append(metrics)
        return metrics

    def _check_for_issues(self, metrics: SegmentQualityMetrics):
        """Identify potential quality issues in a segment."""

        # Low confidence warning
        if metrics.confidence < 0.5:
            metrics.add_issue(f"Low word match confidence ({metrics.confidence:.1%})")

        # Extreme rate changes
        if metrics.rate_change is not None:
            if abs(metrics.rate_change) > 25:
                metrics.add_issue(
                    f"Large rate jump: {metrics.prev_rate:+d}% → {metrics.rate:+d}% (Δ{metrics.rate_change:+d}%)"
                )

        # Very high rate (may sound unnatural)
        if metrics.rate > 40:
            metrics.add_issue(f"High speech rate (+{metrics.rate}%) - may sound unnatural")

        # Very low rate (may sound slow)
        if metrics.rate < -40:
            metrics.add_issue(f"Low speech rate ({metrics.rate}%) - may sound slow")

        # No words matched
        if metrics.total_words > 0 and metrics.word_match_count == 0:
            metrics.add_issue("No words successfully matched to timing data")

        # Low word match ratio
        if metrics.total_words > 0:
            match_ratio = metrics.word_match_count / metrics.total_words
            if match_ratio < 0.5:
                metrics.add_issue(
                    f"Only {metrics.word_match_count}/{metrics.total_words} words matched ({match_ratio:.0%})"
                )

    def get_summary(self) -> Dict:
        """
        Get summary statistics for the entire report.

        Returns:
            Dictionary with summary metrics
        """
        if not self.segments:
            return {
                'total_segments': 0,
                'processing_time': 0
            }

        # Calculate statistics
        confidences = [s.confidence for s in self.segments if s.total_words > 0]
        rate_changes = [abs(s.rate_change) for s in self.segments if s.rate_change is not None]
        problem_segments = [s for s in self.segments if s.has_issues]

        avg_confidence = sum(confidences) / len(confidences) if confidences else 0.0
        max_rate_change = max(rate_changes) if rate_changes else 0
        avg_rate_change = sum(rate_changes) / len(rate_changes) if rate_changes else 0

        processing_time = (datetime.now() - self.start_time).total_seconds()

        return {
            'total_segments': self.total_segments,
            'avg_confidence': round(avg_confidence, 3),
            'confidence_level': self._confidence_to_level(avg_confidence),
            'segments_with_issues': len(problem_segments),
            'issue_percentage': round(100 * len(problem_segments) / self.total_segments, 1),
            'max_rate_change': max_rate_change,
            'avg_rate_change': round(avg_rate_change, 1),
            'processing_time_s': round(processing_time, 2)
        }

    def _confidence_to_level(self, confidence: float) -> str:
        """Convert confidence score to quality level."""
        if confidence > 0.9:
            return "EXCELLENT"
        elif confidence > 0.75:
            return "GOOD"
        elif confidence > 0.6:
            return "FAIR"
        else:
            return "POOR"

    def print_report(self, max_issues_shown: int = 5, show_all_segments: bool = False):
        """
        Print a formatted quality report.

        Args:
            max_issues_shown: Maximum number of issues to display
            show_all_segments: If True, show all segments; if False, show only problematic ones
        """
        summary = self.get_summary()

        print("\n" + "=" * 80)
        print("VOICEOVER SYNCHRONIZATION QUALITY REPORT")
        print("=" * 80)

        print(f"\nTotal Segments: {summary['total_segments']}")
        print(f"Average Confidence: {summary['avg_confidence']:.1%} ({summary['confidence_level']})")
        print(f"Segments with Issues: {summary['segments_with_issues']}/{summary['total_segments']} ({summary['issue_percentage']}%)")
        print(f"Max Rate Change: {summary['max_rate_change']}%")
        print(f"Avg Rate Change: {summary['avg_rate_change']}%")
        print(f"Processing Time: {summary['processing_time_s']}s")

        # Show problematic segments
        if self.segments:
            print(f"\n{'─' * 80}")

            if show_all_segments:
                segments_to_show = self.segments
                print(f"All Segments:")
            else:
                problem_segs = [s for s in self.segments if s.has_issues]
                segments_to_show = problem_segs[:max_issues_shown]
                print(f"Problematic Segments (top {min(max_issues_shown, len(problem_segs))}):")

            for seg in segments_to_show:
                print(f"\n[Segment {seg.segment_idx}] {seg.speaker or 'Unknown'}")
                print(f"  Text: {seg.text[:60]}{'...' if len(seg.text) > 60 else ''}")
                print(f"  Confidence: {seg.confidence:.1%} | Rate: {seg.rate:+d}%", end="")

                if seg.rate_change is not None:
                    print(f" | Change: {seg.rate_change:+d}%", end="")
                print()

                if seg.issues:
                    for issue in seg.issues:
                        print(f"  ⚠ {issue}")

        print("\n" + "=" * 80 + "\n")

    def export_json(self, filepath: str):
        """
        Export full report as JSON.

        Args:
            filepath: Path to save JSON file
        """
        report_data = {
            'summary': self.get_summary(),
            'segments': [s.to_dict() for s in self.segments],
            'timestamp': self.start_time.isoformat()
        }

        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(report_data, f, indent=2, ensure_ascii=False)

    def get_problematic_segments(self) -> List[SegmentQualityMetrics]:
        """
        Get segments that have quality issues.

        Returns:
            List of problematic segments
        """
        return [s for s in self.segments if s.has_issues]

    def get_confidence_histogram(self) -> Dict[str, int]:
        """
        Get histogram of confidence levels.

        Returns:
            Dictionary with confidence ranges and counts
        """
        buckets = {
            '0.0-0.2': 0,
            '0.2-0.4': 0,
            '0.4-0.6': 0,
            '0.6-0.8': 0,
            '0.8-1.0': 0
        }

        for seg in self.segments:
            if seg.confidence < 0.2:
                buckets['0.0-0.2'] += 1
            elif seg.confidence < 0.4:
                buckets['0.2-0.4'] += 1
            elif seg.confidence < 0.6:
                buckets['0.4-0.6'] += 1
            elif seg.confidence < 0.8:
                buckets['0.6-0.8'] += 1
            else:
                buckets['0.8-1.0'] += 1

        return buckets

    def get_statistics(self) -> Dict:
        """
        Get detailed statistics.

        Returns:
            Dictionary with various statistics
        """
        if not self.segments:
            return {}

        rates = [s.rate for s in self.segments]
        confidences = [s.confidence for s in self.segments if s.total_words > 0]

        return {
            'total_segments': len(self.segments),
            'avg_confidence': sum(confidences) / len(confidences) if confidences else 0,
            'min_confidence': min(confidences) if confidences else 0,
            'max_confidence': max(confidences) if confidences else 0,
            'avg_rate': sum(rates) / len(rates) if rates else 0,
            'min_rate': min(rates) if rates else 0,
            'max_rate': max(rates) if rates else 0,
            'issues_count': sum(1 for s in self.segments if s.has_issues),
            'total_issues': sum(len(s.issues) for s in self.segments)
        }
