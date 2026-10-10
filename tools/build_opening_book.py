#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
build_opening_book.py
=====================
Build a compact chess opening book for fast client-side "Book" classification.

Source data:
  lichess-org/chess-openings TSV files (a.tsv .. e.tsv)
  https://github.com/lichess-org/chess-openings
  License: CC0-1.0 (Public Domain Dedication)

Output:
  book/openings.json

Key format
----------
Each book position is keyed by the first THREE fields of the FEN:
    <board placement> <side to move> <castling rights>
i.e. FEN with the en-passant field, halfmove clock and fullmove number
removed.  This is a deliberate choice so that the key computed by chess.js
(whose en-passant field can differ from python-chess for illegal-but-legal
double pushes) always matches.  Example:

    rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq

Every position reached AFTER a move of every opening line is stored, so a
transposition into any named line is detected.

Usage:
  uv run --with chess python tools/build_opening_book.py
  (or: python tools/build_opening_book.py  with python-chess installed)
"""

import json
import os
import sys
import urllib.request

try:
    import chess
    import chess.pgn
except ImportError:
    sys.exit("python-chess required:  uv run --with chess python tools/build_opening_book.py")

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
BOOK_DIR = os.path.join(ROOT, "book")
CACHE_DIR = os.path.join(HERE, "cache")
OUT_PATH = os.path.join(BOOK_DIR, "openings.json")

TSV_FILES = ["a.tsv", "b.tsv", "c.tsv", "d.tsv", "e.tsv"]
BASE_URL = "https://raw.githubusercontent.com/lichess-org/chess-openings/master/"

# Soft cap on output size (bytes). If exceeded we keep only the most common
# openings (by ECO order + line length) until we fit.
MAX_BYTES = 500 * 1024
KEEP_LIMIT = 1000  # fallback: keep at most this many lines if over budget


def fetch(name):
    """Download a TSV to the local cache (once) and return its path."""
    os.makedirs(CACHE_DIR, exist_ok=True)
    path = os.path.join(CACHE_DIR, name)
    if not os.path.exists(path) or os.path.getsize(path) == 0:
        url = BASE_URL + name
        sys.stderr.write("downloading %s\n" % url)
        with urllib.request.urlopen(url, timeout=60) as r:
            data = r.read()
        with open(path, "wb") as f:
            f.write(data)
    return path


def pos_key(board):
    """FEN -> compact positional key (board + side to move + castling)."""
    parts = board.fen().split(" ")
    return " ".join(parts[:3])


def load_lines():
    """Yield (eco, name, list_of_keys) for every opening line."""
    lines = []
    for fn in TSV_FILES:
        path = fetch(fn)
        with open(path, "r", encoding="utf-8") as f:
            next(f, None)  # header: eco \t name \t pgn
            for raw in f:
                raw = raw.rstrip("\n")
                if not raw:
                    continue
                cols = raw.split("\t")
                if len(cols) < 3:
                    continue
                eco, name, pgn = cols[0], cols[1], cols[2]
                game = chess.pgn.read_game(_pgn_io(pgn))
                if game is None:
                    continue
                board = game.board()
                keys = []
                ok = True
                for mv in game.mainline_moves():
                    if mv not in board.legal_moves:
                        ok = False
                        break
                    board.push(mv)
                    keys.append(pos_key(board))
                if ok and keys:
                    lines.append((eco, name, keys))
    return lines


def _pgn_io(pgn):
    import io
    return io.StringIO(pgn)


def build():
    lines = load_lines()
    sys.stderr.write("parsed %d opening lines\n" % len(lines))

    # --- pass 1: size with everything -------------------------------------
    def emit(sel):
        keys = set()
        for _eco, _name, line_keys in sel:
            keys.update(line_keys)
        # Sorted array of keys = smallest JSON with O(1) Set membership in JS.
        data = {"v": 1, "keys": sorted(keys)}
        return data, keys

    sel = lines
    data, keyset = emit(sel)
    blob = json.dumps(data, separators=(",", ":"), ensure_ascii=True)
    nbytes = len(blob.encode("utf-8"))
    sys.stderr.write("full book: %d keys, %d bytes\n" % (len(keyset), nbytes))

    # --- trim if over budget ----------------------------------------------
    if nbytes > MAX_BYTES:
        sys.stderr.write("over budget -> trimming to first %d lines\n" % KEEP_LIMIT)
        sel = lines[:KEEP_LIMIT]
        data, keyset = emit(sel)
        blob = json.dumps(data, separators=(",", ":"), ensure_ascii=True)
        nbytes = len(blob.encode("utf-8"))
        sys.stderr.write("trimmed book: %d keys, %d bytes\n" % (len(keyset), nbytes))

    os.makedirs(BOOK_DIR, exist_ok=True)
    with open(OUT_PATH, "w", encoding="utf-8") as f:
        f.write(blob)

    meta = {
        "lines": len(sel),
        "keys": len(keyset),
        "bytes": nbytes,
    }
    sys.stderr.write("wrote %s\n" % OUT_PATH)
    print(json.dumps(meta))
    return meta


if __name__ == "__main__":
    build()
