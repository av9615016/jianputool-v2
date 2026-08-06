# ============================================================
# JianpuTool Professional MVP 2.3
#
# MP3/WAV
#   |
#   v
# Audio Preprocess
#   |
#   v
# Vocal Only Separation
#   |
#   v
# BasicPitch
#   |
#   v
# Melody Clean Pro
#   |
#   v
# MusicXML
#   |
#   v
# Jianpu Safe Fix
#   |
#   v
# Quantize
#   |
#   v
# Jianpu PDF
#
# ============================================================


import streamlit as st
import os
import sys
import uuid
import glob
import hashlib
import subprocess
import shutil


# ============================================================
# Page
# ============================================================

st.set_page_config(
    page_title="JianpuTool Professional MVP 2.3",
    page_icon="🎵"
)


st.title(
    "🎵 JianpuTool Professional MVP 2.3"
)


st.write(
"""
AI Vocal → MIDI → MusicXML → 簡譜 PDF

Professional Pipeline:

MP3/WAV
 ↓
🎤 Vocal Only Separation
 ↓
🎼 BasicPitch AI
 ↓
🎹 Melody Clean Pro
 ↓
📄 Jianpu PDF
"""
)



# ============================================================
# Command
# ============================================================

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



# ============================================================
# Cache
# ============================================================

CACHE_DIR = "cache"

os.makedirs(
    CACHE_DIR,
    exist_ok=True
)


def file_hash(path):

    h = hashlib.md5()

    with open(path,"rb") as f:

        while True:

            data = f.read(8192)

            if not data:
                break

            h.update(data)


    return h.hexdigest()



# ============================================================
# Upload
# ============================================================


mode = st.radio(
    "轉換模式",
    [
        "快速模式",
        "專業模式"
    ]
)



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


    song_id = file_hash(
        input_file
    )


    cache_path = os.path.join(
        CACHE_DIR,
        song_id
    )


    os.makedirs(
        cache_path,
        exist_ok=True
    )


    st.success(
        "歌曲上傳完成"
    )



    # ========================================================
    # Professional Mode
    # ========================================================

    if mode == "專業模式":

        st.subheader(
            "🎤 Vocal Separation Only"
        )


        cached_vocal = os.path.join(
            cache_path,
            "vocals.wav"
        )


        if os.path.exists(
            cached_vocal
        ):

            st.info(
                "使用快取 Vocal"
            )

            vocal_file = cached_vocal


        else:


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


            shutil.copy(
                vocal_file,
                cached_vocal
            )


        st.success(
            "Vocal 完成"
        )


    else:

        # 快速模式直接使用原音

        vocal_file = input_file


        st.info(
            "快速模式：跳過 Vocal Separation"
        )
 # ========================================================
    # BasicPitch
    # ========================================================

    st.subheader(
        "🎼 BasicPitch AI Melody"
    )


    vocal_mid = os.path.join(
        work,
        "vocal.mid"
    )


    cached_mid = os.path.join(
        cache_path,
        "vocal.mid"
    )


    if os.path.exists(
        cached_mid
    ):


        st.info(
            "使用 MIDI 快取"
        )


        shutil.copy(
            cached_mid,
            vocal_mid
        )


    else:


        run([
            sys.executable,
            "basicpitch_convert.py",
            vocal_file,
            vocal_mid
        ])


        shutil.copy(
            vocal_mid,
            cached_mid
        )



    st.success(
        "MIDI 產生完成"
    )



    # ========================================================
    # Melody Clean Pro
    # ========================================================

    st.subheader(
        "🎹 Melody Clean Pro"
    )


    clean_mid = os.path.join(
        work,
        "clean.mid"
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



    # ========================================================
    # MIDI → MusicXML
    # ========================================================

    st.subheader(
        "🎼 MIDI → MusicXML"
    )


    raw_xml = os.path.join(
        work,
        "raw.musicxml"
    )


    run([
        sys.executable,
        "midi_to_musicxml_clean.py",
        clean_mid,
        raw_xml
    ])



    st.success(
        "MusicXML 建立完成"
    )



    # ========================================================
    # Jianpu Safe Fix
    # ========================================================

    st.subheader(
        "🛠 Jianpu Safe Fix"
    )


    fixed_xml = os.path.join(
        work,
        "fixed.musicxml"
    )


    run([
        sys.executable,
        "jianpu_safe_fix.py",
        raw_xml,
        fixed_xml
    ])



    st.success(
        "MusicXML 修正完成"
    )



    # ========================================================
    # Final Quantize
    # ========================================================

    st.subheader(
        "⏱ Final Quantize"
    )


    final_xml = os.path.join(
        work,
        "final.musicxml"
    )


    run([
        sys.executable,
        "final_quantize.py",
        fixed_xml,
        final_xml
    ])



    st.success(
        "節奏量化完成"
    )



    # ========================================================
    # Cache MusicXML
    # ========================================================

    shutil.copy(
        final_xml,
        os.path.join(
            cache_path,
            "final.musicxml"
        )
    )
# ========================================================
    # Measure Check
    # ========================================================

    st.subheader(
        "🔍 Measure Check"
    )


    run([
        sys.executable,
        "check_measure.py",
        final_xml
    ])


    st.success(
        "✅ 小節檢查通過"
    )



    # ========================================================
    # Jianpu LY
    # ========================================================

    st.subheader(
        "🎵 MusicXML → Jianpu"
    )


    cached_pdf = os.path.join(
        cache_path,
        "jianpu.pdf"
    )


    if os.path.exists(
        cached_pdf
    ):

        st.info(
            "使用 PDF 快取"
        )


        pdf_file = cached_pdf


    else:


        run([
            sys.executable,
            "-m",
            "jianpu_ly",
            final_xml
        ])



        # 找 ly

        ly_files = glob.glob(
            "**/*.ly",
            recursive=True
        )


        if not ly_files:

            raise Exception(
                "找不到 ly 檔"
            )


        ly_file = ly_files[-1]



        # ====================================================
        # LilyPond PDF
        # ====================================================

        st.subheader(
            "📄 LilyPond PDF"
        )


        run([
            "lilypond",
            ly_file
        ])



        pdf_files = glob.glob(
            "**/*.pdf",
            recursive=True
        )


        if not pdf_files:

            raise Exception(
                "找不到 PDF"
            )


        pdf_file = pdf_files[-1]


        shutil.copy(
            pdf_file,
            cached_pdf
        )



    # ========================================================
    # Download
    # ========================================================


    st.success(
        "🎉 Jianpu PDF 完成"
    )


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