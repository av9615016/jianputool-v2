# midi_quantize.py
#
# BasicPitch MIDI 節拍量化修正
# MIDI -> MIDI


import sys
from music21 import converter
from music21 import note
from music21 import chord



def quantize_length(length):

    """
    將音符長度靠近標準拍值
    """

    values = [
        0.125,   # 32分音符
        0.25,    # 16分音符
        0.5,     # 8分音符
        1.0,     # 四分音符
        2.0,     # 二分音符
        4.0      # 全音符
    ]


    return min(
        values,
        key=lambda x: abs(x-length)
    )



def process_midi(input_file, output_file):


    print("讀取 MIDI:")
    print(input_file)


    score = converter.parse(
        input_file
    )


    for part in score.parts:


        # 修正音符時間

        for element in part.flatten().notes:


            if isinstance(element, note.Note):


                element.duration.quarterLength = (
                    quantize_length(
                        element.duration.quarterLength
                    )
                )


            elif isinstance(element, chord.Chord):


                element.duration.quarterLength = (
                    quantize_length(
                        element.duration.quarterLength
                    )
                )



        # 修正offset

        for element in part.flatten().notes:

            element.offset = round(
                element.offset * 4
            ) / 4



    score.write(
        "midi",
        fp=output_file
    )


    print(
        "MIDI quantize OK"
    )



if __name__ == "__main__":


    if len(sys.argv) < 3:

        print(
            "使用方式:"
        )

        print(
            "python midi_quantize.py input.mid output.mid"
        )

        sys.exit(1)



    process_midi(
        sys.argv[1],
        sys.argv[2]
    )