# midi_to_musicxml_clean.py
#
# JianpuTool V33
#
# Vocal AI Melody Filter
#
# BasicPitch Vocal MIDI
#        |
#        v
# Vocal AI Filter
#        |
#        v
# MusicXML
#

import sys
from music21 import converter
from music21 import stream
from music21 import note
from music21 import meter
from music21 import tempo
from music21 import instrument


# ==========================
# V33 Filter Parameters
# ==========================

LOW_PITCH = 48       # C3
HIGH_PITCH = 84      # C6

MIN_DURATION = 0.12

MAX_JUMP = 12        # 最大跳音


# ==========================
# Arguments
# ==========================

if len(sys.argv) < 3:
    print(
        "python midi_to_musicxml_clean.py input.mid output.musicxml"
    )
    exit()


input_mid = sys.argv[1]
output_xml = sys.argv[2]


# ==========================
# Read MIDI
# ==========================

print("讀取 MIDI...")

midi = converter.parse(
    input_mid
)


notes = []

for n in midi.flatten().notes:

    if not isinstance(n, note.Note):
        continue


    pitch = n.pitch.midi

    duration = float(
        n.duration.quarterLength
    )


    notes.append(
        {
            "pitch": pitch,
            "offset": float(n.offset),
            "duration": duration
        }
    )


print(
    "原始音符:",
    len(notes)
)


# ==========================
# Pitch Filter
# ==========================

filtered = []

for n in notes:

    if (
        LOW_PITCH
        <=
        n["pitch"]
        <=
        HIGH_PITCH
    ):
        filtered.append(n)


print(
    "音域篩選:",
    len(filtered)
)


# ==========================
# Duration Filter
# ==========================

filtered2 = []

for n in filtered:

    if n["duration"] >= MIN_DURATION:
        filtered2.append(n)


print(
    "長度篩選:",
    len(filtered2)
)



# ==========================
# Melody Continuity Filter
# ==========================

melody = []


for n in filtered2:

    if not melody:
        melody.append(n)
        continue


    last = melody[-1]


    jump = abs(
        n["pitch"]
        -
        last["pitch"]
    )


    # 太大跳音降低
    if jump > MAX_JUMP:

        continue


    melody.append(n)



print(
    "旋律連續:",
    len(melody)
)



# ==========================
# Phrase Merge
# ==========================

merged = []


for n in melody:

    if not merged:

        merged.append(n)
        continue


    last = merged[-1]


    same_pitch = (
        last["pitch"]
        ==
        n["pitch"]
    )


    end_time = (
        last["offset"]
        +
        last["duration"]
    )


    close = (
        n["offset"]
        -
        end_time
        <
        0.15
    )


    if same_pitch and close:

        last["duration"] = (
            n["offset"]
            +
            n["duration"]
            -
            last["offset"]
        )

    else:

        merged.append(n)



print(
    "Phrase Merge:",
    len(merged)
)



# ==========================
# Build MusicXML
# ==========================

print(
    "建立 MusicXML..."
)


score = stream.Score()


part = stream.Part()


inst = instrument.Instrument()

inst.instrumentName = (
    "Vocal Melody"
)

part.insert(
    0,
    inst
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



for n in merged:

    nn = note.Note(
        n["pitch"]
    )

    nn.offset = n["offset"]

    nn.duration.quarterLength = (
        n["duration"]
    )

    part.insert(
        nn.offset,
        nn
    )


score.append(part)



score.write(
    "musicxml",
    fp=output_xml
)


print(
    "完成:",
    output_xml
)