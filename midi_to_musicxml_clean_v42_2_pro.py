# midi_to_musicxml_clean_v42_2_pro.py
#
# JianpuTool
# MIDI -> MusicXML
#
# V42.2 PRO
#
# Fix:
# - jianpu_ly unexpected '}'
# - invalid measure structure
# - empty measure
# - anacrusis
# - force 4/4
#

import sys
import copy

from music21 import converter
from music21 import stream
from music21 import note
from music21 import chord
from music21 import meter
from music21 import tempo


# =========================
# Quantize
# =========================

def quantize(v):

    return round(v * 4) / 4



# =========================
# Extract melody
# =========================

def extract_melody(score):

    result = []

    for part in score.parts:

        for n in part.recurse():

            if isinstance(n, note.Note):

                result.append(copy.deepcopy(n))

            elif isinstance(n, chord.Chord):

                result.append(
                    note.Note(
                        max(n.pitches)
                    )
                )

    return result



# =========================
# Build score
# =========================

def build_score(notes):

    score = stream.Score()

    part = stream.Part()


    part.insert(
        0,
        meter.TimeSignature("4/4")
    )

    part.insert(
        0,
        tempo.MetronomeMark(
            number=80
        )
    )


    measure = stream.Measure()

    measure.number = 1

    beat = 0


    for n in notes:

        q = quantize(
            n.duration.quarterLength
        )


        if q <= 0:
            continue


        if q > 4:
            q = 4


        if beat + q > 4:

            remain = 4 - beat

            if remain > 0:

                r = note.Rest()

                r.duration.quarterLength = remain

                measure.append(r)


            part.append(measure)


            measure = stream.Measure()

            measure.number += 1

            beat = 0



        new_note = copy.deepcopy(n)

        new_note.duration.quarterLength = q

        measure.append(new_note)

        beat += q



    if beat < 4:

        r = note.Rest()

        r.duration.quarterLength = 4 - beat

        measure.append(r)



    part.append(measure)

    score.append(part)


    return score



# =========================
# Remove empty measures
# =========================

def remove_empty_measures(score):

    for p in score.parts:

        for m in list(
            p.getElementsByClass("Measure")
        ):

            if len(m.notes) == 0:

                p.remove(m)


    return score



# =========================
# Fix measure length
# =========================

def fix_measure_length(score):

    for p in score.parts:

        for m in p.getElementsByClass("Measure"):

            length = m.duration.quarterLength


            if length < 4:

                r = note.Rest()

                r.duration.quarterLength = 4 - length

                m.append(r)


            elif length > 4:

                while m.duration.quarterLength > 4:

                    if len(m.notes):

                        m.pop()


                    else:

                        break


    return score



# =========================
# Remove anacrusis
# =========================

def remove_anacrusis(score):

    for p in score.parts:

        for m in p.getElementsByClass("Measure"):

            try:

                m.padAsAnacrusis = False

            except:

                pass


    return score



# =========================
# Force 4/4
# =========================

def force_44(score):

    ts = meter.TimeSignature(
        "4/4"
    )


    for p in score.parts:

        for m in p.getElementsByClass("Measure"):

            m.timeSignature = copy.deepcopy(ts)


    return score



# =========================
# Remove invalid rests
# =========================

def clean_rests(score):

    for p in score.parts:

        for m in p.getElementsByClass("Measure"):

            for r in list(
                m.recurse().getElementsByClass(note.Rest)
            ):

                if r.duration.quarterLength <= 0:

                    m.remove(r)


    return score



# =========================
# Main
# =========================

def main():

    if len(sys.argv) < 3:

        print(
            "Usage:"
        )

        print(
            "python midi_to_musicxml_clean_v42_2_pro.py input.mid output.musicxml"
        )

        sys.exit(1)



    midi_file = sys.argv[1]

    output = sys.argv[2]


    print("讀取 MIDI...")


    midi = converter.parse(
        midi_file
    )


    print("抽取旋律...")


    notes = extract_melody(
        midi
    )


    print(
        "旋律數:",
        len(notes)
    )


    print(
        "建立 MusicXML..."
    )


    score = build_score(
        notes
    )


    print(
        "MusicXML 安全修正..."
    )


    score = remove_empty_measures(score)

    score = clean_rests(score)

    score = fix_measure_length(score)

    score = remove_anacrusis(score)

    score = force_44(score)



    print(
        "輸出 MusicXML..."
    )


    score.write(
        "musicxml",
        fp=output
    )


    print(
        "完成:",
        output
    )



if __name__ == "__main__":

    main()