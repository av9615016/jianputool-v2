"""
MIDI TO MUSICXML CLEAN V23
JianpuTool Melody Verify Engine

功能:
1. 分析 MIDI Track
2. 抽取主旋律
3. 顯示音符
4. 小星星檢查
5. 輸出 MusicXML
"""


import sys

from music21 import converter
from music21 import stream
from music21 import meter
from music21 import tempo
from music21 import note



print("==============================")
print(" MIDI TO MUSICXML CLEAN V23")
print(" Melody Verify Engine")
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
# Track Analysis
# ==========================


print("分析 MIDI 軌...")


tracks = []



for index, part in enumerate(score.parts):


    notes = []


    for n in part.flat.notes:


        if isinstance(n, note.Note):

            notes.append(n)



    if not notes:

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



    unique = len(
        set(pitches)
    )


    # 旋律評分

    score_value = 0


    score_value += min(
        len(notes),
        100
    )


    if pitch_range <= 24:

        score_value += 30


    if unique <= 15:

        score_value += 30



    print(
        "TRACK",
        index,
        "notes:",
        len(notes),
        "range:",
        pitch_range,
        "score:",
        score_value
    )


    tracks.append(
        (
            score_value,
            part
        )
    )



if not tracks:

    raise Exception(
        "沒有找到 MIDI 音符"
    )



best_part = sorted(
    tracks,
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
# Print Melody
# ==========================


print("------------------------------")
print("旋律音符檢查:")


for n in melody[:50]:


    print(
        n.pitch.nameWithOctave
    )


print("------------------------------")



# ==========================
# Twinkle Check
# ==========================


twinkle = [

    "C4",
    "C4",
    "G4",
    "G4",
    "A4",
    "A4",
    "G4",

]


test = [

    n.pitch.nameWithOctave

    for n in melody[:7]

]



if test == twinkle:

    print(
        "⭐ 偵測到小星星旋律!"
    )

else:

    print(
        "⚠ 不是標準小星星開頭"
    )



# ==========================
# Remove duplicate
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
# Build MusicXML
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


    # 保留原節奏

    new_note.duration = (
        n.duration
    )


    part_out.append(
        new_note
    )



print(
    "輸出音符:",
    len(part_out.notes)
)



score_out = stream.Score()


score_out.append(
    part_out
)



print(
    "輸出 MusicXML..."
)



score_out.write(
    "musicxml",
    fp=output_file
)



print(
    "完成:",
    output_file
)


print("==============================")