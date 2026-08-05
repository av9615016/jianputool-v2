"""
MIDI TO MUSICXML CLEAN V22
JianpuTool Melody Extract Engine

MIDI
 -> Track Analysis
 -> Melody Extract
 -> MusicXML
"""


import sys

from music21 import converter
from music21 import stream
from music21 import meter
from music21 import tempo
from music21 import note



print("==============================")
print(" MIDI TO MUSICXML CLEAN V22")
print(" Melody Extract Engine")
print("==============================")



if len(sys.argv) < 3:

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
# Analyze Tracks
# ==========================


print("分析 MIDI 軌...")


candidates = []



for index, part in enumerate(score.parts):


    notes = []


    for n in part.flat.notes:

        if isinstance(n, note.Note):

            notes.append(n)



    if len(notes) == 0:

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


    unique_pitch = len(
        set(pitches)
    )



    # 旋律評分

    value = 0


    # 音符數

    value += min(
        len(notes),
        100
    )


    # 小音域旋律加分

    if pitch_range <= 24:

        value += 30



    # 音高種類少代表旋律

    if unique_pitch <= 15:

        value += 30



    print(
        "TRACK",
        index,
        "notes:",
        len(notes),
        "range:",
        pitch_range,
        "score:",
        value
    )



    candidates.append(
        (
            value,
            part
        )
    )



if not candidates:

    raise Exception(
        "找不到旋律 Track"
    )



# 最高分

best_part = sorted(
    candidates,
    key=lambda x:x[0],
    reverse=True
)[0][1]



print(
    "選擇旋律 Track"
)



# ==========================
# Extract Melody
# ==========================


melody = []


for n in best_part.flat.notes:


    if isinstance(n,note.Note):

        melody.append(n)



print(
    "原始音符:",
    len(melody)
)



# ==========================
# Remove Duplicate
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
    "清理後:",
    len(clean)
)



# ==========================
# Build Melody Part
# ==========================


out_part = stream.Part()



out_part.append(
    meter.TimeSignature(
        "4/4"
    )
)



out_part.append(
    tempo.MetronomeMark(
        number=80
    )
)



for n in clean:


    new_note = note.Note(
        n.pitch
    )


    # 保留原節奏

    new_note.duration = (
        n.duration
    )


    out_part.append(
        new_note
    )



print(
    "輸出音符:",
    len(out_part.notes)
)



# ==========================
# Score
# ==========================


out_score = stream.Score()


out_score.append(
    out_part
)



# ==========================
# Write
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