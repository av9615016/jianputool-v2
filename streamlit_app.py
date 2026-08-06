import streamlit as st
import os
import sys
import uuid
import subprocess
import shutil
from pathlib import Path


# ==================================================
# Page
# ==================================================

st.set_page_config(
    page_title="JianpuTool Professional MVP 2.2.5",
    page_icon="🎵",
    layout="centered"
)


st.title(
    "🎵 JianpuTool Professional MVP 2.2.5"
)


st.write(
"""
AI Vocal → MIDI → MusicXML → Jianpu PDF

Pipeline:

MP3/WAV
↓
🎤 Demucs Vocal Separation
↓
🎼 BasicPitch AI Melody
↓
🎹 Melody Clean Pro
↓
📄 MusicXML
↓
🎵 Jianpu-ly
↓
🎼 LilyPond PDF
"""
)



# ==================================================
# Path
# ==================================================

BASE_DIR = Path(__file__).parent.resolve()

OUTPUT_DIR = BASE_DIR / "outputs"

OUTPUT_DIR.mkdir(
    exist_ok=True
)


PYTHON = sys.executable



# ==================================================
# Find LilyPond
# ==================================================

def find_lilypond():


    candidates = [

        "lilypond",

        "/usr/bin/lilypond",

        "/usr/local/bin/lilypond",

        "C:/lilypond-2.26.0/bin/lilypond.exe"

    ]


    for p in candidates:

        if shutil.which(p):

            return p


        if Path(p).exists():

            return p


    return None




# ==================================================
# Run command
# ==================================================

def run_cmd(cmd,cwd=None):


    st.code(
        " ".join(str(x) for x in cmd)
    )


    result = subprocess.run(

        cmd,

        cwd=cwd,

        stdout=subprocess.PIPE,

        stderr=subprocess.STDOUT,

        text=True

    )


    st.text(
        result.stdout
    )


    if result.returncode != 0:

        raise Exception(
            result.stdout
        )


    return result.stdout




# ==================================================
# Upload
# ==================================================

upload = st.file_uploader(

    "上傳歌曲 MP3 / WAV",

    type=[
        "mp3",
        "wav"
    ]

)



if upload:


    job_id = str(
        uuid.uuid4()
    )


    job_dir = OUTPUT_DIR / job_id


    job_dir.mkdir(
        exist_ok=True
    )



    input_file = job_dir / upload.name



    with open(
        input_file,
        "wb"
    ) as f:

        f.write(
            upload.getbuffer()
        )


    st.success(
        "歌曲上傳完成"
    )



    # ==================================================
    # 1 Demucs
    # ==================================================

    st.subheader(
        "🎤 1. Vocal Separation"
    )


    run_cmd(

        [

            PYTHON,

            "-m",

            "demucs",

            "--two-stems=vocals",

            "-n",

            "htdemucs",

            str(input_file)

        ],

        cwd=BASE_DIR

    )



    vocals = list(

        BASE_DIR.glob(

            "separated/htdemucs/**/vocals.wav"

        )

    )


    if not vocals:

        raise Exception(
            "找不到 vocals.wav"
        )


    vocal_wav = vocals[0]



    st.success(
        f"取得人聲: {vocal_wav}"
    )




    # ==================================================
    # 2 BasicPitch
    # ==================================================

    st.subheader(
        "🎼 2. BasicPitch AI Melody"
    )


    vocal_mid = job_dir / "vocal.mid"


    run_cmd(

        [

            PYTHON,

            str(BASE_DIR/"basicpitch_convert.py"),

            str(vocal_wav),

            str(vocal_mid)

        ],

        cwd=BASE_DIR

    )



    st.success(
        "MIDI 完成"
    )



    # ==================================================
    # 3 Melody Clean
    # ==================================================

    st.subheader(
        "🎹 3. Melody Clean Pro"
    )


    vocal_clean = job_dir/"vocal_clean.mid"



    run_cmd(

        [

            PYTHON,

            str(BASE_DIR/"melody_clean_pro.py"),

            str(vocal_mid),

            str(vocal_clean)

        ],

        cwd=BASE_DIR

    )


    st.success(
        "旋律清理完成"
    )




    # ==================================================
    # 4 MIDI XML
    # ==================================================

    st.subheader(
        "🎼 4. MIDI → MusicXML"
    )


    raw_xml = job_dir/"raw.musicxml"



    run_cmd(

        [

            PYTHON,

            str(
                BASE_DIR/
                "midi_to_musicxml_clean_v42_2_pro.py"
            ),

            str(vocal_clean),

            str(raw_xml)

        ],

        cwd=BASE_DIR

    )



    st.success(
        "MusicXML 完成"
    )




    # ==================================================
    # 5 Safe Fix
    # ==================================================

    fixed_xml = job_dir/"fixed.musicxml"


    st.subheader(
        "🛠 5. Jianpu Safe Fix"
    )


    run_cmd(

        [

            PYTHON,

            str(BASE_DIR/"jianpu_safe_fix.py"),

            str(raw_xml),

            str(fixed_xml)

        ],

        cwd=BASE_DIR

    )



    # ==================================================
    # 6 Quantize
    # ==================================================

    final_xml = job_dir/"final.musicxml"


    st.subheader(
        "⏱ 6. Final Quantize"
    )


    run_cmd(

        [

            PYTHON,

            str(BASE_DIR/"final_quantize.py"),

            str(fixed_xml),

            str(final_xml)

        ],

        cwd=BASE_DIR

    )




    # ==================================================
    # 7 Check
    # ==================================================

    st.subheader(
        "🔍 7. Measure Check"
    )


    run_cmd(

        [

            PYTHON,

            str(BASE_DIR/"check_measure.py"),

            str(final_xml)

        ],

        cwd=BASE_DIR

    )




    # ==================================================
    # 8 Jianpu ly
    # ==================================================

    st.subheader(
        "🎵 8. MusicXML → Jianpu"
    )


    ly_file = job_dir/"jianpu.ly"



    result = subprocess.run(

        [

            PYTHON,

            "-m",

            "jianpu_ly",

            str(final_xml)

        ],

        cwd=job_dir,

        stdout=subprocess.PIPE,

        stderr=subprocess.PIPE,

        text=True

    )


    if result.returncode !=0:

        raise Exception(
            result.stderr
        )



    with open(
        ly_file,
        "w",
        encoding="utf-8"
    ) as f:

        f.write(
            result.stdout
        )



    if not ly_file.exists():

        raise Exception(
            "jianpu.ly 建立失敗"
        )



    st.success(
        "jianpu.ly 完成"
    )




    # ==================================================
    # 9 LilyPond
    # ==================================================

    st.subheader(
        "🎼 9. LilyPond PDF"
    )


    lilypond = find_lilypond()


    if not lilypond:

        raise Exception(
            "找不到 LilyPond"
        )



    run_cmd(

        [

            lilypond,

            "-o",

            str(job_dir/"jianpu"),

            str(ly_file)

        ],

        cwd=str(job_dir)

    )



    pdf_file = job_dir/"jianpu.pdf"



    if not pdf_file.exists():

        raise Exception(
            "PDF產生失敗"
        )



    st.success(
        "🎉 簡譜 PDF 完成"
    )




    # ==================================================
    # Download
    # ==================================================

    with open(
        pdf_file,
        "rb"
    ) as f:


        st.download_button(

            "⬇️ 下載簡譜 PDF",

            f,

            file_name="jianpu.pdf",

            mime="application/pdf"

        )


    st.balloons()