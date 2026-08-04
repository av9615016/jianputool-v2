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


print("===== V18 SAFE REBUILD ENGINE =====")


# =========================
# LOAD
# =========================

print("load musicxml")

score = converter.parse(INPUT)



# =========================
# CREATE NEW SCORE
# =========================

new_score = stream.Score()



# =========================
# EXTRACT MELODY
# =========================

print("extract melody")


src = score.parts[0]

melody = stream.Part()


count = 0


for n in src.recurse().notes:

    if isinstance(n, note.Note):

        new_n = note.Note(
            n.pitch
        )


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
            0.25
        ]


        closest = min(
            allowed,
            key=lambda x: abs(x-ql)
        )


        new_n.duration = duration.Duration(
            closest
        )


        melody.append(
            new_n
        )


        count += 1



print(
    "notes:",
    count
)



# =========================
# OCTAVE FIX
# =========================

print(
    "limit octave"
)


for n in melody.recurse().notes:

    if n.pitch.octave < 2:
        n.pitch.octave = 2


    if n.pitch.octave > 6:
        n.pitch.octave = 6




# =========================
# HEADER
# =========================

print(
    "force 4/4"
)


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



# =========================
# MEASURE
# =========================

print(
    "rebuild measures"
)


melody = melody.makeMeasures()



# 加入 Score

new_score.append(
    melody
)



# =========================
# WRITE
# =========================

print(
    "WRITE:",
    OUTPUT
)


new_score.write(
    "musicxml",
    fp=OUTPUT
)


print(
    "DONE"
)