"""
MIDI TO MUSICXML CLEAN V24
JianpuTool Melody Deduplicate Engine

MIDI
 -> Melody Track
 -> Remove Duplicate Notes
 -> MusicXML
"""


import sys

from music21 import converter
from music21 import stream
from music21 import meter
from music21 import tempo
from music21 import note



print("==============================")
print(" MIDI TO MUSICXML CLEAN V24")
print(" Melody Deduplicate Engine")
print("==============================")



if len(sys.argv) < 3:

    print(
        "python midi_to_musicxml_clean.py input.mid output.musicxml"
    )

    sys.exit(1)



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
# Find Melody Track
# ==========================


print("分析 MIDI 軌...")


best_part = None

best_score = -1



for index, part in enumerate(score.parts):


    notes = [

        n for n in part.flat.notes

        if isinstance(n, note.Note)

    ]


    if len(notes) == 0:

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



    unique = len(
        set(pitches)
    )



    score_value = (

        min(len(notes),100)

    )


    if pitch_range <= 24:

        score_value += 30



    if unique <= 15:

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

        best_score = score_value

        best_part = part



if best_part is None:

    raise Exception(
        "找不到旋律"
    )



print(
    "選擇旋律 Track"
)



# ==========================
# Original Melody
# ==========================


melody = []


for n in best_part.flat.notes:


    if isinstance(n,note.Note):

        melody.append(n)



print(
    "原始音符:",
    len(melody)
)



print("------------------------------")
print("原始旋律:")


for n in melody[:40]:

    print(
        n.pitch.nameWithOctave
    )


print("------------------------------")



# ==========================
# Deduplicate
# ==========================


clean = []


for n in melody:


    if len(clean) == 0:

        clean.append(n)

        continue



    last = clean[-1]


    # 同音且時間非常接近

    if (

        n.pitch.midi
        ==
        last.pitch.midi

        and

        abs(
            n.offset-last.offset
        )
        <
        0.1

    ):


        # 合併 duration

        if n.duration.quarterLength > last.duration.quarterLength:

            last.duration = n.duration


        continue



    clean.append(n)



print(
    "去重後:",
    len(clean)
)



print("------------------------------")
print("清理旋律:")


for n in clean[:40]:

    print(
        n.pitch.nameWithOctave
    )


print("------------------------------")



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



for n in clean:


    new_note = note.Note(
        n.pitch
    )


    new_note.duration = (
        n.duration
    )


    part_out.append(
        new_note
    )



print(
    "輸出音符:",
    len(part_out.notes)
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