# streamlit_app_professional_mvp2.2.py
#
# JianpuTool Professional MVP 2.2
#
# MP3/WAV
# ↓
# Demucs Vocal Only
# ↓
# BasicPitch
# ↓
# Melody Clean
# ↓
# MusicXML
# ↓
# Quantize
# ↓
# Jianpu PDF


import streamlit as st
import os
import uuid
import glob
import subprocess
import shutil
import sys


# ==========================
# Page
# ==========================

st.set_page_config(
    page_title="JianpuTool Professional MVP 2.2",
    page_icon="🎵"
)


st.title(
    "🎵 JianpuTool Professional MVP 2.2"
)


st.write(
"""
AI Vocal → MIDI → MusicXML → 簡譜 PDF

Professional Pipeline:

MP3/WAV
 ↓
🎤 Vocal Separation Only
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


# ==========================
# Command Runner
# ==========================

def run(cmd):

    st.write("執行:")

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


# ==========================
# Upload
# ==========================

upload = st.file_uploader(
    "上傳歌曲 MP3 / WAV",
    type=[
        "mp3",
        "wav"
    ]
)



if upload:


    work = os.path.join(
        "outputs",
        str(uuid.uuid4())
    )


    os.makedirs(
        work,
        exist_ok=True
    )


    input_file = os.path.join(
        work,
        "input.mp3"
    )


    with open(
        input_file,
        "wb"
    ) as f:

        f.write(
            upload.read()
        )


    st.success(
        "歌曲上傳完成"
    )



    # ==========================
    # Vocal Only Separation
    # ==========================

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



    vocals = glob.glob(
        "separated/**/vocals.wav",
        recursive=True
    )



    if not vocals:

        raise Exception(
            "找不到 vocals.wav"
        )


    vocal_file = vocals[-1]


    st.success(
        f"取得人聲: {vocal_file}"
    )



    # ==========================
    # BasicPitch
    # ==========================

    st.subheader(
        "🎼 2. BasicPitch AI Melody"
    )


    vocal_mid = os.path.join(
        work,
        "vocal.mid"
    )


    run([
        sys.executable,
        "basicpitch_convert.py",
        vocal_file,
        vocal_mid
    ])


    st.success(
        "MIDI 完成"
    )
  # ==========================
    # Melody Clean Pro
    # ==========================

    st.subheader(
        "🎹 3. Melody Clean Pro"
    )


    clean_mid = os.path.join(
        work,
        "vocal_clean.mid"
    )


    run([
        sys.executable,
        "melody_clean_pro.py",
        vocal_mid,
        clean_mid
    ])


    st.success(
        "旋律清理完成"
    )



    # ==========================
    # MIDI → MusicXML
    # ==========================

    st.subheader(
        "🎼 4. MIDI → MusicXML"
    )


    raw_musicxml = os.path.join(
        work,
        "raw.musicxml"
    )


    run([
        sys.executable,
        "midi_to_musicxml_clean.py",
        clean_mid,
        raw_musicxml
    ])


    st.success(
        "MusicXML 建立完成"
    )



    # ==========================
    # Jianpu Safe Fix
    # ==========================

    st.subheader(
        "🛠 5. Jianpu Safe Fix"
    )


    fixed_musicxml = os.path.join(
        work,
        "fixed.musicxml"
    )


    run([
        sys.executable,
        "jianpu_safe_fix.py",
        raw_musicxml,
        fixed_musicxml
    ])



    st.success(
        "MusicXML 修正完成"
    )



    # ==========================
    # Final Quantize
    # ==========================

    st.subheader(
        "⏱ 6. Final Quantize"
    )


    final_musicxml = os.path.join(
        work,
        "final.musicxml"
    )


    run([
        sys.executable,
        "final_quantize.py",
        fixed_musicxml,
        final_musicxml
    ])


    st.success(
        "節奏量化完成"
    )



    # ==========================
    # Measure Check
    # ==========================

    st.subheader(
        "🔍 7. Measure Check"
    )


    run([
        sys.executable,
        "check_measure.py",
        final_musicxml
    ])


    st.success(
        "✅ 小節檢查通過"
    )
# ==========================
    # MusicXML → Jianpu LilyPond
    # ==========================

    st.subheader(
        "🎵 8. MusicXML → Jianpu"
    )


    run([
        sys.executable,
        "-m",
        "jianpu_ly",
        final_musicxml
    ])



    # ==========================
    # 找 ly
    # ==========================

    ly_files = glob.glob(
        "*.ly"
    )


    if not ly_files:

        ly_files = glob.glob(
            "**/*.ly",
            recursive=True
        )


    if not ly_files:

        raise Exception(
            "找不到 jianpu.ly"
        )


    ly_file = ly_files[-1]


    st.success(
        f"產生: {ly_file}"
    )



    # ==========================
    # LilyPond PDF
    # ==========================

    st.subheader(
        "📄 9. LilyPond PDF"
    )


    run([
        "lilypond",
        ly_file
    ])



    # ==========================
    # 找 PDF
    # ==========================

    pdf_files = glob.glob(
        "*.pdf"
    )


    if not pdf_files:

        pdf_files = glob.glob(
            "**/*.pdf",
            recursive=True
        )



    if pdf_files:


        pdf = pdf_files[-1]


        st.success(
            "🎉 簡譜 PDF 完成"
        )


        with open(
            pdf,
            "rb"
        ) as f:


            st.download_button(
                label="⬇️ 下載簡譜 PDF",
                data=f,
                file_name="jianpu.pdf",
                mime="application/pdf"
            )


    else:

        raise Exception(
            "找不到 PDF"
        )