# ==========================================================
# midi_to_musicxml_clean.py V32
#
# Dynamic Programming Melody Path
#
# ==========================================================

import sys
import copy

from music21 import converter
from music21 import stream
from music21 import note
from music21 import chord
from music21 import meter
from music21 import tempo
from music21 import duration


VOCAL_KEYS = [
    "vocal",
    "voice",
    "melody",
    "lead",
    "singer",
    "sing"
]


# ----------------------------------------------------------
# 找 Vocal
# ----------------------------------------------------------

def find_vocal(score):

    for part in score.parts:

        name = str(part.partName).lower()

        if any(k in name for k in VOCAL_KEYS):
            return part

    return None



# ----------------------------------------------------------
# 建立候選音
# ----------------------------------------------------------

def collect_candidates(part):

    groups = {}


    for e in part.flatten().notes:


        notes=[]


        if isinstance(e,note.Note):

            notes=[e]


        elif isinstance(e,chord.Chord):

            notes=e.notes



        for n in notes:


            if 55 <= n.pitch.midi <= 84:


                nn=copy.deepcopy(n)

                nn.offset=e.offset


                t=round(
                    float(e.offset),
                    2
                )


                groups.setdefault(
                    t,
                    []
                ).append(nn)



    timeline=[]


    for t in sorted(groups):

        timeline.append(
            groups[t]
        )


    print(
        "候選時間點:",
        len(timeline)
    )


    return timeline



# ----------------------------------------------------------
# Dynamic Programming Melody Path
# ----------------------------------------------------------

def pitch_score(n):

    p=n.pitch.midi


    # 人聲中心 C4-C5

    return 10 - abs(
        p-72
    )*0.15



def duration_score(n):

    d=float(
        n.duration.quarterLength
    )

    return min(
        d,
        2
    )



def transition_score(a,b):

    jump=abs(
        b.pitch.midi-
        a.pitch.midi
    )


    # 小跳最佳

    if jump<=5:
        return 5


    if jump<=12:
        return 1


    return -8



def dynamic_melody(groups):


    print(
        "Dynamic Programming Tracking"
    )


    if not groups:
        return []


    dp=[]


    parent=[]



    # 第一層

    first=[]


    for n in groups[0]:

        first.append(
            pitch_score(n)
            +
            duration_score(n)
        )


    dp.append(first)

    parent.append(
        [-1]*len(first)
    )



    # 後續

    for i in range(1,len(groups)):


        scores=[]

        parents=[]


        for j,n in enumerate(groups[i]):


            best=-999

            best_k=-1


            for k,prev in enumerate(groups[i-1]):


                s=(

                    dp[i-1][k]

                    +

                    transition_score(
                        prev,
                        n
                    )

                    +

                    pitch_score(n)

                    +

                    duration_score(n)

                )


                if s>best:

                    best=s
                    best_k=k



            scores.append(best)

            parents.append(best_k)



        dp.append(scores)

        parent.append(parents)



    # 回溯

    index=max(
        range(len(dp[-1])),
        key=lambda i:dp[-1][i]
    )


    result=[]


    for i in range(
        len(groups)-1,
        -1,
        -1
    ):

        result.append(
            groups[i][index]
        )

        index=parent[i][index]


        if index<0:
            break



    result.reverse()


    print(
        "最佳旋律:",
        len(result)
    )


    return result



# ----------------------------------------------------------
# 建立 MusicXML
# ----------------------------------------------------------

def build_xml(notes):


    score=stream.Score()

    part=stream.Part()


    part.append(
        meter.TimeSignature("4/4")
    )


    part.append(
        tempo.MetronomeMark(80)
    )


    measure=stream.Measure(
        number=1
    )


    beat=0


    for n in notes:


        q=copy.deepcopy(n)


        q.duration=duration.Duration(
            min(
                float(q.duration.quarterLength),
                2
            )
        )


        length=float(
            q.duration.quarterLength
        )


        if beat+length>4:

            r=note.Rest()

            r.duration=duration.Duration(
                4-beat
            )

            measure.append(r)

            part.append(measure)

            measure=stream.Measure(
                number=measure.number+1
            )

            beat=0



        measure.append(q)

        beat+=length



    if beat<4:

        r=note.Rest()

        r.duration=duration.Duration(
            4-beat
        )

        measure.append(r)



    part.append(measure)

    score.append(part)


    return score



# ----------------------------------------------------------
# MAIN
# ----------------------------------------------------------

if __name__=="__main__":


    midi=sys.argv[1]

    out=sys.argv[2]


    print("讀取 MIDI")


    score=converter.parse(midi)



    vocal=find_vocal(score)



    if vocal:

        notes=[
            n for n in vocal.flatten().notes
            if isinstance(n,note.Note)
        ]

    else:

        print(
            "使用 Dynamic Melody Path"
        )


        part=score.parts[0]


        groups=collect_candidates(
            part
        )


        notes=dynamic_melody(
            groups
        )



    result=build_xml(
        notes
    )


    result.write(
        "musicxml",
        fp=out
    )


    print(
        "完成:",
        out
    )