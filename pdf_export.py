import subprocess
import sys


def make_pdf(ly):

    subprocess.run(
        [
        "lilypond",
        "-o",
        "output",
        ly
        ],
        check=True
    )


if __name__=="__main__":

    make_pdf(sys.argv[1])