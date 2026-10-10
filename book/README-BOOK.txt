README-BOOK.txt  —  Chess opening book for "Book / ตำรา" move classification
===========================================================================

1) SOURCE DATA
--------------
Repository : lichess-org/chess-openings
URL        : https://github.com/lichess-org/chess-openings
Raw files  : https://raw.githubusercontent.com/lichess-org/chess-openings/master/{a,b,c,d,e}.tsv
Files      : a.tsv, b.tsv, c.tsv, d.tsv, e.tsv  (ECO A-E, TSV: eco \t name \t pgn)
License    : CC0-1.0  (Creative Commons Zero v1.0 Universal / Public Domain Dedication)
             "As a collection of facts, this data set is in the public domain.
              ... the work is released under the CC0 Public Domain Dedication."
             No attribution required; credit is given here anyway.
Parsed      : 3865 opening lines / 7981 unique book positions.

2) OUTPUT FILE
--------------
Path       : book/openings.json
Size       : 486084 bytes  (~475 KB, under the ~500 KB budget)
Structure  : { "v": 1, "keys": [ "<poskey>", ... ] }   (sorted array of keys)

KEY ("position key") format
---------------------------
The first THREE space-separated fields of a FEN:
    <board placement> <side to move> <castling rights>
i.e. the full FEN with the en-passant field, halfmove clock and fullmove
number REMOVED.  Example:

    rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq

Why drop the en-passant field?  Different engines/JS libs (chess.js vs
python-chess) disagree about the ep field for double pushes with no legal
capture, so dropping it makes keys robust across both.

Every position reached AFTER a move of every opening line is stored as a key
(including the position after the last move of each line).  This means any
transposition into a named line is detected.

3) FAST LOOKUP IN JS  (load once, then O(1) Set membership)
-----------------------------------------------------------
  const BOOK = await fetch('book/openings.json').then(r => r.json());
  const BOOK_SET = new Set(BOOK.keys);            // ~2 ms for 7981 keys

  // fen = chess.js game.fen()   e.g. "rnbq... w KQkq - 3 3"
  function posKey(fen) { return fen.split(' ').slice(0, 3).join(' '); }

  const isBook = BOOK_SET.has(posKey(game.fen())); // true => "Book" grade

(The array is sorted, so a binary search via sorted-lookup is also possible,
but a Set built once is simpler and faster.)

4) TEST RESULTS  (tools/test_book.py)
-------------------------------------
  10/10 checks passed.
  HIT  (6): Ruy Lopez 1.e4 e5 2.Nf3 Nc6 3.Bb5 ; Queen's Gambit 1.d4 d5 2.c4 ;
            Sicilian 1.e4 c5 ; Italian 1.e4 e5 2.Nf3 Nc6 3.Bc4 ; French 1.e4 e6 ;
            Sicilian Najdorf ...5...a6
  MISS (4): random middlegame FEN ; K+P vs K endgame ; K+Q vs K endgame ;
            7-piece late position (no castling rights)

5) REBUILD / RE-TEST
--------------------
  # build (downloads TSVs into tools/cache/ on first run)
  cd 50_research/2026-10-10_chess-app
  uv run --with chess python tools/build_opening_book.py

  # test
  uv run --with chess python tools/test_book.py

Scripts: tools/build_opening_book.py  (build),  tools/test_book.py  (verify)

6) NOTE ON OPENING NAMES
------------------------
To stay under the ~500 KB byte budget, the JSON stores only the position keys
(membership), not the human-readable ECO/name text.  If you later want to show
"you are in the Ruy Lopez", add a separate map keyed on a line's FINAL position
(only ~3865 entries) rather than storing a name per position.
