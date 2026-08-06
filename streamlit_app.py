# streamlit_app.py
#
# JianpuTool Professional MVP 2.2.1
#
# MP3/WAV
#   ↓
# Demucs Vocal Separation
#   ↓
# BasicPitch AI Melody
#   ↓
# Melody Clean Pro
#   ↓
# MIDI → MusicXML V42.2
#   ↓
# Jianpu Safe Fix
#   ↓
# Final Quantize
#   ↓
# Measure Check
#   ↓
# Jianpu-ly
#   ↓
# LilyPond PDF
#

import streamlit as st
import os
import uuid
import subprocess
import sys
import shutil


# ==========================
# Page
# ==========================

st.set_page_config(
    page_title="JianpuTool Professional MVP 2.2.1",
    page_icon="🎵"
)


st.title(
    "🎵 JianpuTool Professional MVP 2.2.1"
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
# Paths
# ==========================

BASE = os.getcwd()


OUTPUT_DIR = "outputs"


os.makedirs(
    OUTPUT_DIR,
    exist_ok=True
)



# ==========================
# Run command
# ==========================

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


    return result.stdout



# ==========================
# LilyPond Fix
# ==========================

def fix_lilypond_version(path):

    with open(
        path,
        "r",
        encoding="utf-8"
    ) as f:

        data = f.read()


    # jianpu-ly default
    data = data.replace(
        '\\version "2.20.0"',
        '\\version "2.26.0"'
    )


    with open(
        path,
        "w",
        encoding="utf-8"
    ) as f:

        f.write(data)



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


    uid = str(uuid.uuid4())


    workdir = os.path.join(
        OUTPUT_DIR,
        uid
    )


    os.makedirs(
        workdir,
        exist_ok=True
    )


    input_file = os.path.join(
        workdir,
        "input." + upload.name.split(".")[-1]
    )


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
 # ==========================
    # 1. Vocal Separation
    # ==========================

    st.subheader(
        "🎤 1. Vocal Separation"
    )


    vocal_dir = os.path.join(
        "separated",
        "htdemucs",
        "input"
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


    vocal_file = os.path.join(
        vocal_dir,
        "vocals.wav"
    )


    if not os.path.exists(vocal_file):

        raise Exception(
            "找不到 vocals.wav"
        )


    st.success(
        f"取得人聲: {vocal_file}"
    )



    # ==========================
    # 2. BasicPitch
    # ==========================

    st.subheader(
        "🎼 2. BasicPitch AI Melody"
    )


    midi_file = os.path.join(
        workdir,
        "vocal.mid"
    )


    run([
        sys.executable,
        "basicpitch_convert.py",
        vocal_file,
        midi_file
    ])


    st.success(
        "MIDI 完成"
    )



    # ==========================
    # 3. Melody Clean Pro
    # ==========================

    st.subheader(
        "🎹 3. Melody Clean Pro"
    )


    clean_midi = os.path.join(
        workdir,
        "vocal_clean.mid"
    )


    run([
        sys.executable,
        "melody_clean_pro.py",
        midi_file,
        clean_midi
    ])


    st.success(
        "旋律清理完成"
    )



    # ==========================
    # 4. MIDI → MusicXML
    # ==========================

    st.subheader(
        "🎼 4. MIDI → MusicXML"
    )


    raw_xml = os.path.join(
        workdir,
        "raw.musicxml"
    )


    run([
        sys.executable,
        "midi_to_musicxml_clean.py",
        clean_midi,
        raw_xml
    ])


    st.success(
        "MusicXML 建立完成"
    )



    # ==========================
    # 5. Jianpu Safe Fix
    # ==========================

    st.subheader(
        "🛠 5. Jianpu Safe Fix"
    )


    fixed_xml = os.path.join(
        workdir,
        "fixed.musicxml"
    )


    run([
        sys.executable,
        "jianpu_safe_fix.py",
        raw_xml,
        fixed_xml
    ])



    # ==========================
    # 6. Quantize
    # ==========================

    st.subheader(
        "⏱ 6. Final Quantize"
    )


    final_xml = os.path.join(
        workdir,
        "final.musicxml"
    )


    run([
        sys.executable,
        "final_quantize.py",
        fixed_xml,
        final_xml
    ])



    # ==========================
    # 7. Measure Check
    # ==========================

    st.subheader(
        "🔍 7. Measure Check"
    )


    run([
        sys.executable,
        "check_measure.py",
        final_xml
    ])



    # ==========================
    # 8. Jianpu-ly
    # ==========================

    st.subheader(
        "🎵 8. MusicXML → Jianpu"
    )


    old = os.getcwd()


    os.chdir(workdir)


    run([
        sys.executable,
        "-m",
        "jianpu_ly",
        "final.musicxml"
    ])


    os.chdir(old)



    # 找 ly

    ly_file = os.path.join(
        workdir,
        "backup.ly"
    )


    if not os.path.exists(ly_file):

        raise Exception(
            "jianpu_ly 沒有產生 backup.ly"
        )


    # ==========================
    # LilyPond Compatibility
    # ==========================

    st.subheader(
        "🔧 LilyPond Compatibility Fix"
    )


    fix_lilypond_version(
        ly_file
    )


    st.success(
        "LilyPond version patched"
    )



    # ==========================
    # 9. LilyPond PDF
    # ==========================

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


    # ==========================
    # Download
    # ==========================

    with open(
        pdf_file,
        "rb"
    ) as f:

        st.download_button(
            label="📥 下載簡譜 PDF",
            data=f,
            file_name="jianpu.pdf",
            mime="application/pdf"
        )