# streamlit_app.py
#
# JianpuTool MVP 1.2.3
#
# MP3 / WAV / MIDI
#        ↓
# MIDI
#        ↓
# MusicXML
#        ↓
# Jianpu-ly
#        ↓
# LilyPond
#        ↓
# Jianpu PDF


import streamlit as st
import os
import uuid
import shutil
import subprocess
import sys
import traceback


# ==========================
# Page
# ==========================

st.set_page_config(
    page_title="JianpuTool MVP 1.2.3",
    page_icon="🎵"
)


st.title("🎵 JianpuTool MVP 1.2.3")


st.write(
"""
MP3 / WAV / MIDI → MIDI → MusicXML → 簡譜 PDF

Pipeline:

Audio
↓
BasicPitch
↓
MIDI
↓
MusicXML Clean
↓
jianpu-ly
↓
LilyPond
↓
PDF
"""
)


# ==========================
# Path
# ==========================

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


# ==========================
# Upload
# ==========================

uploaded = st.file_uploader(
    "上傳 MP3 / WAV / MIDI",
    type=[
        "mp3",
        "wav",
        "mid",
        "midi"
    ]
)


# ==========================
# Helper
# ==========================

def run_command(cmd):

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
# Main
# ==========================

if uploaded:

    job_id = str(uuid.uuid4())[:8]


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
        uploaded.name
    )


    with open(
        input_file,
        "wb"
    ) as f:

        f.write(
            uploaded.getbuffer()
        )


    st.success(
        f"上傳完成: {uploaded.name}"
    )


    st.info(
        f"工作目錄: {workdir}"
    )


    ext = uploaded.name.lower().split(".")[-1]


    try:

        # ==========================
        # MIDI
        # ==========================

        if ext in [
            "mid",
            "midi"
        ]:

            midi_file = input_file


        else:

            st.warning(
                "Audio 轉 MIDI 功能啟動"
            )


            midi_file = os.path.join(
                workdir,
                "audio.mid"
            )


            cmd = [
                sys.executable,
                "basicpitch_convert.py",
                input_file,
                midi_file
            ]


            run_command(cmd)



        st.success(
            "MIDI 完成"
        )
# ==========================
        # MIDI → MusicXML
        # ==========================

        st.info(
            "🎼 MIDI → MusicXML"
        )


        musicxml_file = os.path.join(
            workdir,
            "clean.musicxml"
        )


        cmd = [
            sys.executable,
            "midi_to_musicxml_clean.py",
            midi_file,
            musicxml_file
        ]


        run_command(cmd)


        if not os.path.exists(
            musicxml_file
        ):

            raise Exception(
                "MusicXML 產生失敗"
            )


        st.success(
            "MusicXML 完成"
        )



        # ==========================
        # Jianpu-ly
        # ==========================

        st.info(
            "🎵 MusicXML → jianpu.ly"
        )


        cmd = [
            sys.executable,
            "-m",
            "jianpu_ly",
            musicxml_file
        ]


        run_command(cmd)



        ly_file = os.path.join(
            workdir,
            "clean.ly"
        )


        if not os.path.exists(
            ly_file
        ):

            # jianpu-ly 有些版本輸出名稱不同
            for f in os.listdir(workdir):

                if f.endswith(".ly"):

                    ly_file = os.path.join(
                        workdir,
                        f
                    )
                    break



        if not os.path.exists(
            ly_file
        ):

            raise Exception(
                "找不到 LilyPond .ly 檔"
            )


        st.success(
            "jianpu.ly 完成"
        )



        # ==========================
        # LilyPond PDF
        # ==========================

        st.info(
            "📄 LilyPond 產生 PDF"
        )


        lilypond = "lilypond"


        pdf_cmd = [
            lilypond,
            "-o",
            os.path.join(
                workdir,
                "jianpu"
            ),
            ly_file
        ]


        run_command(
            pdf_cmd
        )



        pdf_file = os.path.join(
            workdir,
            "jianpu.pdf"
        )


        if not os.path.exists(
            pdf_file
        ):

            raise Exception(
                "PDF 產生失敗"
            )



        st.success(
            "🎉 簡譜 PDF 完成!"
        )


        # ==========================
        # Download
        # ==========================

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



    except Exception as e:


        st.error(
            "轉換錯誤"
        )


        st.exception(
            e
        )


        st.code(
            traceback.format_exc()
        )
