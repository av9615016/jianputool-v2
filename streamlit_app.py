# =====================================================
# streamlit_app_professional_mvp2.2.py
#
# JianpuTool Professional MVP 2.2
#
# MP3/WAV
# ↓
# Demucs Vocal
# ↓
# BasicPitch
# ↓
# Melody MIDI
# ↓
# MusicXML
# ↓
# Final Quantize
# ↓
# Jianpu Safe Fix
# ↓
# Jianpu-ly
# ↓
# LilyPond PDF
#
# =====================================================


import streamlit as st
import os
import uuid
import subprocess
import glob
import shutil


# ===============================
# Page
# ===============================

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

Audio
↓
Vocal Separation
↓
BasicPitch
↓
Melody Tracking
↓
MusicXML
↓
Measure Check
↓
Safe Fix
↓
Jianpu PDF
"""
)



# ===============================
# Command Runner
# ===============================


def run(cmd):

    st.write(
        "執行:"
    )

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



# ===============================
# Upload
# ===============================


upload = st.file_uploader(
    "上傳 MP3 / WAV",
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
        "上傳完成"
    )



    # ===============================
    # Demucs
    # ===============================


    st.subheader(
        "🎤 1. Vocal Separation"
    )


    run([
        "python",
        "-m",
        "demucs",
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
        f"Vocal:{vocal_file}"
    )
 # ===============================
    # BasicPitch
    # ===============================


    st.subheader(
        "🎼 2. BasicPitch AI MIDI"
    )


    midi_file = os.path.join(
        work,
        "vocal.mid"
    )


    run([
        "python",
        "basicpitch_convert.py",
        vocal_file,
        midi_file
    ])



    if not os.path.exists(
        midi_file
    ):

        raise Exception(
            "MIDI 產生失敗"
        )


    st.success(
        "MIDI 完成"
    )



    # ===============================
    # Melody Clean Pro
    # ===============================


    st.subheader(
        "🎹 3. Melody Clean Pro"
    )


    clean_mid = os.path.join(
        work,
        "clean.mid"
    )


    run([
        "python",
        "melody_clean_pro.py",
        midi_file,
        clean_mid
    ])



    if not os.path.exists(
        clean_mid
    ):

        # fallback
        shutil.copy(
            midi_file,
            clean_mid
        )



    # ===============================
    # MIDI -> MusicXML
    # ===============================


    st.subheader(
        "🎼 4. MIDI → MusicXML"
    )


    musicxml = os.path.join(
        work,
        "raw.musicxml"
    )


    run([
        "python",
        "midi_to_musicxml_clean.py",
        clean_mid,
        musicxml
    ])



    if not os.path.exists(
        musicxml
    ):

        raise Exception(
            "MusicXML 產生失敗"
        )



    st.success(
        "MusicXML 完成"
    )



    # ===============================
    # Final Quantize
    # ===============================


    st.subheader(
        "⏱ 5. Final Quantize"
    )


    quantize_xml = os.path.join(
        work,
        "quantize.musicxml"
    )


    run([
        "python",
        "final_quantize.py",
        musicxml,
        quantize_xml
    ])



    if not os.path.exists(
        quantize_xml
    ):

        raise Exception(
            "Quantize 失敗"
        )



    # ===============================
    # Measure Check
    # ===============================


    st.subheader(
        "🔍 6. Measure Check"
    )


    run([
        "python",
        "check_measure.py",
        quantize_xml
    ])



    # ===============================
    # Jianpu Safe Fix
    # ===============================


    st.subheader(
        "🛡 7. Jianpu Safe Fix MVP 2.2"
    )


    safe_xml = os.path.join(
        work,
        "safe.musicxml"
    )


    run([
        "python",
        "jianpu_safe_fix.py",
        quantize_xml,
        safe_xml
    ])



    if not os.path.exists(
        safe_xml
    ):

        raise Exception(
            "Safe Fix 失敗"
        )


    st.success(
        "Safe MusicXML 完成"
    )
 # ===============================
    # MusicXML -> Jianpu LY
    # ===============================


    st.subheader(
        "🎵 8. MusicXML → Jianpu"
    )


    run([
        "python",
        "-m",
        "jianpu_ly",
        safe_xml
    ])



    # ===============================
    # 找 ly
    # ===============================


    st.subheader(
        "🎼 9. LilyPond"
    )


    ly_files = []


    search_paths = [
        work,
        ".",
        "/tmp"
    ]


    for path in search_paths:

        ly_files.extend(
            glob.glob(
                os.path.join(
                    path,
                    "*.ly"
                )
            )
        )


    if not ly_files:

        raise Exception(
            "找不到 jianpu .ly"
        )


    ly_file = ly_files[-1]


    st.success(
        f"LY:{ly_file}"
    )



    # ===============================
    # LilyPond PDF
    # ===============================


    run([
        "lilypond",
        ly_file
    ])



    # ===============================
    # 找 PDF
    # ===============================


    pdf_files = []


    for path in search_paths:

        pdf_files.extend(
            glob.glob(
                os.path.join(
                    path,
                    "*.pdf"
                )
            )
        )


    if not pdf_files:

        raise Exception(
            "PDF 產生失敗"
        )


    pdf = pdf_files[-1]



    st.success(
        "🎉 Jianpu PDF 完成"
    )



    # ===============================
    # Download
    # ===============================


    with open(
        pdf,
        "rb"
    ) as f:


        st.download_button(
            label="📄 下載簡譜 PDF",
            data=f,
            file_name="jianpu.pdf",
            mime="application/pdf"
        )



    st.balloons()
