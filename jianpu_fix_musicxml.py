"""
JIANPU FIX MUSICXML V20
Final Melody Lock Engine

Purpose:
MusicXML -> Jianpu stable conversion

Features:
- Preserve melody
- Lock C major
- Lock octave
- Remove interference
"""


import sys
import copy

from music21 import converter
from music21 import stream
from music21 import note
from music21 import meter
from music21 import key
from music21 import tempo



print("==============================")
print(" JIANPU FIX MUSICXML V20")
print(" Final Melody Lock Engine")
print("==============================")


if len(sys.argv)<3:

    sys.exit(
        "python jianpu_fix_musicxml.py input.musicxml output.musicxml"
    )


input_file=sys.argv[1]

output_file=sys.argv[2]



# ==========================
# Load
# ==========================


print("load musicxml")


score=converter.parse(
    input_file
)



# ==========================
# Extract melody
# ==========================


melody=[]


for n in score.flat.notes:


    if isinstance(n,note.Note):

        melody.append(
            n
        )



print(
    "notes:",
    len(melody)
)



print("------------------------------")
print("MELODY LOCK CHECK")



for n in melody[:20]:

    print(
        n.pitch.nameWithOctave
    )



# ==========================
# Create clean score
# ==========================


part=stream.Part()



# Key

part.append(
    key.KeySignature(
        0
    )
)



# Time

part.append(
    meter.TimeSignature(
        "4/4"
    )
)



part.append(
    tempo.MetronomeMark(
        number=80
    )
)



# ==========================
# Copy notes
# ==========================


for old in melody:


    new=note.Note()


    # lock pitch

    new.pitch.midi = old.pitch.midi



    # preserve duration

    new.duration = copy.deepcopy(
        old.duration
    )



    # remove accidental ambiguity

    new.pitch.accidental=None



    part.append(
        new
    )



# ==========================
# Build score
# ==========================


out=stream.Score()


out.append(
    part
)



print(
    "WRITE:",
    output_file
)



out.write(
    "musicxml",
    fp=output_file
)



print(
    "DONE"
)

print("==============================")