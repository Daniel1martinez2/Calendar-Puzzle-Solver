"""Solver for the Daily Calendar Puzzle using ILP (PuLP).

Strategy: exact cover via Integer Linear Programming.
- Pre-compute all valid placements for each piece on the board.
- Binary variable per placement: 1 if chosen, 0 if not.
- Constraint per piece: exactly one placement is selected.
- Constraint per cell: exactly one placement covers it.
"""

from __future__ import annotations

from typing import Optional

import pulp

from .board import Board, Piece

Placement = dict[str, frozenset[tuple[int, int]]]


class Solver:
    """ILP-based solver for the calendar puzzle."""

    def __init__(self, board: Board) -> None:
        self._board = board

    def solve(self, month: str, day: int, weekday: str) -> Optional[Placement]:
        """Solve the puzzle for a given date.

        Args:
            month:   Spanish abbreviation, e.g. "FEB"
            day:     Day number, e.g. 23
            weekday: Spanish abbreviation, e.g. "LUN"

        Returns:
            A Placement dict if a solution is found, None otherwise.
        """
        targets = self._board.target_cells(month, day, weekday)
        playable = self._board.playable_cells() - targets
        placements = self._precompute_placements(playable, self._board.pieces)
        return self._build_and_solve(playable, placements)

    @staticmethod
    def _precompute_placements(
        playable: set[tuple[int, int]],
        pieces: list[Piece],
    ) -> dict[str, list[frozenset[tuple[int, int]]]]:
        """For each piece, generate all valid placements on the board."""
        result: dict[str, list[frozenset[tuple[int, int]]]] = {}
        for piece in pieces:
            piece_placements: list[frozenset[tuple[int, int]]] = []
            for orientation in piece.all_orientations():
                for r in range(Board.ROWS):
                    for c in range(Board.COLS):
                        translated = frozenset(
                            (r + dr, c + dc) for dr, dc in orientation.cells
                        )
                        if translated.issubset(playable):
                            piece_placements.append(translated)
            result[piece.name] = piece_placements
        return result

    @staticmethod
    def _build_and_solve(
        playable: set[tuple[int, int]],
        placements: dict[str, list[frozenset[tuple[int, int]]]],
    ) -> Optional[Placement]:
        """Build and solve the ILP model. Return placement dict or None."""
        model = pulp.LpProblem("calendar_puzzle", pulp.LpMinimize)

        x: dict[tuple[str, int], pulp.LpVariable] = {}
        for piece_name, piece_placements in placements.items():
            for i in range(len(piece_placements)):
                x[(piece_name, i)] = pulp.LpVariable(
                    f"x_{piece_name}_{i}", cat="Binary"
                )

        # Exactly one placement per piece
        for piece_name, piece_placements in placements.items():
            model += (
                pulp.lpSum(x[(piece_name, i)] for i in range(len(piece_placements))) == 1,
                f"one_placement_{piece_name}",
            )

        # Exactly one piece covers each cell
        for cell in playable:
            covering_vars = []
            for piece_name, piece_placements in placements.items():
                for i, placement in enumerate(piece_placements):
                    if cell in placement:
                        covering_vars.append(x[(piece_name, i)])
            model += (
                pulp.lpSum(covering_vars) == 1,
                f"cover_cell_{cell[0]}_{cell[1]}",
            )

        model.solve(pulp.PULP_CBC_CMD(msg=0))

        if model.status == pulp.LpStatusOptimal:
            result: Placement = {}
            for (piece_name, i), var in x.items():
                if var.varValue == 1:
                    result[piece_name] = placements[piece_name][i]
            return result
        return None
