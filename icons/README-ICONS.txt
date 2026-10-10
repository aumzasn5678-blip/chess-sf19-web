README-ICONS.txt
================================================================
Move-quality icon set (chess.com style) for Chess AI web app
Folder: E:\Hermes_workbench\50_research\2026-10-10_chess-app\icons\
Generated: 2026-10-10
================================================================

SUMMARY
- 11 icons, all PNG 96x96 px, transparent background (RGBA), < 20 KB each.
- Style: solid coloured circle + white symbol inside (chess.com "game review" look).
- 10 icons are genuine chess.com move-classification artwork (see SOURCE).
- 1 icon ("forced") was drawn by us (chess.com has no "forced" classification).

FILE LIST
----------------------------------------------------------------
file            size(px)  bytes   symbol        circle colour      source
----------------------------------------------------------------
book.png        96x96     13499   book icon     brown (#A28462)    chess.com  (BookMove)
brilliant.png   96x96     15709   !!            teal   (#1DABA4)    chess.com  (Brilliant)
great.png       96x96     12842   !             blue                chess.com  (GreatMove)
best.png        96x96     15571   star (*)      green               chess.com  (BestMove)
excellent.png   96x96     14060   thumbs-up     light green         chess.com  (Excellent)
good.png        96x96     16790   check (v)     sage green          chess.com  (Good)
inaccuracy.png  96x96     17960   ?!            yellow              chess.com  (Inaccuracy)
mistake.png     96x96     14048   ?             orange              chess.com  (Mistake)
blunder.png     96x96     16695   ??            red                 chess.com  (Blunder)
miss.png        96x96     17576   x (cross)     coral red           chess.com  (Miss)
forced.png      96x96      2753   right arrow   grey (#6B7280)      drawn by us
----------------------------------------------------------------

SOURCE (authentic chess.com artwork)
The 10 chess.com icons originate from chess.com's own game-review asset
pack. Direct hot-linking to chess.com's CDN is blocked / unstable, so the
artwork was obtained from a public mirror of the chess.com icon set:
  Repository: https://github.com/cheeseonamonkey/Chess.com-icon-set
  Raw path  : https://raw.githubusercontent.com/cheeseonamonkey/Chess.com-icon-set/main/IconsOnly/<Name>.png
  e.g. https://raw.githubusercontent.com/cheeseonamonkey/Chess.com-icon-set/main/IconsOnly/Brilliant.png
Name mapping used:  BestMove->best, BookMove->book, GreatMove->great,
  Brilliant, Excellent, Good, Inaccuracy, Mistake, Blunder, Miss -> same.
Processing applied by us (ImageMagick): cropped to the circle, applied a
circular alpha mask to remove the dark-grey background the mirror used,
then scaled/padded to a clean 96x96 transparent PNG. Symbols and colours
are unchanged from the original chess.com artwork.

SOURCE ("forced" icon)
chess.com's game review does not include a "forced" classification, so no
official artwork exists. forced.png was drawn by us with ImageMagick:
  grey circle (#6B7280) + white right-arrow, to match the same visual style.

COPYRIGHT / LICENCE NOTES
- book/best/great/brilliant/excellent/good/inaccuracy/mistake/blunder/miss
  are the property of Chess.com. Keep this app's use personal / non-commercial;
  do NOT redistribute these icons commercially or as a public asset pack
  without Chess.com's permission.
- forced.png was created by us -> free to use, modify and redistribute freely.
- verify_sheet.png is a contact sheet of all 11 icons (for quick visual check).

HOW TO USE (in index.html, single-file web app)
  <img src="icons/brilliant.png" width="24" height="24" alt="Brilliant">
  or as an overlay on the destination square after a move is played.
================================================================
