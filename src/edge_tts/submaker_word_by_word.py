"""SubMaker module is used to generate subtitles from WordBoundary events."""

from typing import List, Dict, Tuple, Set, Optional
import re

import srt  # type: ignore

from .typing import TTSChunk


class SubMaker:
    """
    SubMaker is used to generate subtitles from WordBoundary messages.
    Ensures that all characters from the original text are preserved in the output SRT.
    """

    def __init__(self) -> None:
        self.cues: List[srt.Subtitle] = []  # type: ignore
        self.original_text = ""
        self.words_with_timing: List[Tuple[str, int, int]] = []  # (word, offset, duration)
        self.current_position = 0
        
    def set_original_text(self, text: str) -> None:
        """
        Set the original text.

        Args:
            text (str): The original input text

        Returns:
            None
        """
        self.original_text = text
        self.words_with_timing = []
        self.cues = []

    def feed(self, msg: TTSChunk) -> None:
        """
        Feed a WordBoundary message to the SubMaker object.

        Args:
            msg (dict): The WordBoundary message.

        Returns:
            None
        """
        if msg["type"] != "WordBoundary":
            raise ValueError("Invalid message type, expected 'WordBoundary'")
        
        # Store word and timing information
        self.words_with_timing.append((
            msg["text"],
            msg["offset"],
            msg["duration"]
        ))

    def _create_exact_subtitles(self) -> None:
        """
        Create subtitles that preserve all characters in their exact positions.
        """
        if not self.original_text or not self.words_with_timing:
            return

        # Create a map to track which parts of the original text have been assigned
        text_length = len(self.original_text)
        assigned_positions = [False] * text_length
        
        # Track positions that have been matched in the original text
        word_matches: List[Tuple[int, int, int, int]] = []  # (start_pos, end_pos, offset, duration)
        
        # First, locate all words in the original text
        current_pos = 0
        for word, offset, duration in self.words_with_timing:
            # Search for the word in the original text
            search_pos = current_pos
            while search_pos < text_length:
                # Find the word with case-insensitive search
                word_match = re.search(r'\b' + re.escape(word) + r'\b', 
                                      self.original_text[search_pos:], 
                                      re.IGNORECASE)
                
                if not word_match:
                    # Try without word boundaries for words with punctuation
                    word_match = re.search(re.escape(word), 
                                          self.original_text[search_pos:], 
                                          re.IGNORECASE)
                
                if not word_match:
                    # If still not found, try fuzzy matching with just the alphanumeric part
                    clean_word = ''.join(c for c in word if c.isalnum())
                    if clean_word:
                        word_match = re.search(r'\b' + re.escape(clean_word) + r'\b', 
                                              self.original_text[search_pos:], 
                                              re.IGNORECASE)
                
                if word_match:
                    abs_start = search_pos + word_match.start()
                    abs_end = search_pos + word_match.end()
                    
                    # Check if this position has already been assigned
                    if not any(assigned_positions[abs_start:abs_end]):
                        word_matches.append((abs_start, abs_end, offset, duration))
                        # Mark these positions as assigned
                        for i in range(abs_start, abs_end):
                            assigned_positions[i] = True
                        
                        # Update search position for next word
                        current_pos = abs_end
                        break
                    else:
                        # Position already assigned, try further in the text
                        search_pos = abs_end
                else:
                    # Word not found from current position, try from beginning
                    if search_pos == current_pos:
                        # If we haven't found it starting from current_pos, don't get stuck in a loop
                        break
                    search_pos = 0
            
            # If we've matched all words, no need to continue
            if all(assigned_positions):
                break
        
        # Sort matches by their position in the original text
        word_matches.sort(key=lambda x: x[0])
        
        # Assign unmatched positions (punctuation, etc.) to their surrounding words
        for i in range(text_length):
            if not assigned_positions[i]:
                # Find closest matched word positions
                closest_before = None
                closest_after = None
                
                for start, end, offset, duration in word_matches:
                    if end <= i:
                        # This match is before the current position
                        if closest_before is None or end > closest_before[1]:
                            closest_before = (start, end, offset, duration)
                    if start > i:
                        # This match is after the current position
                        if closest_after is None or start < closest_after[0]:
                            closest_after = (start, end, offset, duration)
                
                # Assign to closest word (preferring the word before)
                if closest_before:
                    # Extend the end position of the closest word before
                    idx = word_matches.index(closest_before)
                    word_matches[idx] = (
                        closest_before[0], 
                        i + 1,  # Extend to include this position
                        closest_before[2], 
                        closest_before[3]
                    )
                    assigned_positions[i] = True
                elif closest_after:
                    # Extend the start position of the closest word after
                    idx = word_matches.index(closest_after)
                    word_matches[idx] = (
                        i,  # Extend to include this position
                        closest_after[1], 
                        closest_after[2], 
                        closest_after[3]
                    )
                    assigned_positions[i] = True
        
        # Merge adjacent matches with the same timing
        merged_matches = []
        current_match = None
        
        for start, end, offset, duration in sorted(word_matches, key=lambda x: x[0]):
            if current_match is None:
                current_match = (start, end, offset, duration)
            elif current_match[2] == offset and current_match[3] == duration and current_match[1] == start:
                # Merge with current match (same timing and adjacent)
                current_match = (current_match[0], end, offset, duration)
            else:
                # Different timing or not adjacent, save current match and start new one
                merged_matches.append(current_match)
                current_match = (start, end, offset, duration)
        
        # Add the last match if there is one
        if current_match:
            merged_matches.append(current_match)
        
        # Create cues from merged matches
        for start, end, offset, duration in merged_matches:
            text_segment = self.original_text[start:end]
            if text_segment.strip():
                self.cues.append(
                    srt.Subtitle(
                        index=len(self.cues) + 1,
                        start=srt.timedelta(microseconds=offset / 10),
                        end=srt.timedelta(microseconds=(offset + duration) / 10),
                        content=text_segment,
                    )
                )
        
        # Check for any text that hasn't been assigned (typically at the end)
        if not all(assigned_positions):
            # Find the last unassigned character
            last_unassigned = max([i for i, assigned in enumerate(assigned_positions) if not assigned])
            
            # Create a cue for the remaining text
            if last_unassigned < text_length - 1:  # If not the very last character
                remaining_text = self.original_text[last_unassigned:]
                
                if remaining_text.strip():
                    # Use timing from the last word with timing
                    if self.words_with_timing:
                        last_word, last_offset, last_duration = self.words_with_timing[-1]
                        end_time = last_offset + last_duration
                    else:
                        # Default timing if no words with timing
                        end_time = 5000000  # 5 seconds
                    
                    self.cues.append(
                        srt.Subtitle(
                            index=len(self.cues) + 1,
                            start=srt.timedelta(microseconds=end_time / 10),
                            end=srt.timedelta(microseconds=(end_time + 2000000) / 10),  # Add 2 seconds
                            content=remaining_text,
                        )
                    )

    def _ensure_cues_in_order(self) -> None:
        """Ensure cues are in order and don't overlap in time."""
        if not self.cues:
            return
        
        # Sort cues by start time
        self.cues.sort(key=lambda cue: cue.start.total_seconds())
        
        # Fix any overlaps and ensure minimal duration
        for i in range(1, len(self.cues)):
            prev_cue = self.cues[i-1]
            curr_cue = self.cues[i]
            
            # Ensure minimal duration (at least 0.1 seconds)
            min_duration = 0.1
            if (prev_cue.end.total_seconds() - prev_cue.start.total_seconds()) < min_duration:
                self.cues[i-1] = srt.Subtitle(
                    index=prev_cue.index,
                    start=prev_cue.start,
                    end=srt.timedelta(seconds=prev_cue.start.total_seconds() + min_duration),
                    content=prev_cue.content,
                )
            
            # Fix overlap
            if self.cues[i-1].end > curr_cue.start:
                self.cues[i-1] = srt.Subtitle(
                    index=prev_cue.index,
                    start=prev_cue.start,
                    end=curr_cue.start,
                    content=prev_cue.content,
                )
        
        # Renumber cues
        for i, cue in enumerate(self.cues):
            self.cues[i] = srt.Subtitle(
                index=i+1,
                start=cue.start,
                end=cue.end,
                content=cue.content,
            )
    
    def merge_cues(self, words: int) -> None:
        """
        Merge cues to reduce the number of cues.

        Args:
            words (int): The number of words to merge.

        Returns:
            None
        """
        if words <= 0:
            raise ValueError("Invalid number of words to merge, expected > 0")

        if len(self.cues) == 0:
            return

        new_cues: List[srt.Subtitle] = []  # type: ignore
        current_cue: srt.Subtitle = self.cues[0]  # type: ignore
        for cue in self.cues[1:]:
            if len(current_cue.content.split()) < words:
                current_cue = srt.Subtitle(
                    index=current_cue.index,
                    start=current_cue.start,
                    end=cue.end,
                    content=current_cue.content + " " + cue.content,
                )
            else:
                new_cues.append(current_cue)
                current_cue = cue
        new_cues.append(current_cue)
        self.cues = new_cues

    def get_srt(self) -> str:
        """
        Get the SRT formatted subtitles from the SubMaker object.
        Process the original text if it hasn't been processed yet.

        Returns:
            str: The SRT formatted subtitles.
        """
        if not self.cues and self.original_text and self.words_with_timing:
            self._create_exact_subtitles()
            self._ensure_cues_in_order()
        
        # If we still have no cues but do have original text, create a single cue with all content
        if not self.cues and self.original_text:
            if self.words_with_timing:
                first_word, first_offset, first_duration = self.words_with_timing[0]
                last_word, last_offset, last_duration = self.words_with_timing[-1]
                end_time = last_offset + last_duration
            else:
                # Default timing if no words with timing
                first_offset = 0
                end_time = 5000000  # 5 seconds
                
            self.cues.append(
                srt.Subtitle(
                    index=1,
                    start=srt.timedelta(microseconds=first_offset / 10),
                    end=srt.timedelta(microseconds=end_time / 10),
                    content=self.original_text,
                )
            )
            
        return srt.compose(self.cues)  # type: ignore

    def __str__(self) -> str:
        return self.get_srt()
