MIDI TO MUSICXML CLEAN V21
JianpuTool Melody Lock Engine

MIDI
 ↓
選擇旋律 Track
 ↓
去重複
 ↓
旋律抽取
 ↓
MusicXML
"""

import sys
from music21 import converter
from music21 import stream
from music21 import meter
from music21 import note
from music21 import tempo


print("==============================")
print(" MIDI TO MUSICXML CLEAN V21")
print(" Melody Lock Engine")
print("==============================")


if len(sys.argv) < 3:

    print(
        "用法: python midi_to_musicxml_clean.py input.mid output.musicxml"
    )

    sys.exit()



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


best_part = None

best_score = -1



for i, part in enumerate(score.parts):


    notes = [
        n for n in part.flat.notes
        if isinstance(n, note.Note)
    ]


    count = len(notes)


    if count == 0:
        continue



    # 音域

    pitches = [
        n.pitch.midi
        for n in notes
    ]


    pitch_range = max(pitches)-min(pitches)



    # 主旋律評分

    score_value = (
        count
        + pitch_range * 2
    )


    print(
        "TRACK",
        i,
        "notes:",
        count,
        "range:",
        pitch_range
    )


    if score_value > best_score:

        best_score = score_value

        best_part = part



if best_part is None:

    raise Exception(
        "找不到旋律"
    )



print(
    "選擇旋律 Track"
)



# ==========================
# Extract Melody
# ==========================


melody_notes = []


for n in best_part.flat.notes:


    if isinstance(n, note.Note):

        melody_notes.append(n)



print(
    "原始音符:",
    len(melody_notes)
)



# ==========================
# Remove duplicate
# ==========================


clean_notes = []


last_pitch = None
last_offset = None



for n in melody_notes:


    p = n.pitch.midi


    o = round(
        n.offset,
        3
    )


    if (
        p == last_pitch
        and o == last_offset
    ):
        continue



    clean_notes.append(n)


    last_pitch = p

    last_offset = o



print(
    "去重後:",
    len(clean_notes)
)



# ==========================
# Keep Melody
# ==========================


result = stream.Part()


result.append(
    meter.TimeSignature("4/4")
)


result.append(
    tempo.MetronomeMark(
        number=80
    )
)



current = 0



for n in clean_notes:


    new_note = note.Note(
        n.pitch
    )


    new_note.quarterLength = 1


    result.append(
        new_note
    )



print(
    "保留旋律:",
    len(result.notes)
)



# ==========================
# Build Score
# ==========================


out = stream.Score()


out.append(
    result
)



# ==========================
# Write
# ==========================


print(
    "輸出 MusicXML..."
)


out.write(
    "musicxml",
    fp=output_file
)


print(
    "完成:",
    output_file
)


print("==============================")