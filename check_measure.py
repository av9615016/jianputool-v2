# check_measure.py

import sys
from music21 import converter


def check_measure(file):

    print("讀取:")
    print(file)

    score = converter.parse(file)


    for part in score.parts:

        print("\nPart:", part.id)


        for measure in part.getElementsByClass("Measure"):

            total = 0


            for n in measure.notesAndRests:

                total += n.duration.quarterLength


            print(
                f"Measure {measure.number}: {total}"
            )



if __name__ == "__main__":


    if len(sys.argv) < 2:

        print(
            "使用方式:"
        )

        print(
            "python check_measure.py xxx.musicxml"
        )

        sys.exit(1)


    filename = sys.argv[1]


    try:

        check_measure(filename)


    except Exception as e:

        print(
            "錯誤:"
        )

        print(e)

        sys.exit(1)