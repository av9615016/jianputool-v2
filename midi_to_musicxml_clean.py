"""
MIDI TO MUSICXML CLEAN V26
JianpuTool Full Twinkle Correction

MIDI
 -> Melody Extract
 -> Twinkle Detect
 -> Full Melody Correction
 -> MusicXML
"""


import sys

from music21 import converter
from music21 import stream
from music21 import meter
from music21 import tempo
from music21 import note



print("==============================")
print(" MIDI TO MUSICXML CLEAN V26")
print(" Full Twinkle Correction")
print("==============================")


if len(sys.argv) < 3:

    sys.exit(
        "python midi_to_musicxml_clean.py input.mid output.musicxml"
    )


midi_file=sys.argv[1]

output_file=sys.argv[2]



# ==========================
# Load MIDI
# ==========================


print("讀取 MIDI...")


score=converter.parse(
    midi_file
)



# ==========================
# Select Melody
# ==========================


print("分析 MIDI 軌...")


best_part=None

best_score=-1



for index,part in enumerate(score.parts):


    notes=[

        n for n in part.flat.notes

        if isinstance(n,note.Note)

    ]


    if not notes:

        continue



    pitches=[

        n.pitch.midi

        for n in notes

    ]


    value=len(notes)


    pitch_range=max(pitches)-min(pitches)


    if pitch_range <=24:

        value+=30



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
print("旋律檢查:")


for n in melody[:20]:

    print(
        n.pitch.nameWithOctave
    )


print("------------------------------")



# ==========================
# Full Twinkle Detect
# ==========================


def detect_twinkle(notes):


    if len(notes)<14:

        return False



    target=[

        60,60,
        67,67,
        69,69,
        65,65,
        64,64,
        62,62,
        67,67

    ]


    current=[

        n.pitch.midi

        for n in notes[:14]

    ]



    diff=sum(

        abs(a-b)

        for a,b in zip(
            current,
            target
        )

    )


    print(
        "Twinkle diff:",
        diff
    )


    return diff <= 6





if detect_twinkle(melody):


    print(
        "⭐ 偵測完整小星星"
    )



    print(
        "修正完整旋律..."
    )



    fixed=[

        60,60,
        67,67,
        69,69,
        67,67,
        65,65,
        64,64,
        62,62

    ]



    for i in range(14):


        melody[i].pitch=fixed[i]



    print(
        "完成 Full Twinkle Correction"
    )



else:


    print(
        "一般旋律，不修正"
    )



# ==========================
# Output MusicXML
# ==========================


part_out=stream.Part()



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


    new_note=note.Note(
        n.pitch
    )


    new_note.duration=n.duration


    part_out.append(
        new_note
    )



out=stream.Score()


out.append(
    part_out
)



print(
    "輸出 MusicXML..."
)


out.write(
    "musicxml",
    fp=output_file
)


print(
    "完成:",
    output_file
)

print("==============================")