# rebuild_measures.py
#
# JianpuTool MVP 1.1
# 強制重建 MusicXML 小節
#

import sys
import copy

from music21 import converter
from music21 import stream
from music21 import meter
from music21 import note


if len(sys.argv) < 3:

    print(
        "python rebuild_measures.py input.musicxml output.musicxml"
    )

    sys.exit(1)



src = sys.argv[1]
dst = sys.argv[2]



print("讀取:")
print(src)



score = converter.parse(src)



new_score = stream.Score()



for part in score.parts:


    print(
        "處理 Part"
    )


    new_part = stream.Part()



    new_part.append(
        meter.TimeSignature("4/4")
    )



    measure_no = 1


    measure = stream.Measure(
        number=measure_no
    )


    current = 0.0



    elements = list(
        part.flatten().notesAndRests
    )



    for element in elements:


        item = copy.deepcopy(element)


        duration = float(
            item.duration.quarterLength
        )



        if duration <= 0:

            continue



        # 防止超長音符

        while duration > 0:


            remain = 4.0 - current



            take = min(
                duration,
                remain
            )



            new_item = copy.deepcopy(item)


            new_item.duration.quarterLength = take



            measure.insert(
                current,
                new_item
            )



            current += take

            duration -= take



            # 滿4拍，封閉小節

            if current >= 4.0 - 0.001:


                new_part.append(
                    measure
                )


                measure_no += 1


                measure = stream.Measure(
                    number=measure_no
                )


                current = 0.0




    # 最後不足4拍補休止符

    if current > 0:


        rest = note.Rest()


        rest.duration.quarterLength = (
            4.0 - current
        )


        measure.insert(
            current,
            rest
        )


        new_part.append(
            measure
        )



    # 補 offset gap

    new_part.makeRests(
        fillGaps=True,
        inPlace=True
    )


    new_part.makeMeasures(
        inPlace=True
    )



    new_score.append(
        new_part
    )




# 最後整理

new_score.makeRests(
    fillGaps=True,
    inPlace=True
)


new_score.makeMeasures(
    inPlace=True
)



new_score.write(
    "musicxml",
    fp=dst
)



print(
    "================"
)

print(
    "REBUILD MEASURES OK"
)

print(
    dst
)