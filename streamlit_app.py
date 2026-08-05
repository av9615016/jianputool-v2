import streamlit as st
import os
import uuid
import subprocess
import sys
import shutil
import traceback


# ==========================
# Page
# ==========================

st.set_page_config(
    page_title="JianpuTool MVP 1.2",
    page_icon="🎵"
)


st.title("🎵 JianpuTool MVP 1.2")

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
LilyPond PDF
"""
)


# ==========================
# Paths
# ==========================

BASE_DIR = os.getcwd()

OUTPUT_DIR = os.path.join(
    BASE_DIR,
    "outputs"
)

os.makedirs(
    OUTPUT_DIR,
    exist_ok=True
)


# ==========================
# Helper
# ==========================


def run_cmd(cmd):

    st.code(
        " ".join(cmd),
        language="bash"
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
            "Command failed"
        )



def check_file(path):

    if not os.path.exists(path):

        raise FileNotFoundError(
            f"找不到檔案: {path}"
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



if uploaded:


    job_id = str(uuid.uuid4())[:8]


    job_dir = os.path.join(
        OUTPUT_DIR,
        job_id
    )


    os.makedirs(
        job_dir,
        exist_ok=True
    )


    input_file = os.path.join(
        job_dir,
        uploaded.name
    )


    with open(
        input_file,
        "wb"
    ) as f:

        f.write(
            uploaded.read()
        )


    st.success(
        f"上傳完成: {uploaded.name}"
    )


    if st.button(
        "🎼 開始轉換簡譜"
    ):


        try:


            st.info(
                "開始處理..."
            )


            # ---------------------
            # MIDI
            # ---------------------

            if uploaded.name.lower().endswith(
                (".mp3",".wav")
            ):


                midi_file = os.path.join(
                    job_dir,
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


            else:


                midi_file = input_file



            check_file(
                midi_file
            )


            st.success(
                "MIDI 完成"
            )



            # ---------------------
            # MIDI -> MusicXML
            # ---------------------


            raw_xml = os.path.join(
                job_dir,
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


            check_file(raw_xml)



            # ---------------------
            # Clean XML
            # ---------------------


            clean_xml = os.path.join(
                job_dir,
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


            check_file(clean_xml)



            # ---------------------
            # Jianpu Fix
            # ---------------------


            final_xml = os.path.join(
                job_dir,
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


            check_file(final_xml)



            # ---------------------
            # jianpu-ly
            # ---------------------


            run_cmd(
                [
                    sys.executable,
                    "-m",
                    "jianpu_ly",
                    final_xml
                ]
            )



            ly_file = final_xml.replace(
                ".musicxml",
                ".ly"
            )


            check_file(
                ly_file
            )



            # ---------------------
            # LilyPond
            # ---------------------


            run_cmd(
                [
                    "lilypond",
                    "--pdf",
                    ly_file
                ]
            )


            pdf_file = ly_file.replace(
                ".ly",
                ".pdf"
            )


            check_file(
                pdf_file
            )



            st.success(
                "🎉 簡譜 PDF 完成!"
            )



            # Download


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



        except Exception:


            st.error(
                "轉換失敗"
            )


            st.code(
                traceback.format_exc()
            )