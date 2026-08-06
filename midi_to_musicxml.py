import sys

from music21 import converter


def convert(mid,out):

    score=converter.parse(mid)

    score.write(
        "musicxml",
        fp=out
    )


if __name__=="__main__":

    convert(
        sys.argv[1],
        sys.argv[2]
    )