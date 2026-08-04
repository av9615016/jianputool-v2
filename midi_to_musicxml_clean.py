# midi_to_musicxml_clean.py
#
# JianpuTool MVP 1.1
# MIDI -> MusicXML
#

import sys
import copy

from music21 import converter
from music21 import stream
from music21 import meter
from music21 import tempo



def quantize(value):

    # 16分音符量化

    return round(value * 4) / 4



def fix_measures(part):

    """
    修正超過4拍的小節
    """

    for m in part.getElementsByClass("Measure"):


        total = sum(
            n.duration.quarterLength
            for n in m.notesAndRests
        )


        if total > 4.0:


            diff = total - 4.0


            notes = list(
                m.notesAndRests
            )


            if notes:


                last = notes[-1]


                new_length = (
                    last.duration.quarterLength
                    - diff
                )


                if new_length > 0:

                    last.duration.quarterLength = (
                        new_length
                    )




def convert_midi(
    midi_file,
    output_file
):


    print("讀取 MIDI:")
    print(midi_file)



    score = converter.parse(
        midi_file
    )



    new_score = stream.Score()



    for part in score.parts:



        new_part = stream.Part()



        # 強制4/4

        new_part.append(
            meter.TimeSignature("4/4")
        )



        # 保留速度

        for t in part.recurse().getElementsByClass(
            tempo.MetronomeMark
        ):

            new_part.append(
                copy.deepcopy(t)
            )



        # 複製音符

        for n in part.flatten().notesAndRests:


            item = copy.deepcopy(n)



            # offset量化

            item.offset = quantize(
                n.offset
            )



            # duration量化

            length = quantize(
                n.duration.quarterLength
            )



            if length <= 0:

                length = 0.25



            item.duration.quarterLength = length



            new_part.insert(
                item.offset,
                item
            )



        # 建立小節

        new_part.makeMeasures(
            inPlace=True
        )



        # 修正超長小節

        fix_measures(
            new_part
        )



        new_score.append(
            new_part
        )



    # 最後重新建立小節

    new_score.makeMeasures(
        inPlace=True
    )



    new_score.write(
        "musicxml",
        fp=output_file
    )



    print(
        "MusicXML OK:"
    )

    print(
        output_file
    )




if __name__ == "__main__":


    if len(sys.argv) < 3:

        print(
            "使用方式:"
        )

        print(
            "python midi_to_musicxml_clean.py input.mid output.musicxml"
        )

        sys.exit(1)



    convert_midi(
        sys.argv[1],
        sys.argv[2]
    )