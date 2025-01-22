"""
Defines a compact representation of a duration using nanoseconds.
"""

from dataclasses import dataclass
from typing import Tuple
from math import floor


@dataclass
class Duration:
    """
    Represents a time duration stored as a single integer value in nanoseconds.

    Attributes:
        elapsed: The total duration in nanoseconds.
    """
    elapsed: int = 0  # nanoseconds

    @staticmethod
    def parse(seconds: int, nanoseconds: int) -> "Duration":
        """
        Creates a Duration object from seconds and nanoseconds.

        Args:
            seconds: The number of seconds in the duration.
            nanoseconds: The additional nanoseconds beyond the seconds.

        Returns:
            A Duration object representing the specified duration.
        """
        return Duration(nanoseconds + (seconds * pow(10, 9)))

    def get_seconds_and_nano(self) -> Tuple[int, int]:
        """
        Extracts the seconds and nanoseconds components from the duration.

        Returns:
            A tuple containing:
                - The number of seconds in the duration.
                - The remaining nanoseconds after the seconds.
        """
        sec = floor(self.elapsed / pow(10, 9))
        nsec = self.elapsed - (sec * pow(10, 9))
        return sec, nsec

    def __eq__(self, other: object) -> bool:
        """
        Compares two Duration objects for equality.

        Args:
            other: The object to compare against.

        Returns:
            True if the objects have the same elapsed time, False otherwise.
        """
        if isinstance(other, Duration):
            return self.elapsed == other.elapsed
        return False
