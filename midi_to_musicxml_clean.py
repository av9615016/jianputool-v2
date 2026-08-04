# midi_to_musicxml_clean.py
#
# MIDI -> MusicXML
# JianpuTool MVP 1.1


import sys
from music21 import converter
from music21 import stream
from music21 import meter
from music21 import tempo
from music21 import key


def quantize(value):

    # 16分音符量化

    return round(value * 4) / 4



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

        tempos = part.recurse().getElementsByClass(
            tempo.MetronomeMark
        )

        for t in tempos:

            new_part.append(t)



        # 重新插入音符

        for n in part.flatten().notesAndRests:


            item = n.clone()


            # 修正開始位置

            item.offset = quantize(
                n.offset
            )


            # 修正長度

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



        # 重新建立小節

        new_part.makeMeasures(
            inPlace=True
        )


        new_score.append(
            new_part
        )



    # 輸出 MusicXML

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