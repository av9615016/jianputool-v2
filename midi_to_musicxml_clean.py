# midi_to_musicxml_clean.py
#
# JianpuTool
# MIDI -> MusicXML
# V19 Melody Preserve Engine
#

import sys

from music21 import (
    converter,
    stream,
    note,
    chord,
    meter,
    tempo,
    duration
)



INPUT = sys.argv[1]
OUTPUT = sys.argv[2]


print("================ MIDI TO MUSICXML CLEAN V19 ================")


# =========================
# LOAD MIDI
# =========================

print("讀取 MIDI...")

score = converter.parse(INPUT)



# =========================
# EXTRACT NOTES
# =========================

print("抽取旋律...")


events = []


for element in score.flatten().notesAndRests:


    # Note
    if isinstance(element, note.Note):

        events.append(
            element
        )


    # Chord
    elif isinstance(element, chord.Chord):

        # 取最高音當旋律
        highest = max(
            element.notes,
            key=lambda x:x.pitch.midi
        )

        events.append(
            highest
        )



print(
    "旋律音符:",
    len(events)
)



# =========================
# BUILD MELODY
# =========================


print("建立旋律...")


melody = stream.Part()


# 4/4
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



for n in events:


    new_n = note.Note(
        n.pitch
    )


    ql = float(
        n.duration.quarterLength
    )


    if ql <= 0:
        continue


    # MIDI 常見量化
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
        key=lambda x:abs(x-ql)
    )


    new_n.duration = duration.Duration(
        ql
    )


    melody.append(
        new_n
    )



# =========================
# OCTAVE LIMIT
# =========================

print("修正音域...")


for n in melody.notes:

    if n.pitch.octave < 3:

        n.pitch.octave = 3


    if n.pitch.octave > 6:

        n.pitch.octave = 6



# =========================
# MAKE MEASURES
# =========================

print("建立4/4小節...")


result = melody.makeMeasures(
    inPlace=False
)



# =========================
# WRITE
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