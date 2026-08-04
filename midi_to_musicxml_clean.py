# midi_to_musicxml_clean.py
#
# JianpuTool
# MIDI -> MusicXML
# V20.3 Jianpu Safe Pitch Engine


import sys

from music21 import (
    converter,
    stream,
    note,
    meter,
    tempo,
    duration,
    clef,
    key
)


INPUT = sys.argv[1]
OUTPUT = sys.argv[2]


print("==============================")
print(" MIDI TO MUSICXML CLEAN V20.3")
print(" Jianpu Safe Pitch Engine")
print("==============================")


# =========================
# LOAD
# =========================

print("讀取 MIDI...")

src_score = converter.parse(INPUT)



# =========================
# SELECT PART
# =========================

print("選擇旋律軌...")


best_part = None
best_count = 0


for p in src_score.parts:

    c = 0

    for n in p.recurse().notes:

        if isinstance(n, note.Note):
            c += 1


    if c > best_count:
        best_count = c
        best_part = p



if best_part is None:
    raise Exception(
        "找不到音符"
    )


print(
    "原始音符:",
    best_count
)



# =========================
# BUILD PART
# =========================

melody = stream.Part()

melody.partName = "Melody"


# 音樂資訊

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


melody.insert(
    0,
    clef.TrebleClef()
)


melody.insert(
    0,
    key.Key("C")
)



count = 0



for n in best_part.recurse().notes:


    if not isinstance(n, note.Note):
        continue


    midi_num = n.pitch.midi


    # 去除極低雜訊
    if midi_num < 48:
        continue



    new_n = note.Note()


    # 保留原 MIDI pitch
    new_n.pitch.midi = midi_num



    ql = float(
        n.duration.quarterLength
    )


    if ql <= 0:
        continue


    if ql > 4:
        ql = 4



    # 比 V20.2 保留更多節奏

    allowed = [

        4,
        2,
        1,
        0.75,
        0.5,
        0.25,
        0.125

    ]


    closest = min(
        allowed,
        key=lambda x:
        abs(x - ql)
    )


    new_n.duration = duration.Duration(
        closest
    )


    melody.append(
        new_n
    )


    count += 1



print(
    "保留音符:",
    count
)



# =========================
# PITCH CHECK
# =========================

print("================")
print("Pitch Check")
print("================")


for n in melody.notes:

    print(
        n.pitch,
        n.pitch.midi
    )



# =========================
# BUILD SCORE
# =========================


score_out = stream.Score()


score_out.append(
    melody
)



# =========================
# MAKE MEASURES
# =========================

print(
    "建立4/4小節..."
)


final_score = score_out.makeMeasures(
    inPlace=False
)



# =========================
# MEASURE CHECK
# =========================

print(
    "Measure Check"
)


for p in final_score.parts:

    for m in p.getElementsByClass(
        "Measure"
    ):

        print(
            "Measure",
            m.number,
            "=",
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