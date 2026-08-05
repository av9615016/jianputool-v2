"""
MIDI TO MUSICXML CLEAN V21.1
JianpuTool Melody Lock Engine

MIDI -> Melody -> MusicXML
"""

import sys

from music21 import converter
from music21 import stream
from music21 import meter
from music21 import note
from music21 import tempo


print("==============================")
print(" MIDI TO MUSICXML CLEAN V21.1")
print(" Melody Lock Engine")
print("==============================")


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



# ==========================
# Load MIDI
# ==========================

print("讀取 MIDI...")


score = converter.parse(
    midi_file
)



# ==========================
# Select Melody Track
# ==========================


print("分析 MIDI 軌...")


best_part = None

best_value = -1



for index, part in enumerate(score.parts):


    notes = []


    for n in part.flat.notes:

        if isinstance(n, note.Note):

            notes.append(n)



    count = len(notes)


    if count == 0:

        continue



    pitches = [

        n.pitch.midi

        for n in notes

    ]


    pitch_range = (

        max(pitches)
        -
        min(pitches)

    )



    # 旋律評分

    value = (

        count
        +
        pitch_range * 2

    )



    print(
        "TRACK",
        index,
        "notes:",
        count,
        "range:",
        pitch_range
    )



    if value > best_value:

        best_value = value

        best_part = part




if best_part is None:

    raise Exception(
        "找不到 MIDI 旋律"
    )



print(
    "選擇旋律 Track"
)



# ==========================
# Extract Notes
# ==========================


melody = []


for n in best_part.flat.notes:


    if isinstance(n, note.Note):

        melody.append(n)



print(
    "原始音符:",
    len(melody)
)



# ==========================
# Remove exact duplicates
# ==========================


clean = []


last_pitch = None

last_offset = None



for n in melody:


    pitch = n.pitch.midi

    offset = round(
        n.offset,
        3
    )


    if (

        pitch == last_pitch

        and

        offset == last_offset

    ):

        continue



    clean.append(n)


    last_pitch = pitch

    last_offset = offset



print(
    "去重後:",
    len(clean)
)



# ==========================
# Build Melody Part
# ==========================


part_out = stream.Part()



part_out.append(
    meter.TimeSignature(
        "4/4"
    )
)



part_out.append(
    tempo.MetronomeMark(
        number=80
    )
)



for n in clean:


    new_note = note.Note(
        n.pitch
    )


    # 保持簡譜節奏穩定

    new_note.quarterLength = (
        1
    )


    part_out.append(
        new_note
    )



print(
    "保留旋律:",
    len(part_out.notes)
)



# ==========================
# Create Score
# ==========================


out_score = stream.Score()


out_score.append(
    part_out
)



# ==========================
# Export
# ==========================


print(
    "輸出 MusicXML..."
)



out_score.write(
    "musicxml",
    fp=output_file
)



print(
    "完成:",
    output_file
)


print("==============================")