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
print(" MIDI TO MUSICXML CLEAN V20.1")
print("==============================")


# =========================
# LOAD MIDI
# =========================

print("讀取 MIDI...")

score = converter.parse(INPUT)


# =========================
# 找旋律軌
# =========================

print("選擇旋律軌...")


best = None
best_count = 0


for p in score.parts:

    c = 0

    for n in p.recurse().notes:

        if isinstance(n, note.Note):
            c += 1


    if c > best_count:
        best = p
        best_count = c



if best is None:
    raise Exception("沒有找到音符")


print("原始音符:", best_count)



# =========================
# BUILD MELODY
# =========================

melody = stream.Part()


melody.insert(
    0,
    meter.TimeSignature("4/4")
)


melody.insert(
    0,
    tempo.MetronomeMark(number=80)
)



count = 0



for n in best.recurse().notes:


    if not isinstance(n, note.Note):
        continue


    midi = n.pitch.midi


    # 去除低音雜訊
    if midi < 48:
        continue


    # 複製音符
    new = note.Note(
        n.pitch
    )


    ql = float(
        n.duration.quarterLength
    )


    if ql <= 0:
        continue


    # 最大4拍
    if ql > 4:
        ql = 4



    # 四分音符量化
    allowed = [
        4,
        2,
        1,
        0.5,
        0.25
    ]


    ql = min(
        allowed,
        key=lambda x:abs(x-ql)
    )


    new.duration = duration.Duration(
        ql
    )


    melody.append(new)


    count += 1



print(
    "保留音符:",
    count
)



# =========================
# OCTAVE LIMIT
# =========================


for n in melody.notes:

    if n.pitch.octave < 3:
        n.pitch.octave = 3


    if n.pitch.octave > 6:
        n.pitch.octave = 6



# =========================
# MAKE MEASURES
# =========================


print("建立小節...")


result = melody.makeMeasures(
    inPlace=False
)



# =========================
# FINAL CHECK
# =========================


print("檢查...")


for m in result.parts[0].getElementsByClass("Measure"):

    q = float(
        m.duration.quarterLength
    )

    print(
        "Measure",
        m.number,
        q
    )



# =========================
# SAVE
# =========================


print("輸出 MusicXML...")


result.write(
    "musicxml",
    fp=OUTPUT
)


print(
    "完成:",
    OUTPUT
)