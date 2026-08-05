# ==========================================
# JianpuTool MVP 1.2.3
# Streamlit FINAL
#
# Audio / MIDI
# ↓
# BasicPitch MIDI
# ↓
# MusicXML Clean
# ↓
# Jianpu-ly
# ↓
# LY Cleaner
# ↓
# LilyPond PDF
# ==========================================


import streamlit as st
import os
import uuid
import subprocess
import sys
import shutil
import traceback



st.set_page_config(
    page_title="JianpuTool MVP 1.2.3",
    page_icon="🎵"
)



st.title(
    "🎵 JianpuTool MVP 1.2.3"
)


st.write(
"""
MP3 / WAV / MIDI → Jianpu PDF

Pipeline:

Audio
↓
BasicPitch MIDI
↓
MusicXML Clean
↓
Jianpu-LY
↓
LY Cleaner
↓
LilyPond PDF
"""
)



# ==========================================
# command
# ==========================================


def run_cmd(
    cmd,
    cwd=None
):

    st.code(
        " ".join(cmd)
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
            "執行失敗"
        )



# ==========================================
# upload
# ==========================================


uploaded = st.file_uploader(
    "上傳 MP3 / WAV / MIDI",
    type=[
        "mp3",
        "wav",
        "mid",
        "midi"
    ]
)



if uploaded:


    uid = str(uuid.uuid4())[:8]


    outdir = os.path.join(
        "outputs",
        uid
    )


    os.makedirs(
        outdir,
        exist_ok=True
    )



    input_file = os.path.join(
        outdir,
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



    try:


        ext = uploaded.name.lower().split(".")[-1]



        # ==================================
        # MIDI
        # ==================================

        if ext in [
            "mid",
            "midi"
        ]:


            midi_file = input_file



        else:


            st.info(
                "Audio → MIDI"
            )


            midi_file = os.path.join(
                outdir,
                "melody.mid"
            )


            run_cmd(
            [
                sys.executable,
                "basicpitch_convert.py",
                input_file,
                midi_file
            ]
            )



        # ==================================
        # MIDI -> MusicXML
        # ==================================


        raw_xml = os.path.join(
            outdir,
            "raw.musicxml"
        )


        run_cmd(
        [
            sys.executable,
            "midi_to_musicxml_clean.py",
            midi_file,
            raw_xml
        ]
        )



        # ==================================
        # Clean MusicXML
        # ==================================


        clean_xml = os.path.join(
            outdir,
            "clean.musicxml"
        )


        run_cmd(
        [
            sys.executable,
            "clean_musicxml.py",
            raw_xml,
            clean_xml
        ]
        )



        # ==================================
        # Jianpu Fix
        # ==================================


        final_xml = os.path.join(
            outdir,
            "final.musicxml"
        )


        run_cmd(
        [
            sys.executable,
            "jianpu_fix_musicxml.py",
            clean_xml,
            final_xml
        ]
        )



        # ==================================
        # MusicXML -> LY
        # ==================================


        raw_ly = os.path.join(
            outdir,
            "final_raw.ly"
        )


        final_ly = os.path.join(
            outdir,
            "final.ly"
        )



        st.info(
            "產生 LilyPond 檔..."
        )



        with open(
            raw_ly,
            "w",
            encoding="utf-8"
        ) as f:


            subprocess.run(
            [
                sys.executable,
                "-m",
                "jianpu_ly",
                final_xml
            ],
            stdout=f,
            stderr=subprocess.PIPE,
            text=True
            )



        st.success(
            "LY raw完成"
        )



        # ==================================
        # LY Cleaner
        # ==================================


        run_cmd(
        [
            sys.executable,
            "jianpu_ly_cleaner.py",
            raw_ly,
            final_ly
        ]
        )



        # ==================================
        # LilyPond PDF
        # ==================================


        pdf_base = os.path.join(
            outdir,
            "jianpu"
        )


        run_cmd(
        [
            "lilypond",
            "-o",
            pdf_base,
            "--pdf",
            final_ly
        ]
        )



        pdf_file = (
            pdf_base
            +
            ".pdf"
        )


        if os.path.exists(pdf_file):

            st.success(
                "🎉 PDF完成"
            )


            with open(
                pdf_file,
                "rb"
            ) as f:


                st.download_button(
                    "下載 Jianpu PDF",
                    f,
                    file_name="jianpu.pdf"
                )


        else:

            raise Exception(
                "PDF不存在"
            )



    except Exception:


        st.error(
            "轉換失敗"
        )


        st.code(
            traceback.format_exc()
        )