# ==========================================================
# midi_to_musicxml_clean.py V32.1
#
# Dynamic Programming Melody Path FIX
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
# Vocal
# ----------------------------------------------------------

def find_vocal(score):

    for part in score.parts:

        name = ""

        if part.partName:
            name = str(part.partName).lower()


        if any(k in name for k in VOCAL_KEYS):

            print(
                "找到 Vocal:",
                part.partName
            )

            return part

    return None



# ----------------------------------------------------------
# Candidates
# ----------------------------------------------------------

def collect_candidates(part):

    groups = {}


    for e in part.flatten().notes:


        elements=[]


        if isinstance(e,note.Note):

            elements=[e]


        elif isinstance(e,chord.Chord):

            elements=e.notes



        for n in elements:


            nn=copy.deepcopy(n)

            nn.offset=e.offset


            pitch=nn.pitch.midi


            # 人聲範圍

            if 55 <= pitch <= 84:


                # 太短降低權重
                if float(nn.duration.quarterLength) >= 0.125:


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
        "候選時間:",
        len(timeline)
    )


    return timeline



# ----------------------------------------------------------
# Scoring
# ----------------------------------------------------------

def note_score(n):

    pitch=n.pitch.midi


    # 人聲中心附近較高

    score=10-abs(
        pitch-72
    )*0.2


    length=float(
        n.duration.quarterLength
    )


    score += min(
        length,
        2
    )


    return score



def jump_score(a,b):

    jump=abs(
        a.pitch.midi-
        b.pitch.midi
    )


    if jump<=5:
        return 5

    if jump<=12:
        return 1

    return -8



# ----------------------------------------------------------
# DP with Skip
# ----------------------------------------------------------

def dynamic_path(groups):


    print(
        "Dynamic Programming Melody Path"
    )


    if not groups:
        return []



    dp=[]

    parent=[]



    # 第一層

    dp.append(
        [
            note_score(n)
            for n in groups[0]
        ]
    )


    parent.append(
        [
            -1
            for n in groups[0]
        ]
    )



    for i in range(1,len(groups)):


        current=[]

        current_parent=[]


        for j,n in enumerate(groups[i]):


            best=-99999

            best_k=-1



            for k,prev in enumerate(groups[i-1]):


                s=(

                    dp[i-1][k]

                    +

                    jump_score(
                        prev,
                        n
                    )

                    +

                    note_score(n)

                )


                if s>best:

                    best=s
                    best_k=k



            # skip penalty

            if best < -5:

                continue



            current.append(best)

            current_parent.append(best_k)



        if current:

            dp.append(current)

            parent.append(
                current_parent
            )



    # 回溯

    if not dp:
        return []


    idx=max(
        range(len(dp[-1])),
        key=lambda x:dp[-1][x]
    )


    result=[]


    for i in range(
        len(dp)-1,
        -1,
        -1
    ):

        if idx < len(groups[i]):

            result.append(
                groups[i][idx]
            )


        if i>0 and idx < len(parent[i]):

            idx=parent[i][idx]



    result.reverse()


    print(
        "最佳旋律:",
        len(result)
    )


    return result



# ----------------------------------------------------------
# Safe Rest
# ----------------------------------------------------------

def make_rest(length):

    if length <=0:
        return None


    r=note.Rest()


    r.duration=duration.Duration(
        length
    )


    return r



# ----------------------------------------------------------
# MusicXML
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


        n2=copy.deepcopy(n)


        q=min(
            float(n2.duration.quarterLength),
            2
        )


        n2.duration=duration.Duration(q)



        if beat+q>4:


            r=make_rest(
                4-beat
            )


            if r:
                measure.append(r)


            part.append(
                measure
            )


            measure=stream.Measure(
                number=measure.number+1
            )


            beat=0



        measure.append(
            n2
        )


        beat+=q



    r=make_rest(
        4-beat
    )


    if r:
        measure.append(r)



    part.append(
        measure
    )


    score.append(
        part
    )


    return score



# ----------------------------------------------------------
# MAIN
# ----------------------------------------------------------

if __name__=="__main__":


    midi=sys.argv[1]

    out=sys.argv[2]


    print(
        "讀取 MIDI"
    )


    score=converter.parse(
        midi
    )


    vocal=find_vocal(score)



    if vocal:


        notes=[
            n for n in vocal.flatten().notes
            if isinstance(n,note.Note)
        ]


    else:


        print(
            "單軌 Melody Tracking"
        )


        part=score.parts[0]


        groups=collect_candidates(
            part
        )


        notes=dynamic_path(
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