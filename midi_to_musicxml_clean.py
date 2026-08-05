# ==========================================================
# midi_to_musicxml_clean.py V30.3
#
# JianpuTool
#
# MIDI -> MusicXML
#
# Melody Extractor Pro
# Final Quantize Builder
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

            print("找到 Vocal Track:", part.partName)
            return part

    return None



# ----------------------------------------------------------
# Melody Extractor
# ----------------------------------------------------------

def extract_melody_pro(part):

    print("啟動 Melody Extractor Pro")

    raw = []

    for element in part.flatten().notes:

        if isinstance(element, note.Note):

            raw.append(
                copy.deepcopy(element)
            )


        elif isinstance(element, chord.Chord):

            highest = max(
                element.notes,
                key=lambda x:x.pitch.midi
            )

            n = copy.deepcopy(highest)

            n.offset = element.offset

            raw.append(n)


    print("原始音符:", len(raw))


    raw = [
        n for n in raw
        if n.pitch.midi >= 55
    ]


    print("移除低音後:", len(raw))


    timeline = {}


    for n in raw:

        key = round(
            float(n.offset),
            2
        )

        if (
            key not in timeline
            or
            n.pitch.midi >
            timeline[key].pitch.midi
        ):
            timeline[key] = n


    melody = list(
        timeline.values()
    )


    melody.sort(
        key=lambda x:x.offset
    )


    print(
        "時間去重後:",
        len(melody)
    )


    return melody



# ----------------------------------------------------------
# Quantize
# ----------------------------------------------------------

def quantize_length(value):

    """
    四分音符量化
    """

    choices = [
        0.25,
        0.5,
        1.0,
        2.0,
        4.0
    ]

    return min(
        choices,
        key=lambda x:abs(x-value)
    )



def quantize_notes(notes):

    result = []

    for n in notes:

        n2 = copy.deepcopy(n)

        q = float(
            n2.duration.quarterLength
        )


        n2.duration = duration.Duration(
            quantize_length(q)
        )

        result.append(n2)


    return result



# ----------------------------------------------------------
# Measure Builder
# ----------------------------------------------------------

def build_measure_score(notes):


    notes = quantize_notes(notes)


    score = stream.Score()


    part = stream.Part()


    part.append(
        meter.TimeSignature("4/4")
    )


    part.append(
        tempo.MetronomeMark(
            number=80
        )
    )


    measure_no = 1

    measure = stream.Measure(
        number=measure_no
    )


    beat = 0.0



    for n in notes:


        length = float(
            n.duration.quarterLength
        )


        # 音符超過小節

        if beat + length > 4.0:


            rest_time = 4.0 - beat


            if rest_time > 0:

                r = note.Rest()

                r.duration = duration.Duration(
                    rest_time
                )

                measure.append(r)



            part.append(measure)


            measure_no += 1


            measure = stream.Measure(
                number=measure_no
            )


            beat = 0.0



        measure.append(
            n
        )


        beat += length



    # 最後補滿

    if beat < 4.0:

        r = note.Rest()

        r.duration = duration.Duration(
            4.0 - beat
        )

        measure.append(r)



    part.append(measure)


    score.append(part)


    return score



# ----------------------------------------------------------
# MAIN
# ----------------------------------------------------------

if __name__ == "__main__":


    if len(sys.argv) < 3:

        print(
            "python midi_to_musicxml_clean.py input.mid output.musicxml"
        )

        sys.exit()


    midi_file = sys.argv[1]

    output = sys.argv[2]


    print("讀取 MIDI...")


    score = converter.parse(
        midi_file
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

            notes = extract_melody_pro(
                score.parts[0]
            )

        else:

            best = max(
                score.parts,
                key=lambda p:len(p.flatten().notes)
            )

            notes = extract_melody_pro(
                best
            )



    print(
        "建立 Quantized 4/4 MusicXML..."
    )


    final = build_measure_score(
        notes
    )


    final.write(
        "musicxml",
        fp=output
    )


    print(
        "完成:",
        output
    )