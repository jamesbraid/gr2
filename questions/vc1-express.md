# Open questions: VC1 on the Express board

## 1. Line-program encoding and the frame table's line counts

The 237-half-word images and the frame table's records decode to a shape (header, `lines, address` pairs, `ff ff`) but the record counts
sum to 1105 (60 Hz) and 1101 (72 Hz) lines against a conventional 1066 or 1072, and the line-program words are not decoded. Routes tried:
byte dumps of every shipped file; Entry board tables (newport), which use a different shape. Next: the LSI Logic VC1 data sheet (not
held, searched `VC1`), `ide.IP20` video-timing diagnostics, the `*.u` names that look like annotated listings (`vof` files are
binary here).

## 3. Monitor code meaning

Which physical monitor each code 0 to 15 means. Next: Owner's Guide and monitor cable documents, `ide.IP20`.

## 4. Missing timing files and 120 Hz stereo

The TR lists 1024 by 768 at 60, 72 and 30 Hz and 120 Hz stereo; the held `vof` directory has `iris3k`, `presenter` and `rs343a`
but no obvious 72 Hz 1024 by 768 or stereo file. Next: search other IRIX media sets for further `GR2/vof` files.

## 5. Cursor glyph encoding and colours

Kernel loads zeros; the PROM glyph (256 half-words at SRAM `0x200`) is not decoded. Next: decode the PROM's cursor data; X server cursor
loader; XMAP5 questions 3.

## 6. VC1 revision values and `testreg` semantics

The value a real chip returns, and whether other addresses return other test data. Next: none from software.
