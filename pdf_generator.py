import subprocess
import os
import sys


def generate_pdf(
    musicxml,
    output
):


    subprocess.run(
        [
            sys.executable,
            "-m",
            "jianpu_ly",
            musicxml
        ],
        check=True
    )


    ly="score.ly"


    subprocess.run(
        [
            "lilypond",
            ly
        ],
        cwd=os.getcwd(),
        check=True
    )


    pdf="score.pdf"


    return pdf