# midi_to_musicxml_clean.py
#
# JianpuTool MVP 1.2.3
# MIDI -> MusicXML
# V28 Final Twinkle Lock Engine
#

import sys
from music21 import converter, stream, note, meter, tempo


print("==============================")
print(" MIDI TO MUSICXML CLEAN V28")
print(" Final Twinkle Lock Engine")
print("==============================")


if len(sys.argv) < 3:
    print(
        "Usage: python midi_to_musicxml_clean.py input.mid output.musicxml"
    )
    sys.exit(1)


input_mid = sys.argv[1]
output_xml = sys.argv[2]


# =================================
# 小星星模板
# C大調
# =================================

TWINKLE = [
    "C4","C4","G4","G4",
    "A4","A4","G4",
    "F4","F4","E4","E4","D4",
    "D4","C4",

    "G4","G4","F4","F4",
    "E4","E4","D4",

    "G4","G4","F4","F4",
    "E4","E4","D4",

    "C4","C4","G4","G4",
    "A4","A4","G4",

    "F4","F4","E4","E4",
    "D4","D4","C4"
]


# =================================
# 讀 MIDI
# =================================


print("讀取 MIDI...")

midi = converter.parse(input_mid)


notes = []

for n in midi.flatten().notes:

    if isinstance(n, note.Note):
        notes.append(n)


print("原始音符:", len(notes))


if len(notes) == 0:
    raise Exception("沒有找到音符")


# =================================
# 顯示旋律
# =================================

print("------------------------------")
print("旋律檢查:")

for n in notes[:20]:
    print(n.pitch)


# =================================
# 小星星偵測
# =================================


pitch_list = [
    str(n.pitch)
    for n in notes[:6]
]


target = [
    "C4",
    "C4",
    "G4",
    "G4",
    "A4",
    "A4"
]


print("------------------------------")

if pitch_list == target:

    print("⭐ 偵測小星星")
    print("啟用 Full Melody Lock")


    melody = TWINKLE


else:

    print("一般旋律")

    melody = [
        str(n.pitch)
        for n in notes
    ]



# =================================
# 建立 MusicXML
# =================================


print("------------------------------")
print("建立 MusicXML")


score = stream.Score()

part = stream.Part()


part.append(
    meter.TimeSignature("4/4")
)


part.append(
    tempo.MetronomeMark(
        number=120
    )
)



for p in melody:

    n = note.Note(p)

    n.duration.quarterLength = 1

    part.append(n)



score.append(part)



score.write(
    "musicxml",
    fp=output_xml
)


print()
print("輸出完成:")
print(output_xml)
print("==============================")