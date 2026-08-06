# midi_to_musicxml_clean_v42.1_pro.py
#
# JianpuTool
# MIDI -> MusicXML
#
# V42.1 PRO
# Fix:
#   - jianpu_ly KeyError 11.0
#   - anacrusis crash
#   - invalid measure length
#   - force 4/4
#

import sys
import copy

from music21 import converter
from music21 import stream
from music21 import note
from music21 import chord
from music21 import meter
from music21 import tempo


# ==========================
# Quantize
# ==========================

def quantize(v):

    # 16th note grid
    return round(v * 4) / 4



# ==========================
# Force 4/4
# ==========================

def force_44(score):

    ts = meter.TimeSignature("4/4")

    for p in score.parts:

        for m in p.getElementsByClass("Measure"):

            m.timeSignature = copy.deepcopy(ts)

    return score



# ==========================
# Remove anacrusis
# ==========================

def remove_anacrusis(score):

    for p in score.parts:

        measures = list(
            p.getElementsByClass("Measure")
        )

        for i, m in enumerate(measures):

            if i == 0:

                m.paddingLeft = 0

                try:
                    m.padAsAnacrusis = False
                except:
                    pass


    return score



# ==========================
# Melody extraction
# ==========================

def extract_melody(midi):

    notes = []


    for part in midi.parts:

        for n in part.recurse():

            if isinstance(n, note.Note):

                notes.append(n)

            elif isinstance(n, chord.Chord):

                # 最高音當旋律

                notes.append(
                    note.Note(
                        max(n.pitches)
                    )
                )


    return notes



# ==========================
# Build score
# ==========================

def build_musicxml(notes):

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

        ql = quantize(
            n.duration.quarterLength
        )


        if beat + ql > 4:

            # 補滿小節

            rest = note.Rest()

            rest.duration.quarterLength = (
                4 - beat
            )

            if rest.duration.quarterLength > 0:

                measure.append(rest)


            part.append(measure)


            measure = stream.Measure()

            measure.number += 1

            beat = 0


        new_note = copy.deepcopy(n)

        new_note.duration.quarterLength = ql

        measure.append(new_note)

        beat += ql



    # 最後小節

    if beat < 4:

        r = note.Rest()

        r.duration.quarterLength = 4 - beat

        measure.append(r)


    part.append(measure)

    score.append(part)


    return score



# ==========================
# Clean measure
# ==========================

def clean_measure(score):

    for p in score.parts:

        for m in p.getElementsByClass("Measure"):

            length = m.duration.quarterLength


            if length != 4:

                diff = 4 - length


                if diff > 0:

                    r = note.Rest()

                    r.duration.quarterLength = diff

                    m.append(r)


    return score



# ==========================
# Main
# ==========================

def main():

    if len(sys.argv) < 3:

        print(
            "Usage:"
        )

        print(
            "python midi_to_musicxml_clean_v42.1_pro.py input.mid output.musicxml"
        )

        sys.exit(1)


    midi_file = sys.argv[1]

    output = sys.argv[2]


    print("讀取 MIDI...")

    midi = converter.parse(
        midi_file
    )


    print(
        "抽取旋律..."
    )

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


    score = build_musicxml(
        notes
    )


    print(
        "修正拍號..."
    )


    score = clean_measure(score)

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