# ============================================================
# JianpuTool Professional MVP 2.2.2
#
# MP3/WAV
#   ↓
# Demucs Vocal Separation
#   ↓
# BasicPitch AI Melody
#   ↓
# Melody Clean Pro
#   ↓
# MIDI → MusicXML
#   ↓
# Jianpu Safe Fix
#   ↓
# Final Quantize
#   ↓
# Jianpu-ly
#   ↓
# LilyPond PDF
#
# Streamlit Cloud Absolute Path Edition
# ============================================================

import streamlit as st
import os
import sys
import uuid
import subprocess
import shutil


# ============================================================
# BASE PATH FIX
# ============================================================

BASE_DIR = os.path.dirname(
    os.path.abspath(__file__)
)


OUTPUT_DIR = os.path.join(
    BASE_DIR,
    "outputs"
)


os.makedirs(
    OUTPUT_DIR,
    exist_ok=True
)


# ============================================================
# PAGE
# ============================================================

st.set_page_config(
    page_title="JianpuTool Professional MVP 2.2.2",
    page_icon="🎵"
)


st.title(
    "🎵 JianpuTool Professional MVP 2.2.2"
)


st.write(
"""
AI Vocal → MIDI → MusicXML → 簡譜 PDF

Professional Pipeline:

MP3/WAV
↓
🎤 Vocal Separation
↓
🎼 BasicPitch AI Melody
↓
🎹 Melody Clean Pro
↓
📄 MusicXML
↓
🎵 Jianpu PDF
"""
)



# ============================================================
# RUN COMMAND
# ============================================================

def run(cmd):

    st.code(
        " ".join(cmd)
    )

    result = subprocess.run(
        cmd,
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



# ============================================================
# UPLOAD
# ============================================================

uploaded = st.file_uploader(
    "上傳歌曲 MP3 / WAV",
    type=[
        "mp3",
        "wav"
    ]
)



if uploaded:


    job_id = str(uuid.uuid4())


    workdir = os.path.join(
        OUTPUT_DIR,
        job_id
    )


    os.makedirs(
        workdir,
        exist_ok=True
    )


    input_file = os.path.join(
        workdir,
        "input" + os.path.splitext(uploaded.name)[1]
    )


    with open(
        input_file,
        "wb"
    ) as f:

        f.write(
            uploaded.getbuffer()
        )


    st.success(
        "歌曲上傳完成"
    )


    # ========================================================
    # 1 VOCAL SEPARATION
    # ========================================================

    st.subheader(
        "🎤 1. Vocal Separation"
    )


    run([

        sys.executable,

        "-m",
        "demucs",

        "--two-stems=vocals",

        "-n",
        "htdemucs",

        input_file

    ])



    # Demucs output

    song_name = os.path.splitext(
        os.path.basename(input_file)
    )[0]


    vocal_file = os.path.join(

        BASE_DIR,

        "separated",

        "htdemucs",

        song_name,

        "vocals.wav"

    )


    if not os.path.exists(vocal_file):

        # Cloud path fallback

        vocal_file = os.path.join(

            BASE_DIR,

            "separated",

            "htdemucs",

            os.path.splitext(
                os.path.basename(input_file)
            )[0],

            "vocals.wav"

        )


    st.write(
        "取得人聲:",
        vocal_file
    )


    # ========================================================
    # 2 BASIC PITCH
    # ========================================================

    st.subheader(
        "🎼 2. BasicPitch AI Melody"
    )


    midi_file = os.path.join(
        workdir,
        "vocal.mid"
    )


    run([

        sys.executable,

        os.path.join(
            BASE_DIR,
            "basicpitch_convert.py"
        ),

        vocal_file,

        midi_file

    ])


    st.success(
        "MIDI 完成"
    )


    # ========================================================
    # 3 MELODY CLEAN
    # ========================================================

    st.subheader(
        "🎹 3. Melody Clean Pro"
    )


    clean_mid = os.path.join(
        workdir,
        "vocal_clean.mid"
    )


    run([

        sys.executable,

        os.path.join(
            BASE_DIR,
            "melody_clean_pro.py"
        ),

        midi_file,

        clean_mid

    ])


    st.success(
        "旋律清理完成"
    )
  # ========================================================
    # 4 MIDI → MUSICXML
    # ========================================================

    st.subheader(
        "🎼 4. MIDI → MusicXML"
    )


    raw_xml = os.path.join(
        workdir,
        "raw.musicxml"
    )


    run([

        sys.executable,

        os.path.join(
            BASE_DIR,
            "midi_to_musicxml_clean.py"
        ),

        clean_mid,

        raw_xml

    ])


    st.success(
        "MusicXML 建立完成"
    )



    # ========================================================
    # 5 JIANPU SAFE FIX
    # ========================================================

    st.subheader(
        "🛠 5. Jianpu Safe Fix"
    )


    fixed_xml = os.path.join(
        workdir,
        "fixed.musicxml"
    )


    run([

        sys.executable,

        os.path.join(
            BASE_DIR,
            "jianpu_safe_fix.py"
        ),

        raw_xml,

        fixed_xml

    ])



    # ========================================================
    # 6 FINAL QUANTIZE
    # ========================================================

    st.subheader(
        "⏱ 6. Final Quantize"
    )


    final_xml = os.path.join(
        workdir,
        "final.musicxml"
    )


    run([

        sys.executable,

        os.path.join(
            BASE_DIR,
            "final_quantize.py"
        ),

        fixed_xml,

        final_xml

    ])


    st.success(
        "節奏量化完成"
    )



    # ========================================================
    # CHECK FILE
    # ========================================================

    if not os.path.exists(final_xml):

        raise Exception(
            "final.musicxml 不存在"
        )



    # ========================================================
    # 7 MEASURE CHECK
    # ========================================================

    st.subheader(
        "🔍 7. Measure Check"
    )


    run([

        sys.executable,

        os.path.join(
            BASE_DIR,
            "check_measure.py"
        ),

        final_xml

    ])



    # ========================================================
    # 8 JIANPU-LY
    # ========================================================

    st.subheader(
        "🎵 8. MusicXML → Jianpu"
    )


    #
    # jianpu-ly 必須在檔案目錄執行
    #

    old_dir = os.getcwd()


    os.chdir(workdir)


    try:

        run([

            sys.executable,

            "-m",

            "jianpu_ly",

            "final.musicxml"

        ])


    finally:

        os.chdir(old_dir)



    ly_file = os.path.join(
        workdir,
        "backup.ly"
    )


    if not os.path.exists(ly_file):

        raise Exception(
            "jianpu-ly 未產生 backup.ly"
        )



    st.success(
        "Jianpu LilyPond 完成"
    )



    # ========================================================
    # 9 LILYPOND PDF
    # ========================================================

    st.subheader(
        "📄 9. LilyPond PDF"
    )


    run([

        "lilypond",

        ly_file

    ])



    pdf_file = os.path.join(
        workdir,
        "backup.pdf"
    )


    if not os.path.exists(pdf_file):

        raise Exception(
            "PDF 產生失敗"
        )


    st.success(
        "🎉 簡譜 PDF 完成"
    )



    # ========================================================
    # DOWNLOAD
    # ========================================================

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


    st.info(
        f"輸出位置: {pdf_file}"
    )