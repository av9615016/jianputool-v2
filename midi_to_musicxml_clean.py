# ============================================================
# midi_to_musicxml_clean.py
#
# JianpuTool MVP 1.1
#
# MIDI -> MusicXML
#
# FIX:
# output argument is FILE, not directory
#
# ============================================================


import sys
import os

from music21 import converter
from music21 import stream
from music21 import note
from music21 import chord
from music21 import meter
from music21 import tempo



print("================ MIDI TO MUSICXML CLEAN ================")



# ------------------------------------------------------------
# Arguments
# ------------------------------------------------------------

if len(sys.argv) < 3:

    print(
        "Usage:"
    )

    print(
        "python midi_to_musicxml_clean.py input.mid output.musicxml"
    )

    sys.exit(1)



midi_file = sys.argv[1]
output_file = sys.argv[2]



if not os.path.isfile(midi_file):

    raise Exception(
        f"MIDI not found: {midi_file}"
    )



# ------------------------------------------------------------
# Output folder
# ------------------------------------------------------------

output_dir = os.path.dirname(
    output_file
)


if output_dir:

    os.makedirs(
        output_dir,
        exist_ok=True
    )



# ------------------------------------------------------------
# Read MIDI
# ------------------------------------------------------------

print("讀取 MIDI...")


score = converter.parse(
    midi_file
)



# ------------------------------------------------------------
# Find melody part
# ------------------------------------------------------------

print("取得 Piano Part...")


parts = score.parts


if len(parts) > 0:

    part = parts[0]

else:

    part = score



# ------------------------------------------------------------
# Extract notes
# ------------------------------------------------------------

print("抽取旋律...")


melody = stream.Part()


melody.append(
    meter.TimeSignature("4/4")
)



# tempo

melody.append(
    tempo.MetronomeMark(
        number=84
    )
)



for element in part.recurse():

    if isinstance(
        element,
        note.Note
    ):

        n = note.Note(
            element.pitch
        )

        n.duration = element.duration

        melody.append(
            n
        )


    elif isinstance(
        element,
        chord.Chord
    ):

        # 取最高音當旋律

        n = note.Note(
            element.sortAscending().notes[-1].pitch
        )

        n.duration = element.duration

        melody.append(
            n
        )



# ------------------------------------------------------------
# Build score
# ------------------------------------------------------------

print("建立4/4小節...")


out_score = stream.Score()


out_score.insert(
    0,
    melody
)



# ------------------------------------------------------------
# Remove bad durations
# ------------------------------------------------------------

for n in melody.notes:

    if n.duration.quarterLength <= 0:

        n.duration.quarterLength = 1



# ------------------------------------------------------------
# Export
# ------------------------------------------------------------

print("輸出 MusicXML...")


out_score.write(
    "musicxml",
    fp=output_file
)



print(
    "完成:",
    output_file
)


print(
    "========================================================"
)