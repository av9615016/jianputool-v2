"""
jianpu_fix_musicxml.py V19
JianpuTool Melody Preserve Engine

Purpose:
Keep melody order.
Only fix MusicXML structure.

MusicXML
 -> Preserve Notes
 -> Fix Time Signature
 -> Fix Measures
 -> Output
"""


import sys
import copy

from music21 import converter
from music21 import stream
from music21 import meter
from music21 import note
from music21 import tempo



print("==============================")
print(" JIANPU FIX MUSICXML V19")
print(" Melody Preserve Engine")
print("==============================")



if len(sys.argv) < 3:

    sys.exit(
        "python jianpu_fix_musicxml.py input.musicxml output.musicxml"
    )



input_file = sys.argv[1]

output_file = sys.argv[2]



# ==========================
# Load
# ==========================


print("load musicxml")


score = converter.parse(
    input_file
)



# ==========================
# Extract original notes
# ==========================


print("preserve melody")



notes=[]


for n in score.flatten().notes:


    if isinstance(n,note.Note):

        notes.append(
            copy.deepcopy(n)
        )



print(
    "notes:",
    len(notes)
)



# ==========================
# Show melody
# ==========================


print("------------------------------")
print("MELODY CHECK")


for n in notes[:30]:

    print(
        n.pitch.nameWithOctave
    )


print("------------------------------")



# ==========================
# Rebuild Part
# ==========================


part = stream.Part()



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



for n in notes:


    # 保留原音符

    part.append(
        n
    )



# ==========================
# Make score
# ==========================


out = stream.Score()


out.append(
    part
)



# ==========================
# Write
# ==========================


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