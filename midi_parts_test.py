from music21 import converter
import sys


mid_file = sys.argv[1]


score = converter.parse(mid_file)


print("PARTS:", len(score.parts))


for i, part in enumerate(score.parts):

    print("\n================")
    print("PART", i)
    print("================")

    print("name:", part.partName)

    try:
        print(
            "instrument:",
            part.getInstrument()
        )
    except:
        pass


    notes = []

    for n in part.recurse().notes:

        if n.isNote:

            notes.append(n)


    print(
        "notes:",
        len(notes)
    )


    print("前10個音:")


    for n in notes[:10]:

        print(
            n.pitch,
            n.pitch.midi
        )