#
# streamlit_app.py
#
# JianpuTool MVP 1.1.1
#

import streamlit as st
import os
import uuid
import subprocess
import sys
import traceback


st.set_page_config(
    page_title="JianpuTool MVP 1.1",
    page_icon="🎵"
)


st.title("🎵 JianpuTool MVP 1.1")

st.write(
"""
MP3 / WAV / MIDI → Jianpu PDF

Pipeline:

MP3/WAV:
Audio
↓
BasicPitch
↓
MIDI
↓
MusicXML Clean
↓
jianpu-fix V17
↓
jianpu-ly
↓
LilyPond PDF


MIDI:
MIDI
↓
Melody Extract
↓
MusicXML
↓
jianpu-ly
↓
LilyPond PDF
"""
)


OUTPUT_DIR = "outputs"

os.makedirs(
    OUTPUT_DIR,
    exist_ok=True
)



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


    st.text(result.stdout)


    if result.returncode != 0:

        raise Exception(
            result.stdout
        )




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


    file_id = str(uuid.uuid4())[:8]


    input_file = os.path.join(
        OUTPUT_DIR,
        file_id + "_" + uploaded.name
    )


    with open(
        input_file,
        "wb"
    ) as f:

        f.write(
            uploaded.getbuffer()
        )



    st.success(
        "上傳完成"
    )



    ext = uploaded.name.lower().split(".")[-1]



    try:


        # ======================
        # MIDI
        # ======================

        if ext in [
            "mid",
            "midi"
        ]:


            st.subheader(
                "🎼 MIDI → MusicXML"
            )


            raw_musicxml = os.path.join(
                OUTPUT_DIR,
                file_id+"_raw.musicxml"
            )



            run_cmd(
                [
                    sys.executable,
                    "midi_to_musicxml_clean.py",
                    input_file,
                    raw_musicxml
                ]
            )



            final_musicxml = raw_musicxml



        # ======================
        # Audio
        # ======================

        else:


            st.subheader(
                "🎧 Audio → MIDI"
            )


            midi_file = os.path.join(
                OUTPUT_DIR,
                file_id+".mid"
            )


            run_cmd(
                [
                    sys.executable,
                    "basicpitch_convert.py",
                    input_file,
                    midi_file
                ]
            )



            raw_musicxml = os.path.join(
                OUTPUT_DIR,
                file_id+"_raw.musicxml"
            )


            run_cmd(
                [
                    sys.executable,
                    "midi_to_musicxml_clean.py",
                    midi_file,
                    raw_musicxml
                ]
            )



            clean_musicxml = os.path.join(
                OUTPUT_DIR,
                file_id+"_clean.musicxml"
            )


            st.subheader(
                "修正 MusicXML"
            )


            run_cmd(
                [
                    sys.executable,
                    "clean_musicxml.py",
                    raw_musicxml,
                    clean_musicxml
                ]
            )



            final_musicxml = os.path.join(
                OUTPUT_DIR,
                file_id+"_final.musicxml"
            )


            run_cmd(
                [
                    sys.executable,
                    "jianpu_fix_musicxml.py",
                    clean_musicxml,
                    final_musicxml
                ]
            )



        # ======================
        # jianpu-ly
        # ======================

        st.subheader(
            "🎹 MusicXML → LilyPond"
        )


        run_cmd(
            [
                sys.executable,
                "-m",
                "jianpu_ly",
                final_musicxml
            ]
        )



        # 找 ly

        ly_file = None


        for f in os.listdir(
            OUTPUT_DIR
        ):

            if (
                f.endswith(".ly")
                and file_id in f
            ):

                ly_file = os.path.join(
                    OUTPUT_DIR,
                    f
                )


        if ly_file is None:

            raise Exception(
                "找不到 LilyPond 檔案"
            )



        st.subheader(
            "📄 LilyPond PDF"
        )



        run_cmd(
            [
                "lilypond",
                "-o",
                OUTPUT_DIR,
                ly_file
            ]
        )



        pdf_file = ly_file.replace(
            ".ly",
            ".pdf"
        )


        if os.path.exists(pdf_file):

            st.success(
                "完成 PDF"
            )


            with open(
                pdf_file,
                "rb"
            ) as f:


                st.download_button(
                    "下載簡譜 PDF",
                    f,
                    file_name="jianpu.pdf"
                )


        else:

            raise Exception(
                "PDF產生失敗"
            )



    except Exception as e:


        st.error(
            "轉換錯誤"
        )


        st.exception(e)