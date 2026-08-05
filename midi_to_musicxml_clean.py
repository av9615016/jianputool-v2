# ==========================================================
# midi_to_musicxml_clean.py V32.2
#
# JianpuTool
#
# MIDI -> MusicXML
#
# Vocal Track + Melody Tracking
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


# ----------------------------------------------------------
# 安全 duration
# ----------------------------------------------------------

VALID_LENGTH = [
    0.25,
    0.5,
    1.0,
    2.0,
    4.0
]


def quantize_length(x):

    return min(
        VALID_LENGTH,
        key=lambda y:abs(y-x)
    )



def safe_rest(x):

    x = quantize_length(x)

    r = note.Rest()

    r.duration = duration.Duration(
        x
    )

    return r



# ----------------------------------------------------------
# Vocal Track
# ----------------------------------------------------------

def find_vocal(score):

    keys = [
        "vocal",
        "voice",
        "melody",
        "lead",
        "sing"
    ]

    for part in score.parts:

        name=""

        if part.partName:
            name=str(
                part.partName
            ).lower()


        if any(k in name for k in keys):

            print(
                "找到 Vocal:",
                part.partName
            )

            return part


    return None



# ----------------------------------------------------------
# 收集候選音
# ----------------------------------------------------------

def collect_notes(part):

    result=[]


    for e in part.flatten().notes:


        if isinstance(e,note.Note):

            n=copy.deepcopy(e)

            result.append(n)


        elif isinstance(e,chord.Chord):

            # 和弦取最高音

            n=max(
                e.notes,
                key=lambda x:x.pitch.midi
            )

            n=copy.deepcopy(n)

            n.offset=e.offset

            result.append(n)



    return result



# ----------------------------------------------------------
# Melody Filter
# ----------------------------------------------------------

def melody_filter(notes):


    print(
        "原始:",
        len(notes)
    )


    # 人聲範圍

    notes=[
        n for n in notes
        if 55 <= n.pitch.midi <= 84
    ]


    print(
        "音域篩選:",
        len(notes)
    )


    # 同時間最高音

    table={}


    for n in notes:

        t=round(
            float(n.offset),
            2
        )


        if (
            t not in table
            or
            n.pitch.midi >
            table[t].pitch.midi
        ):

            table[t]=n



    result=list(
        table.values()
    )


    result.sort(
        key=lambda x:x.offset
    )


    print(
        "旋律:",
        len(result)
    )


    return result



# ----------------------------------------------------------
# 建立 4/4
# ----------------------------------------------------------

def build_score(notes):


    score=stream.Score()

    part=stream.Part()


    part.append(
        meter.TimeSignature("4/4")
    )


    part.append(
        tempo.MetronomeMark(
            number=80
        )
    )


    measure=stream.Measure(
        number=1
    )


    beat=0



    for n in notes:


        q=quantize_length(
            float(
                n.duration.quarterLength
            )
        )


        n2=copy.deepcopy(n)

        n2.duration=duration.Duration(
            q
        )


        if beat+q > 4:


            rest_time=4-beat


            if rest_time>0:

                measure.append(
                    safe_rest(rest_time)
                )


            part.append(
                measure
            )


            measure=stream.Measure(
                number=
                measure.number+1
            )


            beat=0



        measure.append(
            n2
        )


        beat+=q



    if beat < 4:

        measure.append(
            safe_rest(
                4-beat
            )
        )


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

    output=sys.argv[2]


    print(
        "讀取 MIDI..."
    )


    score=converter.parse(
        midi
    )


    print(
        "Tracks:",
        len(score.parts)
    )



    vocal=find_vocal(score)



    if vocal:

        print(
            "模式: Vocal MIDI"
        )

        notes=collect_notes(
            vocal
        )


    else:

        print(
            "模式: Melody Extraction"
        )


        part=score.parts[0]


        notes=collect_notes(
            part
        )


        notes=melody_filter(
            notes
        )



    print(
        "建立 MusicXML..."
    )


    result=build_score(
        notes
    )


    result.write(
        "musicxml",
        fp=output
    )


    print(
        "完成:",
        output
    )