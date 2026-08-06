import subprocess
import sys


def export(xml):

    subprocess.run(
        [
        "python",
        "-m",
        "jianpu_ly",
        xml
        ],
        check=True
    )


if __name__=="__main__":

    export(sys.argv[1])