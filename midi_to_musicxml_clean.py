import sys
import os
from music21 import converter, stream, note, chord, meter, tempo


print("================ MIDI TO MUSICXML CLEAN V2 ================")


if len(sys.argv) < 3:
    print(
        "使用方式: python midi_to_musicxml_clean.py input.mid output.musicxml"
    )
    sys.exit(1)


midi_file = sys.argv[1]
output_file = sys.argv[2]


if not os.path.exists(midi_file):
    raise Exception(
        f"MIDI not found: {midi_file}"
    )


# =========================
# Load MIDI
# =========================

print("讀取 MIDI...")

score = converter.parse(
    midi_file
)


# =========================
# 分析 Part
# =========================

print("\n分析 MIDI 軌道...")


best_part = None
best_count = 0


for i, p in enumerate(score.parts):

    notes = list(
        p.flat.notes
    )

    count = len(notes)

    print(
        "PART",
        i,
        "name=",
        p.partName,
        "notes=",
        count
    )


    if count > best_count:

        best_count = count
        best_part = p



if best_part is None:

    raise Exception(
        "找不到 MIDI 音符"
    )


print(
    "\n選擇 Part:",
    best_part.partName,
    "notes:",
    best_count
)



# =========================
# 建立新旋律
# =========================

print("抽取旋律...")


melody = stream.Part()


melody.insert(
    0,
    meter.TimeSignature("4/4")
)


# tempo

melody.insert(
    0,
    tempo.MetronomeMark(
        number=80
    )
)



for n in best_part.flat.notes:


    # 和弦只取最高音

    if isinstance(
        n,
        chord.Chord
    ):

        new_note = note.Note(
            n.pitches[-1]
        )

        new_note.duration = n.duration


    elif isinstance(
        n,
        note.Note
    ):

        new_note = note.Note(
            n.pitch
        )

        new_note.duration = n.duration


    else:

        continue



    melody.append(
        new_note
    )



# =========================
# 建立 Score
# =========================

new_score = stream.Score()


new_score.append(
    melody
)



# =========================
# 修正小節
# =========================

print("建立4/4小節...")


new_score.makeMeasures(
    inPlace=True
)


# =========================
# 輸出
# =========================

print("輸出 MusicXML...")


new_score.write(
    "musicxml",
    fp=output_file
)


print(
    "完成:",
    output_file
)


print(
    "========================================================"
)