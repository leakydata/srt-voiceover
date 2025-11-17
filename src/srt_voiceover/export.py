"""
Multi-format export for word-level timing data.

Enables integration with video editors, web players, and other tools.
"""

from typing import List, Dict, Optional
from pathlib import Path
import json


def seconds_to_vtt_time(seconds: float) -> str:
    """
    Convert seconds to WebVTT time format (HH:MM:SS.mmm).

    Args:
        seconds: Time in seconds

    Returns:
        VTT format string
    """
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    millis = int((seconds % 1) * 1000)

    return f"{hours:02d}:{minutes:02d}:{secs:02d}.{millis:03d}"


def seconds_to_srt_time(seconds: float) -> str:
    """
    Convert seconds to SRT time format (HH:MM:SS,mmm).

    Args:
        seconds: Time in seconds

    Returns:
        SRT format string
    """
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    millis = int((seconds % 1) * 1000)

    return f"{hours:02d}:{minutes:02d}:{secs:02d},{millis:03d}"


def export_word_timings_vtt(
    word_timings: List[Dict],
    output_path: str,
    verbose: bool = True
) -> str:
    """
    Export word timings in WebVTT format (for web players, video.js, etc.).

    Args:
        word_timings: List of word timing dicts with 'word', 'start', 'end'
        output_path: Path to save VTT file
        verbose: Print status messages

    Returns:
        Path to created file
    """
    output_path = str(output_path)

    if verbose:
        print(f"Exporting {len(word_timings)} words to WebVTT format...")

    with open(output_path, 'w', encoding='utf-8') as f:
        f.write("WEBVTT\n\n")

        for word in word_timings:
            word_text = word.get('word', '').strip()
            start = word.get('start', 0.0)
            end = word.get('end', start)

            if word_text:
                start_vtt = seconds_to_vtt_time(start)
                end_vtt = seconds_to_vtt_time(end)
                f.write(f"{start_vtt} --> {end_vtt}\n")
                f.write(f"{word_text}\n\n")

    if verbose:
        print(f"[OK] WebVTT exported to: {output_path}")

    return output_path


def export_word_timings_srt(
    word_timings: List[Dict],
    output_path: str,
    verbose: bool = True
) -> str:
    """
    Export word timings in SubRip (SRT) format.

    Useful for manual synchronization in subtitle editors.

    Args:
        word_timings: List of word timing dicts
        output_path: Path to save SRT file
        verbose: Print status messages

    Returns:
        Path to created file
    """
    output_path = str(output_path)

    if verbose:
        print(f"Exporting {len(word_timings)} words to SRT format...")

    with open(output_path, 'w', encoding='utf-8') as f:
        for i, word in enumerate(word_timings, 1):
            word_text = word.get('word', '').strip()
            start = word.get('start', 0.0)
            end = word.get('end', start)

            if word_text:
                start_srt = seconds_to_srt_time(start)
                end_srt = seconds_to_srt_time(end)

                f.write(f"{i}\n")
                f.write(f"{start_srt} --> {end_srt}\n")
                f.write(f"{word_text}\n\n")

    if verbose:
        print(f"[OK] SRT exported to: {output_path}")

    return output_path


def export_word_timings_json(
    word_timings: List[Dict],
    output_path: str,
    verbose: bool = True
) -> str:
    """
    Export word timings in JSON format (standard machine-readable format).

    Args:
        word_timings: List of word timing dicts
        output_path: Path to save JSON file
        verbose: Print status messages

    Returns:
        Path to created file
    """
    output_path = str(output_path)

    if verbose:
        print(f"Exporting {len(word_timings)} words to JSON format...")

    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(word_timings, f, indent=2, ensure_ascii=False)

    if verbose:
        print(f"[OK] JSON exported to: {output_path}")

    return output_path


def export_word_timings_csv(
    word_timings: List[Dict],
    output_path: str,
    verbose: bool = True
) -> str:
    """
    Export word timings in CSV format (for spreadsheets, analysis tools).

    Args:
        word_timings: List of word timing dicts
        output_path: Path to save CSV file
        verbose: Print status messages

    Returns:
        Path to created file
    """
    output_path = str(output_path)

    if verbose:
        print(f"Exporting {len(word_timings)} words to CSV format...")

    try:
        import csv
    except ImportError:
        raise ImportError("csv module required for CSV export")

    with open(output_path, 'w', encoding='utf-8', newline='') as f:
        writer = csv.writer(f)

        # Write header
        writer.writerow(['word_number', 'word', 'start_seconds', 'end_seconds', 'duration_seconds'])

        # Write data
        for i, word in enumerate(word_timings, 1):
            word_text = word.get('word', '').strip()
            start = word.get('start', 0.0)
            end = word.get('end', start)
            duration = end - start

            writer.writerow([i, word_text, f"{start:.3f}", f"{end:.3f}", f"{duration:.3f}"])

    if verbose:
        print(f"[OK] CSV exported to: {output_path}")

    return output_path


