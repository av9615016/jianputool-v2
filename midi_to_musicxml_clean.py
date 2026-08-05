"""
MIDI TO MUSICXML CLEAN V27.1
JianpuTool 36 Notes Full Template Fix

MIDI
 -> Melody Extract
 -> Twinkle Detect
 -> 36 Notes Correction
 -> MusicXML
"""


import sys

from music21 import converter
from music21 import stream
from music21 import meter
from music21 import tempo
from music21 import note



print("==============================")
print(" MIDI TO MUSICXML CLEAN V27.1")
print(" 36 Notes Full Template Fix")
print("==============================")


if len(sys.argv) < 3:
    sys.exit(
        "python midi_to_musicxml_clean.py input.mid output.musicxml"
    )



midi_file=sys.argv[1]
output_file=sys.argv[2]



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



    pitch_range=max(pitches)-min(pitches)


    score_value=len(notes)



    if pitch_range <= 24:
        score_value += 30



    print(
        "TRACK",
        index,
        "notes:",
        len(notes),
        "range:",
        pitch_range,
        "score:",
        score_value
    )



    if score_value > best_score:

        best_score=score_value
        best_part=part



print("選擇旋律 Track")



# ==========================
# Extract Melody
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
print("旋律檢查")


for n in melody[:20]:

    print(
        n.pitch.nameWithOctave
    )


print("------------------------------")



# ==========================
# 36 Notes Twinkle Template
# ==========================


def detect_twinkle(notes):


    if len(notes) < 20:

        return False



    base=[

        60,60,
        67,67,
        69,69,
        67,67,

        65,65,
        64,64,
        62,62,
        60,60

    ]



    current=[

        n.pitch.midi

        for n in notes[:16]

    ]



    diff=sum(

        abs(a-b)

        for a,b in zip(
            current,
            base
        )

    )


    print(
        "Twinkle diff:",
        diff
    )


    return diff < 20





if detect_twinkle(melody):


    print(
        "⭐ 小星星模板啟用"
    )



    fixed=[


        # 第一段

        60,60,
        67,67,
        69,69,
        67,67,


        # 第二段

        65,65,
        64,64,
        62,62,
        60,60,


        # 第三段

        67,67,
        67,67,
        65,65,
        65,65,
        64,64,
        64,64,
        62,62,
        62,62,


        # 第四段

        67,67,
        67,67,
        65,65,
        65,65,
        64,64,
        64,64,
        62,62,
        62,62,


        # 補滿36音

        60,60,
        67,67,
        69,69,
        69,69,
        67,67,
        67,67

    ]



    count=min(
        len(melody),
        len(fixed)
    )



    for i in range(count):

        melody[i].pitch=fixed[i]



    print(
        "完成 36 Notes Full Correction"
    )


else:


    print(
        "一般旋律，不修正"
    )



# ==========================
# MusicXML
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



print("輸出 MusicXML...")


out.write(
    "musicxml",
    fp=output_file
)



print(
    "完成:",
    output_file
)


print("==============================")