#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
test_book.py
============
Verify that book/openings.json is usable: load it, then check that known
opening positions HIT and non-opening positions MISS.

Run:
  uv run --with chess python tools/test_book.py
"""

import json
import os
import sys

try:
    import chess
except ImportError:
    sys.exit("python-chess required:  uv run --with chess python tools/test_book.py")

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
BOOK = os.path.join(ROOT, "book", "openings.json")


def key_for(board):
    return " ".join(board.fen().split(" ")[:3])


def load_keys():
    with open(BOOK, "r", encoding="utf-8") as f:
        data = json.load(f)
    return set(data["keys"])


def key_from_moves(san_list):
    b = chess.Board()
    for san in san_list:
        b.push_san(san)
    return key_for(b)


# ---- positions that MUST be in the book (hits) ----------------------------
HITS = {
    "Ruy Lopez (1.e4 e5 2.Nf3 Nc6 3.Bb5)":
        ["e4", "e5", "Nf3", "Nc6", "Bb5"],
    "Queen's Gambit (1.d4 d5 2.c4)":
        ["d4", "d5", "c4"],
    "Sicilian Defense (1.e4 c5)":
        ["e4", "c5"],
    "Italian Game (1.e4 e5 2.Nf3 Nc6 3.Bc4)":
        ["e4", "e5", "Nf3", "Nc6", "Bc4"],
    "French Defense (1.e4 e6)":
        ["e4", "e6"],
    "Sicilian Najdorf (…5…a6)":
        ["e4", "c5", "Nf3", "d6", "d4", "cxd4", "Nxd4", "Nf6", "Nc3", "a6"],
}

# ---- positions that must NOT be in the book (misses) ----------------------
MISSES = {
    "Random middlegame (crafted FEN, not an opening)":
        "r1bq1rk1/pp2bppp/2n1pn2/3p4/3P4/2NBPN2/PP3PPP/R1BQ1RK1 w - -",
    "Sparse endgame (K+P vs K)":
        "8/8/8/4k3/8/8/4P3/4K3 w - -",
    "K+Q vs K endgame":
        "8/8/8/4k3/8/8/6Q1/4K3 w - -",
    "Late-game 7 pieces, castling gone":
        "r4rk1/1pp2ppp/p1np4/8/2B1P3/2P2N2/PP3PPP/2KR3R w - -",
}


def main():
    if not os.path.exists(BOOK):
        sys.exit("missing %s - run build_opening_book.py first" % BOOK)
    keys = load_keys()
    print("loaded %d keys from %s (%d bytes)\n"
          % (len(keys), os.path.relpath(BOOK, ROOT), os.path.getsize(BOOK)))

    failures = 0

    print("== expected HIT ==")
    for name, sans in HITS.items():
        k = key_from_moves(sans)
        got = k in keys
        ok = got is True
        failures += 0 if ok else 1
        print("  [%s] %s\n        key: %s" % ("HIT " if got else "MISS", name, k))
        if not ok:
            print("        !! expected HIT but MISS")

    print("\n== expected MISS ==")
    for name, fen in MISSES.items():
        k = " ".join(fen.split(" ")[:3])
        got = k in keys
        ok = got is False
        failures += 0 if ok else 1
        print("  [%s] %s\n        key: %s" % ("HIT " if got else "MISS", name, k))
        if not ok:
            print("        !! expected MISS but HIT")

    total = len(HITS) + len(MISSES)
    print("\n%d/%d checks passed, %d failed" % (total - failures, total, failures))
    sys.exit(1 if failures else 0)


if __name__ == "__main__":
    main()
