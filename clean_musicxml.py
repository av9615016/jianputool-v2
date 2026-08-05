"""
clean_musicxml.py V35
JianpuTool Melody Preserve Cleaner

Purpose:
Keep original melody.
Only clean MusicXML structure.

MusicXML
 -> Preserve Notes
 -> Force 4/4
 -> Output
"""


import sys
import copy


from music21 import converter
from music21 import stream
from music21 import meter
from music21 import tempo
from music21 import note



print("==============================")
print(" CLEAN MUSICXML V35")
print(" Melody Preserve Cleaner")
print("==============================")



if len(sys.argv) < 3:

    sys.exit(
        "python clean_musicxml.py input.musicxml output.musicxml"
    )



input_file = sys.argv[1]

output_file = sys.argv[2]



# ==========================
# Load
# ==========================


print("讀取 MusicXML...")


score = converter.parse(
    input_file
)



# ==========================
# Preserve Notes
# ==========================


print("保留旋律...")


notes=[]



for n in score.flatten().notes:


    if isinstance(n,note.Note):


        notes.append(
            copy.deepcopy(n)
        )



print(
    "保留音符:",
    len(notes)
)



print("------------------------------")
print("旋律確認:")


for n in notes[:20]:

    print(
        n.pitch.nameWithOctave
    )


print("------------------------------")



# ==========================
# Build Clean Score
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


    part.append(
        n
    )



out = stream.Score()


out.append(
    part
)



# ==========================
# Write
# ==========================


print(
    "輸出:",
    output_file
)



out.write(
    "musicxml",
    fp=output_file
)



print(
    "CLEAN MUSICXML DONE"
)


print("==============================")