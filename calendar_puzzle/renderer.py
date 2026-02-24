"""Visualization tools for the calendar puzzle (Jupyter notebook)."""

from __future__ import annotations

from IPython.display import display, HTML

from .board import Board, Piece
from .solver import Placement


class Renderer:
    """HTML-based renderer for Jupyter notebooks."""

    _BG = {
        "A": "#ef4444", "B": "#22c55e", "C": "#facc15", "D": "#3b82f6",
        "E": "#a855f7", "F": "#06b6d4", "G": "#f97316", "H": "#ec4899",
        "I": "#84cc16", "J": "#64748b",
    }
    _FG = {
        "A": "#fff", "B": "#fff", "C": "#000", "D": "#fff", "E": "#fff",
        "F": "#000", "G": "#000", "H": "#fff", "I": "#000", "J": "#fff",
    }

    def __init__(self, board: Board) -> None:
        self._board = board

    def show_board(
        self,
        placement: Placement,
        targets: set[tuple[int, int]] | None = None,
        size: int = 54,
        show_labels: bool = True,
    ) -> None:
        """Display solved board in a Jupyter cell."""
        if targets is None:
            targets = set()

        owner = [[None] * Board.COLS for _ in range(Board.ROWS)]
        for name, cells in placement.items():
            for r, c in cells:
                owner[r][c] = name

        tds = ""
        for r in range(Board.ROWS):
            tds += "<tr>"
            for c in range(Board.COLS):
                label = Board.LABELS[r][c]
                s = f"width:{size}px;height:{size}px;text-align:center;vertical-align:middle;"
                if label is None:
                    tds += f'<td style="{s}background:#1e1e1e;border:none;"></td>'
                    continue
                me = owner[r][c]
                brd = self._borders(owner, r, c)
                if (r, c) in targets:
                    tds += f'<td style="{s}background:#fef9c3;color:#92400e;{brd}">{label}</td>'
                elif me:
                    cell_text = me if show_labels else ""
                    tds += f'<td style="{s}background:{self._BG[me]};color:{self._FG[me]};{brd}">{cell_text}</td>'
                else:
                    tds += f'<td style="{s}background:#f1f5f9;color:#94a3b8;{brd}">{label}</td>'
            tds += "</tr>"

        display(HTML(
            f'<table style="border-collapse:collapse;font:700 14px monospace;">{tds}</table>'
        ))

    def show_pieces(self, size: int = 32) -> None:
        """Display all 10 pieces with all orientations in a Jupyter cell."""
        html = ""
        for piece in sorted(self._board.pieces, key=lambda p: p.name):
            orients = piece.all_orientations()
            html += (
                f'<div style="margin-bottom:12px;">'
                f'<b style="font:700 13px monospace;">Piece {piece.name} — {len(piece.cells)} cells, '
                f'{len(orients)} orientations</b>'
                f'<div style="display:flex;flex-wrap:wrap;align-items:flex-start;gap:8px;">'
            )
            for o in orients:
                html += self._piece_table(o, size)
            html += "</div></div>"
        display(HTML(html))

    @staticmethod
    def _borders(owner: list[list[str | None]], r: int, c: int) -> str:
        """Return CSS border string. Thick between different pieces."""
        me = owner[r][c]
        sides = {}
        for side, dr, dc in [("top", -1, 0), ("right", 0, 1), ("bottom", 1, 0), ("left", 0, -1)]:
            nr, nc = r + dr, c + dc
            if not (0 <= nr < Board.ROWS and 0 <= nc < Board.COLS):
                nb = None
            elif Board.LABELS[nr][nc] is None:
                nb = None
            else:
                nb = owner[nr][nc]
            if nb != me or nb is None:
                sides[side] = "3px solid #334155"
            else:
                sides[side] = "1px solid rgba(0,0,0,0.06)"
        return "; ".join(f"border-{s}: {v}" for s, v in sides.items())

    def _piece_table(self, piece: Piece, size: int = 32) -> str:
        """Small HTML table for one piece orientation."""
        coords = Piece._normalize(piece.cells)
        cells = set(coords)
        R = max(r for r, _ in coords) + 1
        C = max(c for _, c in coords) + 1
        bg, fg = self._BG[piece.name], self._FG[piece.name]

        tds = ""
        for r in range(R):
            tds += "<tr>"
            for c in range(C):
                s = f"width:{size}px;height:{size}px;text-align:center;"
                if (r, c) in cells:
                    brd = []
                    for side, dr, dc in [("top", -1, 0), ("right", 0, 1), ("bottom", 1, 0), ("left", 0, -1)]:
                        if (r + dr, c + dc) in cells:
                            brd.append(f"border-{side}:2px solid {bg}")
                        else:
                            brd.append(f"border-{side}:2px solid #334155")
                    tds += f'<td style="{s}background:{bg};color:{fg};{"".join(b + ";" for b in brd)}">{piece.name}</td>'
                else:
                    tds += f'<td style="{s}border:none;"></td>'
            tds += "</tr>"
        return f'<table style="border-collapse:collapse;display:inline-block;margin:4px;font:700 12px monospace;">{tds}</table>'
