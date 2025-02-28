"""SubMaker module is used to generate subtitles from WordBoundary events."""

from typing import List, Dict, Tuple, Optional
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
        self.boundary_events: List[Tuple[str, int, int]] = []  # (text, offset, duration)
        
    def set_original_text(self, text: str) -> None:
        """
        Set the original text.

        Args:
            text (str): The original input text

        Returns:
            None
        """
        self.original_text = text
        self.boundary_events = []
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
        
        # Store boundary event information
        self.boundary_events.append((
            msg["text"],
            msg["offset"],
            msg["duration"]
        ))

    def create_meaningful_subtitles(self, words_per_subtitle: int = 5) -> None:
        """
        Create subtitles with meaningful phrases/sentences rather than word by word.
        
        Args:
            words_per_subtitle (int): Target number of words per subtitle
        """
        if not self.original_text or not self.boundary_events:
            return
            
        # Track which positions in the original text have been assigned to subtitles
        word_positions: List[Tuple[int, int, int, int]] = []  # start, end, offset, duration
        
        # First, locate all words from boundary events in the original text
        pos = 0
        for word, offset, duration in self.boundary_events:
            # Search for this word in the original text
            pattern = re.compile(r'\b' + re.escape(word) + r'\b', re.IGNORECASE)
            match = pattern.search(self.original_text[pos:])
            
            if match:
                start_pos = pos + match.start()
                end_pos = pos + match.end()
                word_positions.append((start_pos, end_pos, offset, duration))
                pos = end_pos
            else:
                # If we can't find it with word boundaries, try without
                match = re.search(re.escape(word), self.original_text[pos:], re.IGNORECASE)
                if match:
                    start_pos = pos + match.start()
                    end_pos = pos + match.end()
                    word_positions.append((start_pos, end_pos, offset, duration))
                    pos = end_pos
                # If still not found, search from beginning (helps with repeated words)
                else:
                    match = re.search(re.escape(word), self.original_text, re.IGNORECASE)
                    if match:
                        start_pos = match.start()
                        end_pos = match.end()
                        word_positions.append((start_pos, end_pos, offset, duration))
        
        # Sort word positions by their order in the text
        word_positions.sort(key=lambda x: x[0])
        
        # Group words into meaningful phrases/sentences
        subtitles = []
        current_group = []
        current_words = 0
        
        for i, (start, end, offset, duration) in enumerate(word_positions):
            current_group.append((start, end, offset, duration))
            current_words += 1
            
            # Check if we should create a subtitle from the current group
            create_subtitle = False
            
            # Create a subtitle if we've reached the target number of words
            if current_words >= words_per_subtitle:
                create_subtitle = True
            
            # Create a subtitle on sentence boundaries (period, question mark, exclamation mark)
            elif self.original_text[end:end+2].strip() in ['.', '?', '!', '."', '?"', '!"']:
                create_subtitle = True
                
            # Create a subtitle on clause boundaries (comma, semicolon, colon)
            elif self.original_text[end:end+2].strip() in [',', ';', ':']:
                if current_words >= 3:  # Only break on punctuation if we have enough words
                    create_subtitle = True
            
            # Always create a subtitle at the last word
            elif i == len(word_positions) - 1:
                create_subtitle = True
                
            if create_subtitle and current_group:
                group_start = current_group[0][0]
                group_end = current_group[-1][1]
                
                # Include any trailing punctuation
                while (group_end < len(self.original_text) and 
                       not self.original_text[group_end].isalnum() and
                       not self.original_text[group_end].isspace()):
                    group_end += 1
                    
                # Extract text for this group
                subtitle_text = self.original_text[group_start:group_end]
                
                # Get timing information
                start_time = current_group[0][2]  # First word offset
                end_time = current_group[-1][2] + current_group[-1][3]  # Last word offset + duration
                
                subtitles.append((subtitle_text, start_time, end_time))
                current_group = []
                current_words = 0
        
        # Create final subtitle for any remaining words
        if current_group:
            group_start = current_group[0][0]
            group_end = current_group[-1][1]
            
            # Include any trailing punctuation
            while (group_end < len(self.original_text) and 
                   not self.original_text[group_end].isalnum() and
                   not self.original_text[group_end].isspace()):
                group_end += 1
                
            subtitle_text = self.original_text[group_start:group_end]
            start_time = current_group[0][2]
            end_time = current_group[-1][2] + current_group[-1][3]
            
            subtitles.append((subtitle_text, start_time, end_time))
        
        # Create subtitle objects
        for i, (text, start_time, end_time) in enumerate(subtitles):
            self.cues.append(
                srt.Subtitle(
                    index=i+1,
                    start=srt.timedelta(microseconds=start_time / 10),
                    end=srt.timedelta(microseconds=end_time / 10),
                    content=text.strip(),
                )
            )
        
        # Check if any text remains at the end that wasn't covered
        if word_positions:
            last_position = word_positions[-1][1]
            if last_position < len(self.original_text) and self.original_text[last_position:].strip():
                remaining_text = self.original_text[last_position:].strip()
                last_offset, last_duration = word_positions[-1][2], word_positions[-1][3]
                end_time = last_offset + last_duration
                
                self.cues.append(
                    srt.Subtitle(
                        index=len(self.cues) + 1,
                        start=srt.timedelta(microseconds=end_time / 10),
                        end=srt.timedelta(microseconds=(end_time + 2000000) / 10),  # Add 2 seconds
                        content=remaining_text,
                    )
                )
        
        # Fix any overlapping timings
        self._fix_timing_issues()
    
    def _fix_timing_issues(self) -> None:
        """Fix any timing issues between subtitles."""
        if not self.cues:
            return
            
        # Sort cues by start time
        self.cues.sort(key=lambda c: c.start.total_seconds())
        
        # Fix overlapping subtitle times and too short durations
        min_duration = 0.7  # seconds
        for i in range(len(self.cues)):
            start_time = self.cues[i].start.total_seconds()
            end_time = self.cues[i].end.total_seconds()
            
            # Ensure minimum duration
            if end_time - start_time < min_duration:
                end_time = start_time + min_duration
                self.cues[i] = srt.Subtitle(
                    index=self.cues[i].index,
                    start=self.cues[i].start,
                    end=srt.timedelta(seconds=end_time),
                    content=self.cues[i].content,
                )
            
            # Fix overlaps with next subtitle
            if i < len(self.cues) - 1:
                next_start = self.cues[i+1].start.total_seconds()
                if end_time > next_start:
                    # Split the difference
                    middle = (end_time + next_start) / 2
                    
                    # Ensure minimum duration for current subtitle
                    if middle - start_time < min_duration:
                        middle = start_time + min_duration
                    
                    self.cues[i] = srt.Subtitle(
                        index=self.cues[i].index,
                        start=self.cues[i].start,
                        end=srt.timedelta(seconds=middle),
                        content=self.cues[i].content,
                    )
                    
                    self.cues[i+1] = srt.Subtitle(
                        index=self.cues[i+1].index,
                        start=srt.timedelta(seconds=middle),
                        end=self.cues[i+1].end,
                        content=self.cues[i+1].content,
                    )
        
        # Renumber subtitles
        for i in range(len(self.cues)):
            self.cues[i] = srt.Subtitle(
                index=i+1,
                start=self.cues[i].start,
                end=self.cues[i].end,
                content=self.cues[i].content,
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
        
        # Renumber subtitles
        for i in range(len(new_cues)):
            new_cues[i] = srt.Subtitle(
                index=i+1,
                start=new_cues[i].start,
                end=new_cues[i].end,
                content=new_cues[i].content,
            )
        
        self.cues = new_cues

    def get_srt(self) -> str:
        """
        Get the SRT formatted subtitles from the SubMaker object.
        Process the original text if it hasn't been processed yet.

        Returns:
            str: The SRT formatted subtitles.
        """
        if not self.cues and self.original_text and self.boundary_events:
            self.create_meaningful_subtitles()
        
        # If we still have no cues but do have original text, create a single subtitle
        if not self.cues and self.original_text:
            if self.boundary_events:
                first_word, first_offset, first_duration = self.boundary_events[0]
                last_word, last_offset, last_duration = self.boundary_events[-1]
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
