from music21 import converter
import sys

mid = converter.parse(sys.argv[1])

for i, part in enumerate(mid.parts):

    notes = [
        n for n in part.recurse().notes
        if n.isNote
    ]

    print("Track", i)
    print("名稱:", part.partName)
    print("音符數:", len(notes))

    pitches = [n.pitch.midi for n in notes]

    print(
        "音域:",
        min(pitches),
        "-",
        max(pitches)
    )

    print(
        "前20音:",
        [str(n.pitch) for n in notes[:20]]
    )