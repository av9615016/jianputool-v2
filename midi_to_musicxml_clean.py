# ============================================================
# midi_to_musicxml_clean.py
#
# JianpuTool MVP 1.2
# MIDI -> Melody MusicXML
#
# V20 Melody Extraction Engine
#
# ============================================================

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


print("================ MIDI TO MUSICXML CLEAN V20 ================")


# ============================================================
# LOAD MIDI
# ============================================================

print("讀取 MIDI...")

score = converter.parse(INPUT)


print(
    "PARTS:",
    len(score.parts)
)


# ============================================================
# COLLECT NOTES
# ============================================================

print("分析音符...")


notes = []


for part in score.parts:

    for n in part.recurse().notes:

        if isinstance(n, note.Note):

            midi = n.pitch.midi


            # -------------------------
            # 移除低音伴奏
            # -------------------------

            if midi < 55:
                continue


            # -------------------------
            # 移除太高雜訊
            # -------------------------

            if midi > 96:
                continue


            notes.append(n)



print(
    "候選音符:",
    len(notes)
)



# ============================================================
# REMOVE DUPLICATE
# ============================================================

print("移除重複音...")


melody_notes = []


last_pitch = None


for n in notes:

    pitch = n.pitch.midi


    # 連續相同音只保留一次
    if pitch == last_pitch:
        continue


    melody_notes.append(n)

    last_pitch = pitch



print(
    "旋律音符:",
    len(melody_notes)
)



# ============================================================
# BUILD MELODY
# ============================================================


print("建立旋律...")


melody = stream.Part()


count = 0


for n in melody_notes:


    new_n = note.Note(
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



    # 保留常用節奏

    allowed = [
        4,
        2,
        1,
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
    "輸出音符:",
    count
)



# ============================================================
# FIX OCTAVE
# ============================================================


print("修正八度...")


for n in melody.recurse().notes:


    if n.pitch.octave < 3:

        n.pitch.octave = 3


    if n.pitch.octave > 6:

        n.pitch.octave = 6




# ============================================================
# TIME SIGNATURE
# ============================================================


print("建立4/4小節...")


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



# ============================================================
# MAKE MEASURES
# ============================================================


score2 = melody.makeMeasures(
    inPlace=False
)



# ============================================================
# FINAL CHECK
# ============================================================


print("檢查 duration...")


for n in score2.recurse().notes:


    if n.duration.type == "inexpressible":

        print(
            "修正:",
            n.pitch
        )


        n.duration = duration.Duration(
            0.25
        )



# ============================================================
# WRITE
# ============================================================


print("輸出 MusicXML...")


score2.write(
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