from music21 import converter

import sys

mid = converter.parse(sys.argv[1])

print("MIDI Tracks:")

for i, part in enumerate(mid.parts):
    print(
        i,
        part.partName,
        len(part.notes)
    )