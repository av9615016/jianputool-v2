import sys
import os
import subprocess
import shutil


# ==================================
# JianpuTool PDF Generator V2
# MusicXML -> Jianpu -> LilyPond -> PDF
# ==================================


def run_cmd(cmd):

    result = subprocess.run(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True
    )

    print(result.stdout)

    if result.returncode != 0:

        raise Exception(
            "\n".join(
                [
                    "Command failed:",
                    " ".join(cmd),
                    result.stdout
                ]
            )
        )



# ==================================
# Create PDF
# ==================================

def create_pdf(
        musicxml_file,
        pdf_file
):


    print(
        "🎼 MusicXML → Jianpu"
    )


    if not os.path.isfile(
        musicxml_file
    ):

        raise Exception(
            "找不到 MusicXML:"
            + musicxml_file
        )



    # ------------------------------
    # Output folder
    # ------------------------------

    pdf_dir = os.path.dirname(
        pdf_file
    )


    if pdf_dir == "":

        pdf_dir = "."


    os.makedirs(
        pdf_dir,
        exist_ok=True
    )



    # ------------------------------
    # Temporary jianpu folder
    # ------------------------------

    work_dir = os.path.join(
        pdf_dir,
        "jianpu_work"
    )


    os.makedirs(
        work_dir,
        exist_ok=True
    )


    ly_file = os.path.join(
        work_dir,
        "score.ly"
    )



    # ------------------------------
    # jianpu-ly
    # ------------------------------

    print(
        "轉換 jianpu-ly..."
    )


    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "jianpu_ly",
            musicxml_file
        ],
        cwd=work_dir,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True
    )


    print(
        result.stdout
    )


    if result.returncode != 0:

        raise Exception(
            "jianpu-ly失敗\n"
            +
            result.stdout
        )



    # 找 ly

    found = None


    for root,dirs,files in os.walk(
        work_dir
    ):

        for f in files:

            if f.endswith(
                ".ly"
            ):

                found = os.path.join(
                    root,
                    f
                )


    if found is None:

        raise Exception(
            "找不到 .ly 檔"
        )


    if found != ly_file:

        shutil.copy(
            found,
            ly_file
        )



    print(
        "LilyPond:"
        ,
        ly_file
    )



    # ------------------------------
    # LilyPond
    # ------------------------------

    print(
        "產生 PDF..."
    )


    output_base = os.path.join(
        pdf_dir,
        "jianpu"
    )


    run_cmd(
        [
            "lilypond",
            "-o",
            output_base,
            ly_file
        ]
    )



    generated_pdf = output_base + ".pdf"



    if not os.path.isfile(
        generated_pdf
    ):

        raise Exception(
            "LilyPond沒有產生PDF"
        )



    shutil.copy(
        generated_pdf,
        pdf_file
    )



    print(
        "完成:",
        pdf_file
    )




# ==================================
# Main
# ==================================

if __name__ == "__main__":


    if len(sys.argv) < 3:


        print(
            "使用:"
        )


        print(
            "python jianpu_pdf.py input.musicxml output.pdf"
        )


        sys.exit(1)



    create_pdf(
        sys.argv[1],
        sys.argv[2]
    )