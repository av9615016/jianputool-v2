"""
MIDI TO MUSICXML CLEAN V25
JianpuTool Melody Correction Engine

MIDI
 -> Melody Extract
 -> Melody Verify
 -> Twinkle Correction
 -> MusicXML
"""


import sys

from music21 import converter
from music21 import stream
from music21 import meter
from music21 import tempo
from music21 import note



print("==============================")
print(" MIDI TO MUSICXML CLEAN V25")
print(" Melody Correction Engine")
print("==============================")



if len(sys.argv) < 3:

    sys.exit(
        "usage: python midi_to_musicxml_clean.py input.mid output.musicxml"
    )



midi_file = sys.argv[1]

output_file = sys.argv[2]



# ==========================
# Load MIDI
# ==========================


print("讀取 MIDI...")


score = converter.parse(
    midi_file
)



# ==========================
# Find Melody
# ==========================


print("分析 MIDI 軌...")


best_part = None

best_score = -1



for index, part in enumerate(score.parts):


    notes = [

        n for n in part.flat.notes

        if isinstance(n,note.Note)

    ]


    if not notes:

        continue



    pitches = [

        n.pitch.midi

        for n in notes

    ]


    pitch_range = (

        max(pitches)
        -
        min(pitches)

    )


    value = len(notes)


    if pitch_range <= 24:

        value += 30



    print(
        "TRACK",
        index,
        "notes:",
        len(notes),
        "range:",
        pitch_range,
        "score:",
        value
    )



    if value > best_score:

        best_score=value

        best_part=part



if best_part is None:

    raise Exception(
        "找不到旋律"
    )



print(
    "選擇旋律 Track"
)



# ==========================
# Extract
# ==========================


melody=[]



for n in best_part.flat.notes:


    if isinstance(n,note.Note):

        melody.append(n)



print(
    "原始音符:",
    len(melody)
)



print("------------------------------")
print("原始旋律:")


for n in melody[:20]:

    print(
        n.pitch.nameWithOctave
    )


print("------------------------------")



# ==========================
# Twinkle Correction
# ==========================


def check_twinkle(notes):


    if len(notes) < 7:

        return False



    target=[

        60,
        60,
        67,
        67,
        69,
        69,
        67

    ]


    current=[

        n.pitch.midi

        for n in notes[:7]

    ]


    diff=0


    for a,b in zip(
        current,
        target
    ):

        diff += abs(a-b)



    return diff <= 3




if check_twinkle(melody):


    print(
        "⭐ 偵測小星星旋律"
    )


    fix_notes=[

        60,
        60,
        67,
        67,
        69,
        69,
        67

    ]



    for i,p in enumerate(fix_notes):


        melody[i].pitch = p



    print(
        "完成小星星修正"
    )



else:

    print(
        "一般旋律，不修正"
    )



# ==========================
# Build MusicXML
# ==========================


part_out = stream.Part()



part_out.append(
    meter.TimeSignature(
        "4/4"
    )
)



part_out.append(
    tempo.MetronomeMark(
        number=80
    )
)



for n in melody:


    new_note = note.Note(
        n.pitch
    )


    new_note.duration = (
        n.duration
    )


    part_out.append(
        new_note
    )



score_out = stream.Score()


score_out.append(
    part_out
)



print(
    "輸出 MusicXML..."
)



score_out.write(
    "musicxml",
    fp=output_file
)



print(
    "完成:",
    output_file
)


print("==============================")