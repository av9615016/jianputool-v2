import sys

from music21 import (
    converter,
    stream,
    meter,
    tempo,
    note,
    duration
)


INPUT = sys.argv[1]
OUTPUT = sys.argv[2]


print("================ MIDI TO MUSICXML CLEAN V18 ================")


# =========================
# LOAD MIDI
# =========================

print("讀取 MIDI...")


score = converter.parse(INPUT)



# =========================
# 找最多音符 Part
# =========================

print("選擇旋律軌...")


src = None
max_count = 0


for p in score.parts:

    count = len(
        list(
            p.recurse().notes
        )
    )

    if count > max_count:

        max_count = count
        src = p


print(
    "notes:",
    max_count
)



# =========================
# 建立新 Part
# =========================

print("建立旋律...")


melody = stream.Part()


# 4/4

melody.append(
    meter.TimeSignature("4/4")
)


melody.append(
    tempo.MetronomeMark(
        number=80
    )
)



# =========================
# 保留節奏
# =========================

for n in src.recurse().notes:


    if not isinstance(n, note.Note):
        continue


    new_n = note.Note(
        n.pitch
    )


    # 保留原始長度

    ql = float(
        n.duration.quarterLength
    )


    if ql <= 0:
        continue


    # 量化

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
        abs(x-ql)
    )


    new_n.duration = duration.Duration(
        ql
    )


    # 關鍵：
    # 保留時間位置

    new_n.offset = n.offset


    melody.insert(
        n.offset,
        new_n
    )



# =========================
# 小節
# =========================

print("建立4/4小節...")


result = stream.Score()

result.append(
    melody.makeMeasures()
)



# =========================
# OUTPUT
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

print(
"========================================================"
)