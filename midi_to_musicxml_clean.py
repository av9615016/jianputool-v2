# ==========================================================
# midi_to_musicxml_clean.py V31
#
# JianpuTool
#
# Vocal Melody Tracker
#
# MIDI -> MusicXML
#
# ==========================================================

import sys
import copy
import math

from music21 import converter
from music21 import stream
from music21 import note
from music21 import chord
from music21 import meter
from music21 import tempo
from music21 import duration



# ----------------------------------------------------------
# Vocal Track
# ----------------------------------------------------------

VOCAL_KEYS = [
    "vocal",
    "voice",
    "melody",
    "lead",
    "singer",
    "sing"
]


def find_vocal_part(score):

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
# 收集候選旋律音
# ----------------------------------------------------------

def collect_candidates(part):

    notes = []


    for e in part.flatten().notes:


        if isinstance(e, note.Note):

            n = copy.deepcopy(e)
            notes.append(n)


        elif isinstance(e, chord.Chord):

            for n in e.notes:

                nn = copy.deepcopy(n)

                nn.offset = e.offset

                notes.append(nn)



    print(
        "全部音符:",
        len(notes)
    )


    # 人聲範圍

    candidates = [

        n for n in notes

        if 55 <= n.pitch.midi <= 84

    ]


    print(
        "人聲範圍候選:",
        len(candidates)
    )


    return candidates



# ----------------------------------------------------------
# Melody Tracking
# ----------------------------------------------------------

def melody_tracker(notes):


    print(
        "啟動 Vocal Melody Tracker"
    )


    # 同時間分組

    groups = {}


    for n in notes:

        t = round(
            float(n.offset),
            2
        )


        groups.setdefault(
            t,
            []
        ).append(n)



    timeline = []


    for t in sorted(groups.keys()):


        candidates = groups[t]


        # 長音優先

        best = max(
            candidates,
            key=lambda n:
            (
                float(n.duration.quarterLength),
                n.pitch.midi
            )
        )


        timeline.append(best)



    # ----------------------------------
    # 音程連續修正
    # ----------------------------------

    result = []


    last_pitch = None


    for n in timeline:


        pitch = n.pitch.midi


        if last_pitch is not None:


            jump = abs(
                pitch-last_pitch
            )


            # 太大跳躍通常是伴奏

            if jump > 12:

                continue



        result.append(n)

        last_pitch = pitch



    print(
        "追蹤後:",
        len(result)
    )


    return result



# ----------------------------------------------------------
# Quantize
# ----------------------------------------------------------

def quantize_note(n):

    n2 = copy.deepcopy(n)


    values = [

        0.25,
        0.5,
        1,
        2,
        4

    ]


    q = float(
        n2.duration.quarterLength
    )


    best = min(
        values,
        key=lambda x:abs(x-q)
    )


    n2.duration = duration.Duration(
        best
    )


    return n2



# ----------------------------------------------------------
# 建立4/4
# ----------------------------------------------------------

def build_musicxml(notes):


    score = stream.Score()

    part = stream.Part()


    part.append(
        meter.TimeSignature("4/4")
    )


    part.append(
        tempo.MetronomeMark(80)
    )


    measure = stream.Measure(
        number=1
    )


    beat = 0


    bar = 1



    for n in notes:


        n = quantize_note(n)


        length = float(
            n.duration.quarterLength
        )


        if beat + length > 4:


            rest = note.Rest()

            rest.duration = duration.Duration(
                4-beat
            )


            if 4-beat > 0:

                measure.append(rest)



            part.append(measure)


            bar += 1


            measure = stream.Measure(
                number=bar
            )


            beat = 0



        measure.append(n)

        beat += length



    if beat < 4:


        rest = note.Rest()

        rest.duration = duration.Duration(
            4-beat
        )

        measure.append(rest)



    part.append(measure)


    score.append(part)


    return score



# ----------------------------------------------------------
# MAIN
# ----------------------------------------------------------

if __name__ == "__main__":


    if len(sys.argv)<3:

        print(
            "python midi_to_musicxml_clean.py input.mid output.musicxml"
        )

        exit()



    midi = sys.argv[1]

    output = sys.argv[2]


    print(
        "讀取 MIDI..."
    )


    score = converter.parse(
        midi
    )


    print(
        "Tracks:",
        len(score.parts)
    )



    vocal = find_vocal_part(score)



    if vocal:


        print(
            "模式: Vocal MIDI"
        )


        notes = [

            n for n in vocal.flatten().notes

            if isinstance(n,note.Note)

        ]


    else:


        print(
            "沒有 Vocal Track"
        )


        if len(score.parts)==1:

            part = score.parts[0]


        else:

            part = max(
                score.parts,
                key=lambda p:
                len(p.flatten().notes)
            )



        candidates = collect_candidates(
            part
        )


        notes = melody_tracker(
            candidates
        )



    print(
        "建立 MusicXML..."
    )


    result = build_musicxml(
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