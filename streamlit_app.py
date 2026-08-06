# ==========================================
# JianpuTool MVP 1.3
# Streamlit FINAL
#
# Audio / MIDI
# ↓
# BasicPitch MIDI
# ↓
# MusicXML Clean
# ↓
# Jianpu Fix
# ↓
# Jianpu-ly
# ↓
# LY Cleaner
# ↓
# LilyPond PDF
#
# Output:
# MIDI
# MusicXML
# Staff PDF
# Jianpu PDF
# ==========================================


import streamlit as st
import os
import uuid
import subprocess
import sys
import traceback



# ==========================================
# Page
# ==========================================

st.set_page_config(
    page_title="JianpuTool MVP 1.3",
    page_icon="🎵"
)


st.title(
    "🎵 JianpuTool MVP 1.3"
)


st.write(
"""
MP3 / WAV / MIDI → Jianpu PDF

Pipeline:

Audio
↓
BasicPitch MIDI
↓
MusicXML
↓
Jianpu
↓
LilyPond PDF


輸出：

🎹 MIDI

🎼 MusicXML

🎼 五線譜 PDF

🔢 簡譜 PDF
"""
)



# ==========================================
# command
# ==========================================

def run_cmd(cmd):

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
        # Audio -> MIDI
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
            "產生 LilyPond..."
        )


        with open(
            raw_ly,
            "w",
            encoding="utf-8"
        ) as f:


            result = subprocess.run(
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


            if result.returncode != 0:

                raise Exception(
                    result.stderr
                )


        st.success(
            "LY 產生完成"
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


        jianpu_pdf = (
            pdf_base
            +
            ".pdf"
        )



        # ==================================
        # Download
        # ==================================

        st.divider()

        st.header(
            "📥 下載輸出"
        )



        # MIDI

        if os.path.exists(midi_file):

            with open(
                midi_file,
                "rb"
            ) as f:


                st.download_button(
                    "🎹 下載 MIDI",
                    f,
                    file_name="melody.mid",
                    mime="audio/midi"
                )



        # MusicXML

        if os.path.exists(final_xml):

            with open(
                final_xml,
                "rb"
            ) as f:


                st.download_button(
                    "🎼 下載 MusicXML",
                    f,
                    file_name="score.musicxml",
                    mime="application/xml"
                )



        # Jianpu PDF

        if os.path.exists(jianpu_pdf):

            with open(
                jianpu_pdf,
                "rb"
            ) as f:


                st.download_button(
                    "🔢 下載簡譜 PDF",
                    f,
                    file_name="jianpu.pdf",
                    mime="application/pdf"
                )



        # Staff PDF

        staff_base = os.path.join(
            outdir,
            "staff"
        )


        run_cmd(
            [
                "lilypond",
                "-o",
                staff_base,
                "--pdf",
                final_ly
            ]
        )


        staff_pdf = (
            staff_base
            +
            ".pdf"
        )


        if os.path.exists(staff_pdf):


            with open(
                staff_pdf,
                "rb"
            ) as f:


                st.download_button(
                    "🎼 下載五線譜 PDF",
                    f,
                    file_name="staff.pdf",
                    mime="application/pdf"
                )



        st.success(
            "🎉 全部完成"
        )



    except Exception:


        st.error(
            "❌ 轉換失敗"
        )


        st.code(
            traceback.format_exc()
        )