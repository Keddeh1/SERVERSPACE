# Compact owner count symbols

Owner instruction: replace the A/B marker plus count with a letter conveying both. This implementation interprets the suggested B range as L–T (nine symbols). Framing and long-run segmentation are implementation choices open to owner revision.

| Run length | Ones (A) | Zeros (B) |
|---|---|---|
| 1 | C | L |
| 2 | D | M |
| 3 | E | N |
| 4 | F | O |
| 5 | G | P |
| 6 | H | Q |
| 7 | I | R |
| 8 | J | S |
| 9 | K | T |

11111000 → GN. The bit type is intrinsic to the symbol; no repeated A or B is needed. A 16-one run becomes KI (9+7). Canonical segmentation permits adjacent same-type symbols only when the preceding chunk is nine. That prevents competing encodings such as C+C instead of D. `ABC1:<bit-length>:<symbols>` distinguishes this format from decimal `AB1`; exact total length and canonical symbols are checked before reconstruction. Empty input has an empty symbol sequence.

Subsequent compact layers encode the bytes of the preceding frame, preserving the binary→symbol→binary→symbol contract. Counting repeated symbols directly would be a separate, explicitly tagged alphabet transform and is not silently substituted. This format is reversible abstraction, with no encryption keys.

Removing the redundant marker reduces alternating-run token bytes from two to one, but length-nine chunking penalizes very long runs compared with decimal counts. Synthetic 1,024-byte zero input is 14 bytes in decimal AB and 921 bytes in compact framing; alternating input is 16,393 versus 8,202. Exact figures and all attachment-prefix comparisons are in the empirical measurement record. This is a serialization tradeoff, not universal compression. Full document and chunk-level format selection remain future work.

Executed suite: eleven tests, including exhaustive compact round trips of 65,536 two-byte inputs, mapping examples, long runs, multiple layers, malformed/noncanonical input and existing library integrity tests. Implementations: scripts/library/ab_codec.py; reproduction: python3 -B scripts/library/measure_compact_ab.py.
