import os
import sys
import subprocess
import shutil


def create_pdf(
    musicxml_file,
    pdf_file
):

    print("🎼 MusicXML → Jianpu")


    if not os.path.isfile(
        musicxml_file
    ):

        raise Exception(
            f"找不到 MusicXML: {musicxml_file}"
        )


    work_dir = os.path.dirname(
        pdf_file
    )


    if work_dir == "":
        work_dir = "."


    os.makedirs(
        work_dir,
        exist_ok=True
    )


    ly_file = os.path.join(
        work_dir,
        "score.ly"
    )


    print("轉換 jianpu-ly...")


    with open(
        ly_file,
        "w",
        encoding="utf-8"
    ) as f:


        result = subprocess.run(

            [
                sys.executable,
                "-m",
                "jianpu_ly",
                musicxml_file
            ],

            stdout=f,

            stderr=subprocess.STDOUT,

            text=True

        )


    if result.returncode != 0:

        with open(
            ly_file,
            "r",
            encoding="utf-8",
            errors="ignore"
        ) as f:

            error = f.read()


        raise Exception(
            "jianpu-ly失敗\n"
            + error
        )


    if not os.path.isfile(
        ly_file
    ):

        raise Exception(
            "找不到 LilyPond .ly"
        )


    print(
        "產生:",
        ly_file
    )


    print(
        "LilyPond 編譯..."
    )


    output_prefix = os.path.splitext(
        pdf_file
    )[0]


    result = subprocess.run(

        [
            "lilypond",
            "-o",
            output_prefix,
            ly_file
        ],

        stdout=subprocess.PIPE,

        stderr=subprocess.STDOUT,

        text=True

    )


    print(
        result.stdout
    )


    if result.returncode != 0:

        raise Exception(
            "LilyPond失敗\n"
            + result.stdout
        )


    generated_pdf = (
        output_prefix
        +
        ".pdf"
    )


    if not os.path.isfile(
        generated_pdf
    ):

        raise Exception(
            "PDF沒有產生"
        )


    if generated_pdf != pdf_file:

        shutil.move(
            generated_pdf,
            pdf_file
        )


    print(
        "完成:",
        pdf_file
    )



if __name__ == "__main__":


    if len(sys.argv) < 3:

        print(
            "用法:"
        )

        print(
            "python jianpu_pdf.py input.musicxml output.pdf"
        )

        sys.exit(1)



    create_pdf(

        sys.argv[1],

        sys.argv[2]

    )