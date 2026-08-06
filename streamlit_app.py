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
    page_title="JianpuTool Professional MVP 2.2.3",
    page_icon="🎵",
    layout="centered"
)


st.title("🎵 JianpuTool Professional MVP 2.2.3")

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
# Run command
# ==================================================

def run_cmd(cmd, cwd=None):

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

    st.text(result.stdout)

    if result.returncode != 0:

        raise Exception(
            result.stdout
        )

    return result.stdout



# ==================================================
# Find file
# ==================================================

def find_file(folder, ext):

    folder = Path(folder)

    files = list(
        folder.glob(ext)
    )

    if len(files):

        return files[0]

    return None



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


    with open(input_file,"wb") as f:

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


    vocal_candidates = list(
        BASE_DIR.glob(
            "separated/htdemucs/**/vocals.wav"
        )
    )


    if not vocal_candidates:

        raise Exception(
            "找不到 vocals.wav"
        )


    vocal_wav = vocal_candidates[0]


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
            str(BASE_DIR / "basicpitch_convert.py"),
            str(vocal_wav),
            str(vocal_mid)
        ],
        cwd=BASE_DIR
    )


    st.success(
        "MIDI 完成"
    )
 # ==================================================
    # 3 Melody Clean Pro
    # ==================================================

    st.subheader(
        "🎹 3. Melody Clean Pro"
    )


    vocal_clean = job_dir / "vocal_clean.mid"


    run_cmd(
        [
            PYTHON,
            str(BASE_DIR / "melody_clean_pro.py"),
            str(vocal_mid),
            str(vocal_clean)
        ],
        cwd=BASE_DIR
    )


    st.success(
        "旋律清理完成"
    )


    # ==================================================
    # 4 MIDI -> MusicXML
    # ==================================================

    st.subheader(
        "🎼 4. MIDI → MusicXML"
    )


    raw_xml = job_dir / "raw.musicxml"


    run_cmd(
        [
            PYTHON,
            str(
                BASE_DIR /
                "midi_to_musicxml_clean_v42_2_pro.py"
            ),
            str(vocal_clean),
            str(raw_xml)
        ],
        cwd=BASE_DIR
    )


    st.success(
        "MusicXML 建立完成"
    )


    # ==================================================
    # 5 Jianpu Safe Fix
    # ==================================================

    st.subheader(
        "🛠 5. Jianpu Safe Fix"
    )


    fixed_xml = job_dir / "fixed.musicxml"


    run_cmd(
        [
            PYTHON,
            str(
                BASE_DIR /
                "jianpu_safe_fix.py"
            ),
            str(raw_xml),
            str(fixed_xml)
        ],
        cwd=BASE_DIR
    )


    st.success(
        "MusicXML 修正完成"
    )


    # ==================================================
    # 6 Final Quantize
    # ==================================================

    st.subheader(
        "⏱ 6. Final Quantize"
    )


    final_xml = job_dir / "final.musicxml"


    run_cmd(
        [
            PYTHON,
            str(
                BASE_DIR /
                "final_quantize.py"
            ),
            str(fixed_xml),
            str(final_xml)
        ],
        cwd=BASE_DIR
    )


    st.success(
        "節奏量化完成"
    )


    # ==================================================
    # 7 Measure Check
    # ==================================================

    st.subheader(
        "🔍 7. Measure Check"
    )


    run_cmd(
        [
            PYTHON,
            str(
                BASE_DIR /
                "check_measure.py"
            ),
            str(final_xml)
        ],
        cwd=BASE_DIR
    )


    st.success(
        "小節檢查完成"
    )
 # ==================================================
    # 8 MusicXML -> Jianpu
    # ==================================================

    st.subheader(
        "🎵 8. MusicXML → Jianpu"
    )


    # jianpu-ly 輸出目錄
    # ==================================================
# 8 MusicXML -> Jianpu
# ==================================================

st.subheader(
    "🎵 8. MusicXML → Jianpu"
)


ly_file = job_dir / "jianpu.ly"


cmd = [

    PYTHON,

    "-m",

    "jianpu_ly",

    str(final_xml)

]


with open(
    ly_file,
    "w",
    encoding="utf-8"
) as f:


    result = subprocess.run(

        cmd,

        cwd=str(job_dir),

        stdout=f,

        stderr=subprocess.PIPE,

        text=True

    )



if result.returncode != 0:

    raise Exception(

        "jianpu-ly錯誤:\n"

        +

        result.stderr

    )



if not ly_file.exists():

    raise Exception(

        "jianpu-ly 未產生 jianpu.ly"

    )


st.success(
    f"產生 LilyPond: {ly_file}"
)

    st.success(
        f"找到 LilyPond: {ly_file}"
    )



    # ==================================================
    # 9 LilyPond PDF
    # ==================================================

    st.subheader(
        "🎼 9. LilyPond PDF"
    )


    run_cmd(
        [
            "lilypond",
            "-o",
            str(job_dir / "jianpu"),
            str(ly_file)
        ],
        cwd=ly_dir
    )



    pdf_file = job_dir / "jianpu.pdf"



    if not pdf_file.exists():

        pdf_candidates = list(
            job_dir.glob("*.pdf")
        )


        if pdf_candidates:

            pdf_file = pdf_candidates[0]



    if not pdf_file.exists():

        raise Exception(
            "LilyPond 未產生 PDF"
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
            label="⬇️ 下載簡譜 PDF",
            data=f,
            file_name="jianpu.pdf",
            mime="application/pdf"
        )


    st.balloons()