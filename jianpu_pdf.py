"""
JianpuTool Professional MVP 2.4

MusicXML
→ Jianpu-ly
→ LilyPond
→ PDF
"""

import sys
import os
import subprocess
import shutil



def create_pdf(
    musicxml,
    output_dir
):


    os.makedirs(
        output_dir,
        exist_ok=True
    )


    basename=os.path.splitext(
        os.path.basename(musicxml)
    )[0]



    ly_file=os.path.join(
        output_dir,
        basename+".ly"
    )


    pdf_file=os.path.join(
        output_dir,
        basename+".pdf"
    )



    print("🎼 MusicXML → Jianpu")



    # MusicXML to LilyPond

    result=subprocess.run(
        [
            sys.executable,
            "-m",
            "jianpu_ly",
            musicxml
        ],
        capture_output=True,
        text=True
    )



    if result.returncode !=0:

        raise Exception(
            "jianpu-ly失敗\n"+
            result.stderr
        )



    # 找產生的 ly

    generated=None


    for f in os.listdir("."):

        if f.endswith(".ly"):

            generated=f



    if generated is None:

        raise Exception(
            "找不到 LilyPond 檔"
        )



    shutil.move(
        generated,
        ly_file
    )



    print(
        "🎹 LilyPond PDF"
    )



    subprocess.run(
        [
            "lilypond",
            "-o",
            os.path.join(
                output_dir,
                basename
            ),
            ly_file
        ],
        check=True
    )



    if not os.path.exists(pdf_file):

        raise Exception(
            "PDF產生失敗"
        )


    print(
        "完成:",
        pdf_file
    )


    return pdf_file





if __name__=="__main__":


    if len(sys.argv)<3:

        print(
        """
使用方式:

python jianpu_pdf.py input.musicxml output_folder

        """
        )

        sys.exit()



    create_pdf(
        sys.argv[1],
        sys.argv[2]
    )