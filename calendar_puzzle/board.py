"""Board and piece representation for the Daily Calendar Puzzle (Spanish labels)."""

from __future__ import annotations

from dataclasses import dataclass


# ---------------------------------------------------------------------------
# Piece
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class Piece:
    """A puzzle piece defined by the cells it occupies (relative coordinates)."""

    name: str
    cells: frozenset[tuple[int, int]]

    # -- Transformations ---------------------------------------------------

    @staticmethod
    def _normalize(coords: frozenset[tuple[int, int]]) -> frozenset[tuple[int, int]]:
        """Translate coords so the minimum row and column are both 0."""
        min_r = min(r for r, _ in coords)
        min_c = min(c for _, c in coords)
        return frozenset((r - min_r, c - min_c) for r, c in coords)

    @staticmethod
    def _rotate_90(coords: frozenset[tuple[int, int]]) -> frozenset[tuple[int, int]]:
        """Rotate coords 90 degrees clockwise and normalize."""
        rotated = frozenset((c, -r) for r, c in coords)
        return Piece._normalize(rotated)

    @staticmethod
    def _reflect(coords: frozenset[tuple[int, int]]) -> frozenset[tuple[int, int]]:
        """Mirror coords horizontally and normalize."""
        reflected = frozenset((r, -c) for r, c in coords)
        return Piece._normalize(reflected)

    def all_orientations(self) -> list[Piece]:
        """Return all unique orientations (up to 8) via rotation and reflection."""
        seen: set[frozenset[tuple[int, int]]] = set()
        result: list[Piece] = []
        current = Piece._normalize(self.cells)
        for _ in range(4):
            for variant in (current, Piece._reflect(current)):
                n = Piece._normalize(variant)
                if n not in seen:
                    seen.add(n)
                    result.append(Piece(self.name, n))
            current = Piece._rotate_90(current)
        return result

    @staticmethod
    def from_grid(name: str, grid_lines: list[str]) -> Piece:
        """Create a Piece from visual grid lines ('X' = filled, anything else = empty)."""
        coords: set[tuple[int, int]] = set()
        for r, row in enumerate(grid_lines):
            for c, ch in enumerate(row):
                if ch == "X":
                    coords.add((r, c))
        return Piece(name, frozenset(coords))


# ---------------------------------------------------------------------------
# Board
# ---------------------------------------------------------------------------

class Board:
    """The 8x7 calendar puzzle board with Spanish labels."""

    ROWS = 8
    COLS = 7

    LABELS = [
        ["ENE", "FEB", "MAR", "ABR", "MAY", "JUN", None],
        ["JUL", "AGO", "SEP", "OCT", "NOV", "DIC", None],
        ["1",   "2",   "3",   "4",   "5",   "6",   "7"],
        ["8",   "9",   "10",  "11",  "12",  "13",  "14"],
        ["15",  "16",  "17",  "18",  "19",  "20",  "21"],
        ["22",  "23",  "24",  "25",  "26",  "27",  "28"],
        ["29",  "30",  "31",  "LUN", "MAR", "MIE", "JUE"],
        [None,  None,  None,  None,  "VIE", "SAB", "DOM"],
    ]

    _PIECE_GRIDS = {
        "A": ["XX", "XX", "OX"],
        "B": ["XO", "XO", "XX", "OX"],
        "C": ["XO", "XO", "XX"],
        "D": ["XOO", "XXX", "OOX"],
        "E": ["X", "X", "X", "X"],
        "F": ["OX", "XX", "XO"],
        "G": ["XXX", "XOX"],
        "H": ["XOO", "XXX", "XO O"],
        "I": ["XO", "XO", "XO", "XX"],
        "J": ["XOO", "XOO", "XXX"],
    }

    _MONTHS = {"ENE", "FEB", "MAR", "ABR", "MAY", "JUN",
               "JUL", "AGO", "SEP", "OCT", "NOV", "DIC"}
    _WEEKDAYS = {"LUN", "MAR", "MIE", "JUE", "VIE", "SAB", "DOM"}

    def __init__(self) -> None:
        self._month_cells: dict[str, tuple[int, int]] = {}
        self._day_cells: dict[int, tuple[int, int]] = {}
        self._weekday_cells: dict[str, tuple[int, int]] = {}

        for r, row in enumerate(self.LABELS):
            for c, label in enumerate(row):
                if label is None:
                    continue
                if r <= 1 and label in self._MONTHS:
                    self._month_cells[label] = (r, c)
                elif r >= 6 and label in self._WEEKDAYS:
                    self._weekday_cells[label] = (r, c)
                else:
                    self._day_cells[int(label)] = (r, c)

    @property
    def month_cells(self) -> dict[str, tuple[int, int]]:
        return self._month_cells

    @property
    def day_cells(self) -> dict[int, tuple[int, int]]:
        return self._day_cells

    @property
    def weekday_cells(self) -> dict[str, tuple[int, int]]:
        return self._weekday_cells

    @property
    def pieces(self) -> list[Piece]:
        """All 10 puzzle pieces."""
        return [Piece.from_grid(name, grid) for name, grid in self._PIECE_GRIDS.items()]

    def playable_cells(self) -> set[tuple[int, int]]:
        """All board positions that are not blocked (not None)."""
        cells: set[tuple[int, int]] = set()
        for r in range(self.ROWS):
            for c in range(self.COLS):
                if self.LABELS[r][c] is not None:
                    cells.add((r, c))
        return cells

    def target_cells(self, month: str, day: int, weekday: str) -> set[tuple[int, int]]:
        """The three cells that must remain uncovered for a given date."""
        return {
            self._month_cells[month],
            self._day_cells[day],
            self._weekday_cells[weekday],
        }
