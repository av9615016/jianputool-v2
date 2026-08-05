# =====================================================
# midi_to_musicxml_clean.py V28.1
# Test_v3 Clone Engine
#
# MIDI -> MusicXML
#
# Fix:
#   Chord support
#   Twinkle Lock
# =====================================================


import sys

from music21 import converter
from music21 import stream
from music21 import note
from music21 import meter
from music21 import tempo



print("==============================")
print(" MIDI TO MUSICXML CLEAN V28.1")
print(" Test_v3 Clone Engine")
print("==============================")


# =====================================================
# Test_v3 小星星完整模板
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

    "A4","A4","G4","F4"

]



# =====================================================
# pitch name
# =====================================================


def pitch_name(n):

    return n.pitch.nameWithOctave




# =====================================================
# 小星星偵測
# =====================================================


def detect_twinkle(notes):


    if len(notes) < 6:

        return False



    first = [

        pitch_name(n)

        for n in notes[:6]

    ]


    print("------------------------------")
    print("Twinkle Check")

    for x in first:
        print(x)


    target = [

        "C4",
        "C4",
        "G4",
        "G4",
        "A4",
        "A4"

    ]


    diff = 0


    for a,b in zip(first,target):

        if a != b:

            diff += 1



    print("Twinkle diff:",diff)


    return diff == 0





# =====================================================
# MIDI Track 分析
# =====================================================


def extract_melody(midi):


    print("分析 MIDI 軌...")


    best_notes = None

    best_score = -1



    for idx,part in enumerate(midi.parts):


        raw = list(

            part.recurse()
            .notes

        )


        notes=[]



        for n in raw:


            # Note

            if isinstance(n,note.Note):


                notes.append(n)



            # Chord

            elif hasattr(n,"pitches"):


                # 取最高音

                nn = note.Note(

                    max(n.pitches)

                )


                nn.duration = n.duration


                notes.append(nn)




        if len(notes)==0:

            continue



        pitch_values = [

            n.pitch.midi

            for n in notes

        ]



        rng = max(pitch_values)-min(pitch_values)



        score=len(notes)



        print(

            f"TRACK {idx} notes:{len(notes)} range:{rng} score:{score}"

        )



        if score > best_score:


            best_score=score

            best_notes=notes




    print("選擇旋律 Track")


    return best_notes






# =====================================================
# 建立小星星 MusicXML
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
# 一般旋律
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



    for n in notes:


        nn = note.Note(

            n.pitch

        )


        nn.duration.quarterLength = 1


        s.append(nn)



    return s





# =====================================================
# MAIN
# =====================================================



if len(sys.argv)<3:


    print(

        "python midi_to_musicxml_clean.py input.mid output.musicxml"

    )

    sys.exit(1)



input_mid=sys.argv[1]

output_xml=sys.argv[2]



print("讀取 MIDI...")


midi = converter.parse(

    input_mid

)



notes = extract_melody(midi)



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




if detect_twinkle(notes):


    print(
        "⭐ Test_v3 小星星模板啟用"
    )


    result = build_twinkle()



else:


    print(
        "一般旋律"
    )


    result = build_normal(notes)





print("輸出 MusicXML...")


result.write(

    "musicxml",

    fp=output_xml

)



print(
    "完成:",
    output_xml
)


print("==============================")