def export_word_timings_fcpxml(
    word_timings: List[Dict],
    output_path: str,
    fps: float = 29.97,
    verbose: bool = True
) -> str:
    """
    Export word timings in Final Cut Pro XML format.

    Enables direct import into Final Cut Pro for video editing synchronization.

    Args:
        word_timings: List of word timing dicts
        output_path: Path to save FCPXML file
        fps: Frames per second (default 29.97 NTSC)
        verbose: Print status messages

    Returns:
        Path to created file
    """
    output_path = str(output_path)

    if verbose:
        print(f"Exporting {len(word_timings)} words to Final Cut Pro XML format...")

    # Helper function to convert seconds to FCP timecode
    def seconds_to_fcpxml_time(seconds: float, fps: float = 29.97) -> str:
        """Convert seconds to FCP format (frames)."""
        total_frames = int(seconds * fps)
        hours = total_frames // (int(fps) * 3600)
        remaining = total_frames % (int(fps) * 3600)
        minutes = remaining // (int(fps) * 60)
        remaining = remaining % (int(fps) * 60)
        seconds_part = remaining // int(fps)
        frames = remaining % int(fps)

        return f"{hours:02d}:{minutes:02d}:{seconds_part:02d}:{frames:02d}"

    # Build FCPXML
    xml_lines = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        '<fcpxml version="1.9">',
        f'  <project name="Word Timings Export">',
        f'    <sequence duration="{int(word_timings[-1]["end"] * 30000) if word_timings else 0}">',
        f'      <spine>',
    ]

    for i, word in enumerate(word_timings):
        word_text = word.get('word', '').strip()
        start = word.get('start', 0.0)
        end = word.get('end', start)
        duration = end - start

        if word_text:
            # Create a title clip for each word
            start_tc = seconds_to_fcpxml_time(start, fps)
            end_tc = seconds_to_fcpxml_time(end, fps)
            duration_frames = int(duration * fps)

            xml_lines.append(
                f'        <title name="Word {i+1}: {word_text}" duration="{duration_frames}">'
            )
            xml_lines.append(
                f'          <text>Word {i+1}: {word_text}</text>'
            )
            xml_lines.append(f'        </title>')

    xml_lines.extend([
        f'      </spine>',
        f'    </sequence>',
        f'  </project>',
        '</fcpxml>'
    ])

    with open(output_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(xml_lines))

    if verbose:
        print(f"[OK] Final Cut Pro XML exported to: {output_path}")

    return output_path


def export_word_timings_multi(
    word_timings: List[Dict],
    output_base_path: str,
    formats: List[str] = None,
    verbose: bool = True
) -> Dict[str, str]:
    """
    Export word timings in multiple formats simultaneously.

    Args:
        word_timings: List of word timing dicts
        output_base_path: Base path for output (without extension)
        formats: List of formats to export (default: all)
                 Options: 'vtt', 'srt', 'json', 'csv', 'fcpxml'
        verbose: Print status messages

    Returns:
        Dictionary mapping format names to file paths
    """
    if formats is None:
        formats = ['json', 'vtt', 'srt', 'csv']

    results = {}
    output_base_path = str(output_base_path)

    # Remove extension if present
    if '.' in Path(output_base_path).name:
        output_base_path = str(Path(output_base_path).with_suffix(''))

    if 'vtt' in formats:
        try:
            path = export_word_timings_vtt(
                word_timings,
                f"{output_base_path}.vtt",
                verbose=verbose
            )
            results['vtt'] = path
        except Exception as e:
            if verbose:
                print(f"[ERROR] VTT export failed: {e}")

    if 'srt' in formats:
        try:
            path = export_word_timings_srt(
                word_timings,
                f"{output_base_path}.srt",
                verbose=verbose
            )
            results['srt'] = path
        except Exception as e:
            if verbose:
                print(f"[ERROR] SRT export failed: {e}")

    if 'json' in formats:
        try:
            path = export_word_timings_json(
                word_timings,
                f"{output_base_path}.json",
                verbose=verbose
            )
            results['json'] = path
        except Exception as e:
            if verbose:
                print(f"[ERROR] JSON export failed: {e}")

    if 'csv' in formats:
        try:
            path = export_word_timings_csv(
                word_timings,
                f"{output_base_path}.csv",
                verbose=verbose
            )
            results['csv'] = path
        except Exception as e:
            if verbose:
                print(f"[ERROR] CSV export failed: {e}")

    if 'fcpxml' in formats:
        try:
            path = export_word_timings_fcpxml(
                word_timings,
                f"{output_base_path}.fcpxml",
                verbose=verbose
            )
            results['fcpxml'] = path
        except Exception as e:
            if verbose:
                print(f"[ERROR] FCPXML export failed: {e}")

    return results
