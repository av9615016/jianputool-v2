import sys
from music21 import converter


src = sys.argv[1]
dst = sys.argv[2]


score = converter.parse(src)



for part in score.parts:


    for measure in part.getElementsByClass("Measure"):


        total = sum(
            n.duration.quarterLength
            for n in measure.notesAndRests
        )


        if total != 4.0:


            diff = total - 4.0


            notes = list(
                measure.notesAndRests
            )


            if notes:


                last = notes[-1]


                new_len = (
                    last.duration.quarterLength
                    - diff
                )


                if new_len > 0:

                    last.duration.quarterLength = new_len



score.write(
    "musicxml",
    fp=dst
)


print(
    "FINAL MEASURE FIX OK"
)