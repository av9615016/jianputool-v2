# midi_to_musicxml_clean.py
#
# JianpuTool
# MIDI -> MusicXML
# V20.2 SAFE SCORE ENGINE


import sys

from music21 import (
    converter,
    stream,
    note,
    meter,
    tempo,
    duration
)


INPUT = sys.argv[1]
OUTPUT = sys.argv[2]


print("==============================")
print(" MIDI TO MUSICXML CLEAN V20.2")
print("==============================")


# =========================
# LOAD MIDI
# =========================

print("讀取 MIDI...")

midi_score = converter.parse(INPUT)



# =========================
# SELECT MELODY PART
# =========================

print("選擇旋律軌...")


best_part = None
best_count = 0


for part in midi_score.parts:

    count = 0

    for n in part.recurse().notes:

        if isinstance(n, note.Note):
            count += 1


    if count > best_count:

        best_count = count
        best_part = part



if best_part is None:

    raise Exception(
        "找不到旋律"
    )


print(
    "原始音符:",
    best_count
)



# =========================
# CREATE MELODY PART
# =========================

melody = stream.Part()


melody.partName = "Melody"



melody.insert(
    0,
    meter.TimeSignature("4/4")
)


melody.insert(
    0,
    tempo.MetronomeMark(
        number=80
    )
)



count = 0



for n in best_part.recurse().notes:


    if not isinstance(n, note.Note):
        continue



    midi = n.pitch.midi


    # 去除低音
    if midi < 48:
        continue



    new_note = note.Note(
        n.pitch
    )



    ql = float(
        n.duration.quarterLength
    )


    if ql <= 0:
        continue



    if ql > 4:
        ql = 4



    # 節奏量化
    allowed = [

        4,
        2,
        1,
        0.5,
        0.25

    ]


    ql = min(
        allowed,
        key=lambda x:
        abs(x - ql)
    )


    new_note.duration = duration.Duration(
        ql
    )


    melody.append(
        new_note
    )


    count += 1



print(
    "保留音符:",
    count
)



# =========================
# OCTAVE LIMIT
# =========================

print(
    "限制音域..."
)


for n in melody.notes:


    if n.pitch.octave < 3:

        n.pitch.octave = 3


    if n.pitch.octave > 6:

        n.pitch.octave = 6




# =========================
# SCORE BUILD
# =========================

print(
    "建立 Score..."
)


score_out = stream.Score()


score_out.append(
    melody
)



# =========================
# MEASURE BUILD
# =========================

print(
    "建立4/4小節..."
)


final_score = score_out.makeMeasures(
    inPlace=False
)



# =========================
# CHECK MEASURE
# =========================

print(
    "檢查小節..."
)


for part in final_score.parts:

    for m in part.getElementsByClass(
        "Measure"
    ):

        print(
            "Measure",
            m.number,
            "duration=",
            m.duration.quarterLength
        )



# =========================
# WRITE
# =========================

print(
    "輸出 MusicXML..."
)


final_score.write(
    "musicxml",
    fp=OUTPUT
)



print(
    "完成:",
    OUTPUT
)

print("==============================")