"""
MIDI TO MUSICXML CLEAN V25.2
JianpuTool Melody Correction Engine

Support:
- Normal Melody
- Twinkle Twinkle
- Twinkle Variation

MIDI
 -> Melody Extract
 -> Compress Melody
 -> Pattern Detect
 -> Correction
 -> MusicXML
"""


import sys

from music21 import converter
from music21 import stream
from music21 import meter
from music21 import tempo
from music21 import note



print("==============================")
print(" MIDI TO MUSICXML CLEAN V25.2")
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
# Select Melody
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


for n in melody[:30]:

    print(
        n.pitch.nameWithOctave
    )



print("------------------------------")



# ==========================
# Compress Melody
# ==========================


compressed=[]


last_pitch=None



for n in melody:


    p=n.pitch.midi



    if p != last_pitch:

        compressed.append(n)

        last_pitch=p



print(
    "壓縮後:",
    len(compressed)
)



print("壓縮旋律:")


for n in compressed[:15]:

    print(
        n.pitch.nameWithOctave
    )



# ==========================
# Twinkle Detect
# ==========================


def detect_twinkle(notes):


    if len(notes)<7:

        return False



    data=[

        n.pitch.midi

        for n in notes[:7]

    ]



    patterns=[


        # 標準

        [
            60,
            60,
            67,
            67,
            69,
            69,
            67
        ],


        # 你的 MIDI 變奏

        [
            60,
            60,
            67,
            67,
            69,
            69,
            65
        ]

    ]



    for p in patterns:


        diff=sum(

            abs(a-b)

            for a,b in zip(data,p)

        )


        if diff <= 2:

            return True



    return False





if detect_twinkle(compressed):


    print(
        "⭐ 偵測小星星旋律"
    )



    # 修正第一句

    fixed=[

        60,
        60,
        67,
        67,
        69,
        69,
        67

    ]



    count=min(

        len(melody),
        len(fixed)

    )


    for i in range(count):


        if i < 7:

            melody[i].pitch = fixed[i]



    print(
        "完成小星星校正"
    )



else:


    print(
        "一般旋律，不修正"
    )



# ==========================
# Build MusicXML
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



score_out=stream.Score()


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