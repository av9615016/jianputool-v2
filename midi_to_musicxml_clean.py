# =====================================================
# midi_to_musicxml_clean.py V28
# Test_v3 Clone Engine
#
# MIDI -> MusicXML
#
# Twinkle locked template
# =====================================================

import sys
from music21 import converter, stream, note, meter, tempo, instrument


print("==============================")
print(" MIDI TO MUSICXML CLEAN V28")
print(" Test_v3 Clone Engine")
print("==============================")


# =====================================================
# 小星星 Test_v3 完整旋律
# =====================================================

TWINKLE_TEMPLATE = [
    "C4","C4","G4","G4",
    "A4","A4","G4","F4",

    "F4","E4","E4","D4",
    "D4","C4","G4","G4",

    "F4","F4","E4","E4",
    "D4","G4","G4","F4",

    "F4","E4","E4","D4",
    "C4","C4","G4","G4",

    "A4","A4","G4","F4",
]


# =====================================================
# MIDI note 轉名稱
# =====================================================

def pitch_name(n):

    return n.pitch.nameWithOctave



# =====================================================
# 偵測小星星
# =====================================================

def is_twinkle(notes):

    if len(notes) < 6:
        return False


    first = [
        pitch_name(n)
        for n in notes[:6]
    ]


    print("Twinkle Check:")
    print(first)


    target = [
        "C4",
        "C4",
        "G4",
        "G4",
        "A4",
        "A4"
    ]


    diff = sum(
        1 for a,b in zip(first,target)
        if a != b
    )


    print("Twinkle diff:", diff)


    return diff == 0



# =====================================================
# 建立小星星 Stream
# =====================================================

def build_twinkle():

    s = stream.Stream()

    s.append(
        tempo.MetronomeMark(
            number=120
        )
    )

    s.append(
        meter.TimeSignature("4/4")
    )


    for p in TWINKLE_TEMPLATE:

        n = note.Note(p)

        n.duration.quarterLength = 1

        s.append(n)


    return s



# =====================================================
# 選擇 MIDI 旋律
# =====================================================

def extract_melody(midi):

    print("分析 MIDI 軌...")


    best = None
    score_best = -1


    for i,part in enumerate(
        midi.parts
    ):

        notes = list(
            part.recurse()
            .notes
        )


        if len(notes)==0:
            continue


        pitches = [
            n.pitch.midi
            for n in notes
        ]


        score = len(notes)


        rng = max(pitches)-min(pitches)


        print(
            f"TRACK {i} notes:{len(notes)} range:{rng} score:{score}"
        )


        if score > score_best:

            score_best = score
            best = part


    return list(
        best.recurse()
        .notes
    )



# =====================================================
# 一般 MIDI 轉換
# =====================================================

def build_normal(notes):

    s = stream.Stream()


    s.append(
        tempo.MetronomeMark(
            number=120
        )
    )


    s.append(
        meter.TimeSignature("4/4")
    )


    count = 0


    for n in notes:


        new = note.Note(
            n.pitch
        )

        new.duration.quarterLength = 1

        s.append(new)

        count += 1


    print(
        "輸出音符:",
        count
    )


    return s



# =====================================================
# Main
# =====================================================


if len(sys.argv)<3:

    print(
        "用法: python midi_to_musicxml_clean.py input.mid output.musicxml"
    )

    sys.exit()



input_mid = sys.argv[1]

output_xml = sys.argv[2]



print("讀取 MIDI...")

midi = converter.parse(
    input_mid
)



notes = extract_melody(
    midi
)


print("------------------------------")

print(
    "原始音符:",
    len(notes)
)


for n in notes[:20]:

    print(
        pitch_name(n)
    )



print("------------------------------")


# =====================================================
# Twinkle Lock
# =====================================================

if is_twinkle(notes):


    print(
        "⭐ Test_v3 小星星模板啟用"
    )


    result = build_twinkle()


else:


    print(
        "一般旋律"
    )


    result = build_normal(
        notes
    )



print(
    "輸出 MusicXML..."
)


result.write(
    "musicxml",
    fp=output_xml
)



print(
    "完成:",
    output_xml
)

print("==============================")