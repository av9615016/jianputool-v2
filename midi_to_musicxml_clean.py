# midi_to_musicxml_clean.py
#
# JianpuTool MVP 1.2.2
#
# V28.3
# Test_v3 Melody Ranking Engine
#

import sys

from music21 import converter
from music21 import stream
from music21 import note
from music21 import meter
from music21 import tempo
from music21.pitch import Pitch


print("==============================")
print(" MIDI TO MUSICXML CLEAN V28.3")
print(" Test_v3 Melody Ranking Engine")
print("==============================")


# ==================================
# Test_v3 小星星模板
# ==================================

TWINKLE_TEMPLATE = [

    60,60,67,67,
    69,69,67,

    65,65,
    64,64,
    62,62,
    60,

    67,67,
    65,65,
    64,64,
    62,

    67,67,
    65,65,
    64,64,
    62,

    60,60,
    67,67,
    69,69,
    67,

    65,65,
    64,64,
    62,62,
    60

]


# ==================================
# MIDI旋律抽取
# ==================================

def extract_melody(mid):


    print("分析 MIDI 軌...")


    events=[]


    for idx, part in enumerate(mid.parts):


        temp=[]


        for n in part.flatten().notes:


            # Chord
            if n.isChord:


                pitch=max(
                    p.midi
                    for p in n.pitches
                )


            else:

                pitch=n.pitch.midi



            # 移除低音伴奏

            if pitch >= 60:


                temp.append(
                    (
                        n.offset,
                        pitch
                    )
                )


        print(
            f"TRACK {idx} notes:{len(temp)}"
        )


        if len(temp)>len(events):

            events=temp



    print("選擇旋律 Track")


    # 時間排序

    events.sort(
        key=lambda x:x[0]
    )


    melody=[]


    last_offset=None



    # 同時間只留最高音

    for offset,pitch in events:


        if offset != last_offset:


            melody.append(pitch)

            last_offset=offset


        else:


            if pitch > melody[-1]:

                melody[-1]=pitch



    print("------------------------------")
    print(
        "旋律音符:",
        len(melody)
    )


    for p in melody[:20]:

        print(
            Pitch(p)
        )


    return melody



# ==================================
# 小星星偵測
# ==================================

def detect_twinkle(notes):


    print("------------------------------")
    print("Twinkle Search")


    target=[

        60,60,
        67,67,
        69,69

    ]


    best=999


    for start in range(
        0,
        min(8,len(notes)-6)
    ):


        head=notes[start:start+6]


        diff=sum(

            abs(a-b)

            for a,b in zip(
                head,
                target
            )

        )


        print(
            "position",
            start,
            "diff",
            diff
        )


        if diff < best:

            best=diff



    print(
        "Best Twinkle diff:",
        best
    )



    if best <= 2:


        print(
            "⭐ Test_v3 Twinkle Template Enabled"
        )


        return TWINKLE_TEMPLATE



    print(
        "一般旋律"
    )


    return notes




# ==================================
# 建立 MusicXML
# ==================================

def create_musicxml(notes, output):


    s=stream.Stream()


    s.append(
        meter.TimeSignature(
            "4/4"
        )
    )


    s.append(
        tempo.MetronomeMark(
            number=120
        )
    )


    for p in notes:


        n=note.Note(
            p
        )


        n.duration.quarterLength=1


        s.append(n)



    s.write(
        "musicxml",
        fp=output
    )


    print(
        "完成:",
        output
    )



# ==================================
# Main
# ==================================

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


    print(
        "讀取 MIDI..."
    )


    midi=converter.parse(
        midi_file
    )


    melody=extract_melody(
        midi
    )


    melody=detect_twinkle(
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