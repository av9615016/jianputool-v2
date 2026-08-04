# midi_to_musicxml_clean.py
#
# JianpuTool
# MIDI -> MusicXML
# V20.4 Jianpu PDF Clean Engine


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
print(" MIDI TO MUSICXML CLEAN V20.4")
print(" Jianpu PDF Clean Engine")
print("==============================")


# =========================
# LOAD MIDI
# =========================

print("讀取 MIDI...")

src = converter.parse(INPUT)



# =========================
# SELECT MELODY
# =========================

print("選擇旋律軌...")


best = None
max_notes = 0


for p in src.parts:

    c = len(
        list(
            p.recurse().notes
        )
    )


    if c > max_notes:

        max_notes = c
        best = p



if best is None:
    raise Exception(
        "無旋律"
    )


print(
    "原始音符:",
    max_notes
)



# =========================
# CREATE PART
# =========================

part = stream.Part()

part.partName = "Melody"


part.insert(
    0,
    meter.TimeSignature("4/4")
)


part.insert(
    0,
    tempo.MetronomeMark(
        number=80
    )
)


part.insert(
    0,
    clef.TrebleClef()
)


part.insert(
    0,
    key.Key("C")
)



count = 0



# =========================
# COPY NOTES ONLY
# =========================

for n in best.recurse().notes:


    if not isinstance(n, note.Note):
        continue


    midi = n.pitch.midi


    if midi < 48:
        continue



    new = note.Note()

    new.pitch.midi = midi



    ql = float(
        n.duration.quarterLength
    )


    if ql <= 0:
        continue



    if ql > 4:
        ql = 4



    allowed = [

        4,
        2,
        1,
        0.5,
        0.25,
        0.125

    ]


    ql = min(
        allowed,
        key=lambda x:
        abs(x-ql)
    )



    new.duration = duration.Duration(
        ql
    )


    part.append(
        new
    )


    count += 1



print(
    "保留音符:",
    count
)



# =========================
# SCORE
# =========================

score = stream.Score()

score.append(
    part
)



# =========================
# MAKE MEASURE
# =========================

print(
    "建立小節..."
)


score = score.makeMeasures(
    inPlace=False
)



# =========================
# CLEAN MEASURES
# =========================

print(
    "清理 MusicXML..."
)


for p in score.parts:

    for m in p.getElementsByClass(
        "Measure"
    ):


        # 移除 barline 資訊
        m.leftBarline = None
        m.rightBarline = None



        # 移除空休止
        for r in list(
            m.recurse().getElementsByClass("Rest")
        ):

            m.remove(r)



# =========================
# FINAL CHECK
# =========================

print(
    "Final notes:"
)


for n in score.recurse().notes:

    print(
        n.pitch,
        n.pitch.midi
    )



# =========================
# WRITE
# =========================

print(
    "輸出 MusicXML..."
)


score.write(
    "musicxml",
    fp=OUTPUT
)


print(
    "完成:",
    OUTPUT
)


print("==============================")