import streamlit as st
import os
import uuid
import subprocess
import sys
import shutil


st.set_page_config(
    page_title="JianpuTool MVP 1.1",
    page_icon="🎵"
)


st.title("🎵 JianpuTool MVP 1.1")


st.write(
"""
MP3 / WAV / MIDI → Jianpu PDF

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
Jianpu PDF
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
# 清除舊檔
# ==========================

def clear_outputs():

    for f in os.listdir(OUTPUT_DIR):

        path = os.path.join(
            OUTPUT_DIR,
            f
        )

        if os.path.isfile(path):

            os.remove(path)



# ==========================
# command
# ==========================

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


            # 清除舊檔
            clear_outputs()



            # -----------------
            # MIDI
            # -----------------

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



            # -----------------
            # MIDI -> MusicXML
            # -----------------

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



            # -----------------
            # clean
            # -----------------

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



            # -----------------
            # final
            # -----------------

            final_xml=os.path.join(
                OUTPUT_DIR,
                f"{uid}_final.musicxml"
            )


            run_cmd(
                [
                    sys.executable,
                    "jianpu_fix_musicxml.py",
                    clean_xml,
                    final_xml
                ]
            )



            # -----------------
            # jianpu-ly
            # -----------------

            st.info(
                "🎹 MusicXML → Jianpu LilyPond"
            )


            run_cmd(
                [
                    sys.executable,
                    "-m",
                    "jianpu_ly",
                    final_xml
                ]
            )



            # 固定抓自己的 ly

            ly_file = os.path.splitext(final_xml)[0] + ".ly"



            if not os.path.exists(ly_file):

                raise Exception(
                    f"找不到 {ly_file}"
                )



            st.success(
                f"產生: {ly_file}"
            )



            # -----------------
            # LilyPond
            # -----------------

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



            # 固定抓自己的 PDF

            pdf_file = os.path.splitext(ly_file)[0] + ".pdf"



            if not os.path.exists(pdf_file):

                raise Exception(
                    "PDF產生失敗"
                )



            st.success(
                "🎉 簡譜完成!"
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



        except Exception as e:


            st.error(
                "轉換錯誤"
            )


            st.exception(e)



# ==========================
# Debug
# ==========================

with st.expander(
    "outputs 檔案"
):

    for f in os.listdir(OUTPUT_DIR):

        st.write(f)