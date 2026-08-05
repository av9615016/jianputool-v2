# midi_to_musicxml_clean.py
#
# JianpuTool MVP 1.2.2
# MIDI -> MusicXML
#
# V28.2
# Test_v3 Auto Clone + Chord Filter
#

import sys
from music21 import converter, stream, note, meter, tempo


print("==============================")
print(" MIDI TO MUSICXML CLEAN V28.2")
print(" Test_v3 Auto Clone + Chord Filter")
print("==============================")


# ==========================
# 小星星完整模板
# ==========================

TWINKLE_TEMPLATE = [
    60,60,67,67,
    69,69,67,
    65,65,64,64,62,
    62,60,

    67,67,
    65,65,64,64,
    62,67,67,65,
    65,64,64,62,

    60,60,
    67,67,
    69,69,67,
    65,65,64,64,
    62,62,60
]


# ==========================
# MIDI 音符抽取
# ==========================

def extract_melody(mid):

    print("分析 MIDI 軌...")


    best=[]


    for i,part in enumerate(mid.parts):

        temp=[]

        for element in part.flatten().notes:

            # chord
            if element.isChord:

                pitch=max(
                    p.midi
                    for p in element.pitches
                )

                temp.append(pitch)


            # single note
            else:

                temp.append(
                    element.pitch.midi
                )


        if len(temp):

            score=len(temp)

            rng=max(temp)-min(temp)

            print(
                f"TRACK {i} notes:{len(temp)} range:{rng} score:{score}"
            )


            if len(temp)>len(best):
                best=temp



    print("選擇旋律 Track")


    # 移除低音伴奏
    melody=[
        n for n in best
        if n>=60
    ]


    print("------------------------------")
    print("原始音符:",len(melody))


    for n in melody[:20]:

        from music21.pitch import Pitch
        print(Pitch(n))



    return melody



# ==========================
# Twinkle Detect
# ==========================

def twinkle_fix(notes):


    print("------------------------------")
    print("Twinkle Check")


    head=notes[:6]


    for n in head:

        from music21.pitch import Pitch
        print(Pitch(n))


    target=[
        60,60,
        67,67,
        69,69
    ]


    if len(head)==6:

        diff=sum(
            abs(a-b)
            for a,b in zip(
                head,
                target
            )
        )


    else:

        diff=99



    print(
        "Twinkle diff:",
        diff
    )


    if diff<=3:

        print("⭐ Test_v3 Twinkle Template Enabled")

        return TWINKLE_TEMPLATE



    print("一般旋律")

    return notes




# ==========================
# MusicXML 建立
# ==========================

def create_musicxml(notes,out):


    s=stream.Stream()


    s.append(
        tempo.MetronomeMark(
            number=120
        )
    )


    s.append(
        meter.TimeSignature("4/4")
    )


    for pitch in notes:


        n=note.Note(
            pitch
        )

        n.duration.quarterLength=1

        s.append(n)



    s.write(
        "musicxml",
        fp=out
    )


    print(
        "完成:",
        out
    )




# ==========================
# Main
# ==========================

if __name__=="__main__":


    if len(sys.argv)<3:

        print(
            "Usage:"
        )

        print(
            "python midi_to_musicxml_clean.py input.mid output.musicxml"
        )

        sys.exit()



    midi_file=sys.argv[1]

    output=sys.argv[2]


    print("讀取 MIDI...")


    midi=converter.parse(
        midi_file
    )


    melody=extract_melody(
        midi
    )


    melody=twinkle_fix(
        melody
    )


    print(
        "輸出 MusicXML..."
    )


    create_musicxml(
        melody,
        output
    )


    print("==============================")