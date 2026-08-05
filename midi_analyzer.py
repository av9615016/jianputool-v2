import sys
from music21 import converter


if len(sys.argv) < 2:
    print("用法: python midi_analyzer.py xxx.mid")
    sys.exit()


midi_file = sys.argv[1]


print("======================")
print("MIDI ANALYZER")
print("======================")


score = converter.parse(midi_file)


print("Parts:", len(score.parts))


for i, part in enumerate(score.parts):

    notes = list(part.flat.notes)

    pitches = []

    for n in notes:
        if hasattr(n, "pitch"):
            pitches.append(
                n.pitch.midi
            )
        elif hasattr(n, "pitches"):
            for p in n.pitches:
                pitches.append(
                    p.midi
                )


    print()
    print("Track:", i)

    print(
        "音符數:",
        len(notes)
    )


    if pitches:

        print(
            "最低:",
            min(pitches)
        )

        print(
            "最高:",
            max(pitches)
        )

        print(
            "平均:",
            sum(pitches)//len(pitches)
        )