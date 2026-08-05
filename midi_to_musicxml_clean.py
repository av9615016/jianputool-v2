# midi_to_musicxml_clean.py
#
# JianpuTool V33.1
#
# Vocal AI Melody Filter
# + Quantize Builder
#
# BasicPitch Vocal MIDI
#        |
#        v
# Vocal Filter
#        |
#        v
# Quantize
#        |
#        v
# 4/4 Measure Builder
#        |
#        v
# MusicXML


import sys

from music21 import converter
from music21 import stream
from music21 import note
from music21 import meter
from music21 import tempo
from music21 import instrument


# =========================
# Parameters
# =========================

LOW_PITCH = 48
HIGH_PITCH = 84

MIN_DURATION = 0.12

MAX_JUMP = 12


# =========================
# Quantize
# =========================

def quantize(value):

    grid = 0.25

    return round(
        value / grid
    ) * grid



# =========================
# Arguments
# =========================

if len(sys.argv) < 3:

    print(
        "python midi_to_musicxml_clean.py input.mid output.musicxml"
    )

    exit()


input_mid = sys.argv[1]
output_xml = sys.argv[2]



# =========================
# Read MIDI
# =========================

print("讀取 MIDI...")


midi = converter.parse(
    input_mid
)



raw = []


for n in midi.flatten().notes:

    if not isinstance(n, note.Note):
        continue


    raw.append(
        {
            "pitch": n.pitch.midi,
            "offset": float(n.offset),
            "duration": float(
                n.duration.quarterLength
            )
        }
    )


print(
    "原始音符:",
    len(raw)
)



# =========================
# Pitch Filter
# =========================

notes = []


for n in raw:

    if (
        LOW_PITCH
        <= n["pitch"]
        <= HIGH_PITCH
    ):

        notes.append(n)


print(
    "音域篩選:",
    len(notes)
)



# =========================
# Duration Filter
# =========================

notes2 = []


for n in notes:

    if n["duration"] >= MIN_DURATION:

        notes2.append(n)


print(
    "長度篩選:",
    len(notes2)
)



# =========================
# Sort
# =========================

notes2.sort(
    key=lambda x:x["offset"]
)



# =========================
# Melody Continuity
# =========================

melody = []


for n in notes2:


    if not melody:

        melody.append(n)

        continue



    last = melody[-1]


    jump = abs(
        n["pitch"]
        -
        last["pitch"]
    )


    if jump <= MAX_JUMP:

        melody.append(n)



print(
    "旋律連續:",
    len(melody)
)



# =========================
# Phrase Merge
# =========================

merged = []


for n in melody:


    n["duration"] = quantize(
        n["duration"]
    )


    if not merged:

        merged.append(n)

        continue



    last = merged[-1]


    same = (
        last["pitch"]
        ==
        n["pitch"]
    )


    distance = (
        n["offset"]
        -
        (
            last["offset"]
            +
            last["duration"]
        )
    )


    if same and distance <= 0.25:


        last["duration"] += n["duration"]


    else:

        merged.append(n)



print(
    "Phrase Merge:",
    len(merged)
)



# =========================
# Build Score
# =========================

print(
    "建立 MusicXML..."
)


score = stream.Score()


part = stream.Part()


part.insert(
    0,
    instrument.Instrument(
        "Vocal Melody"
    )
)


part.append(
    meter.TimeSignature("4/4")
)


part.insert(
    0,
    tempo.MetronomeMark(
        number=80
    )
)



current = 0



for n in merged:


    dur = n["duration"]


    if dur <= 0:

        continue



    nn = note.Note(
        n["pitch"]
    )


    nn.duration.quarterLength = dur


    part.insert(
        current,
        nn
    )


    current += dur



# =========================
# Fill 4/4 Measures
# =========================

score.append(part)


# make measures

score = score.makeMeasures(
    inPlace=False
)


score.write(
    "musicxml",
    fp=output_xml
)



print(
    "完成:",
    output_xml
)