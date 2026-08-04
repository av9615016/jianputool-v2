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
    page_title="JianpuTool MVP 1.1",
    page_icon="🎵"
)


st.title("🎵 JianpuTool MVP 1.1")

st.write(
"""
MP3 / WAV / MIDI → MIDI → MusicXML → Jianpu PDF

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
LilyPond PDF
"""
)


# ==========================
# PATH
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
# command
# ==========================

def run_cmd(cmd):

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

    st.text(result.stdout)

    if result.returncode != 0:

        raise Exception(
            result.stdout
        )


# ==========================
# find file
# ==========================

def find_file(folder, ext):

    files = []

    for f in os.listdir(folder):

        if f.lower().endswith(ext):

            files.append(
                os.path.join(folder,f)
            )

    if files:
        return files[0]

    return None



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


    uid = uuid.uuid4().hex[:8]


    input_file = os.path.join(
        OUTPUT_DIR,
        f"{uid}_{uploaded.name}"
    )


    with open(
        input_file,
        "wb"
    ) as f:

        f.write(
            uploaded.read()
        )


    st.success(
        "上傳完成"
    )


    if st.button(
        "開始轉換 🎵"
    ):


        try:


            # ---------------------
            # MIDI
            # ---------------------

            if uploaded.name.lower().endswith(
                (".mid",".midi")
            ):

                midi_file=input_file


            else:


                st.info(
                    "🎧 Audio → MIDI"
                )


                midi_file=os.path.join(
                    OUTPUT_DIR,
                    f"{uid}.mid"
                )


                run_cmd(
                [
                    sys.executable,
                    "basicpitch_convert.py",
                    input_file,
                    midi_file
                ]
                )



            if not os.path.exists(midi_file):

                raise Exception(
                    "MIDI沒有產生"
                )



            # ---------------------
            # MIDI -> MusicXML
            # ---------------------

            st.info(
                "🎼 MIDI → MusicXML"
            )


            raw_xml=os.path.join(
                OUTPUT_DIR,
                f"{uid}_raw.musicxml"
            )


            run_cmd(
            [
                sys.executable,
                "midi_to_musicxml_clean.py",
                midi_file,
                raw_xml
            ]
            )



            # ---------------------
            # Clean
            # ---------------------

            st.info(
                "修正 MusicXML"
            )


            clean_xml=os.path.join(
                OUTPUT_DIR,
                f"{uid}_clean.musicxml"
            )


            run_cmd(
            [
                sys.executable,
                "clean_musicxml.py",
                raw_xml,
                clean_xml
            ]
            )



            # ---------------------
            # Final
            # ---------------------

            final_xml=os.path.join(
                OUTPUT_DIR,
                f"{uid}_final.musicxml"
            )


            if os.path.exists(
                "jianpu_fix_musicxml.py"
            ):


                run_cmd(
                [
                    sys.executable,
                    "jianpu_fix_musicxml.py",
                    clean_xml,
                    final_xml
                ]
                )

            else:

                shutil.copy(
                    clean_xml,
                    final_xml
                )



            # ---------------------
            # jianpu-ly
            # ---------------------

            st.info(
                "🎹 MusicXML → LilyPond"
            )


            run_cmd(
            [
                sys.executable,
                "-m",
                "jianpu_ly",
                final_xml
            ]
            )



            # 找 ly

            ly_file=find_file(
                OUTPUT_DIR,
                ".ly"
            )


            if ly_file is None:

                raise Exception(
                    "jianpu_ly沒有產生 .ly"
                )


            st.success(
                f"找到 LilyPond: {ly_file}"
            )



            # ---------------------
            # LilyPond PDF
            # ---------------------

            st.info(
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



            pdf_file=find_file(
                OUTPUT_DIR,
                ".pdf"
            )


            if pdf_file:


                st.success(
                    "🎉 完成!"
                )


                with open(
                    pdf_file,
                    "rb"
                ) as f:

                    st.download_button(
                        "下載簡譜 PDF",
                        f,
                        file_name=os.path.basename(pdf_file)
                    )


            else:

                raise Exception(
                    "PDF沒有產生"
                )



        except Exception as e:


            st.error(
                "轉換錯誤"
            )


            st.exception(e)



# ==========================
# debug
# ==========================

with st.expander(
    "檢查 outputs"
):

    for f in os.listdir(
        OUTPUT_DIR
    ):

        st.write(f)