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
PDF
"""
)


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



# =========================
# LilyPond
# =========================

def find_lilypond():

    p = shutil.which(
        "lilypond"
    )

    if p:
        return p


    paths = [

        "/usr/bin/lilypond",

        "/usr/local/bin/lilypond",

        "C:\\lilypond-2.26.0\\bin\\lilypond.exe"

    ]


    for x in paths:

        if os.path.exists(x):

            return x


    return None



LILYPOND = find_lilypond()


st.write(
    "🎼 LilyPond:",
    LILYPOND
)



# =========================
# Command
# =========================

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



# =========================
# 找檔案
# =========================

def find_file(folder, names):


    for n in names:

        p = os.path.join(
            folder,
            n
        )

        if os.path.exists(p):

            return p


    return None



# =========================
# Upload
# =========================


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


    uid = str(uuid.uuid4())


    work = os.path.join(
        OUTPUT_DIR,
        uid
    )


    os.makedirs(
        work,
        exist_ok=True
    )


    input_file = os.path.join(
        work,
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
        "上傳完成"
    )



    if st.button(
        "🎼 開始轉換"
    ):


        try:


            current = input_file



            # =================
            # Audio → MIDI
            # =================


            if uploaded.name.lower().endswith(
                (
                    ".mp3",
                    ".wav"
                )
            ):


                st.info(
                    "🎤 Audio → MIDI"
                )


                run_cmd(
                    [
                        sys.executable,
                        "basicpitch_convert.py",
                        current,
                        work
                    ]
                )


                current = find_file(
                    work,
                    [
                        "melody.mid",
                        "output.mid",
                        "converted.mid"
                    ]
                )


                if current is None:

                    raise Exception(
                        "找不到 MIDI"
                    )



            # =================
            # MIDI → MusicXML
            # =================


            st.info(
                "🎹 MIDI → MusicXML"
            )


            run_cmd(
                [
                    sys.executable,
                    "midi_to_musicxml_clean.py",
                    current,
                    work
                ]
            )



            st.write(
                "輸出檔案:",
                os.listdir(work)
            )



            musicxml = find_file(
                work,
                [
                    "raw.musicxml",
                    "output.musicxml",
                    "melody.musicxml",
                    "fixed.musicxml"
                ]
            )



            if musicxml is None:

                raise Exception(
                    "找不到 MusicXML\n"
                    + str(os.listdir(work))
                )



            st.success(
                f"MusicXML: {musicxml}"
            )



            # =================
            # Clean
            # =================


            st.info(
                "🧹 Clean MusicXML"
            )


            run_cmd(
                [
                    sys.executable,
                    "clean_musicxml.py",
                    musicxml,
                    work
                ]
            )



            clean_xml = find_file(
                work,
                [
                    "clean.musicxml",
                    "clean_fixed.musicxml"
                ]
            )


            if clean_xml is None:

                raise Exception(
                    "沒有產生 clean.musicxml"
                )



            # =================
            # Final Fix
            # =================


            st.info(
                "🎼 Final MusicXML Fix"
            )


            run_cmd(
                [
                    sys.executable,
                    "jianpu_fix_musicxml.py",
                    clean_xml,
                    work
                ]
            )



            final_xml = find_file(
                work,
                [
                    "final.musicxml",
                    "fixed2.musicxml"
                ]
            )


            if final_xml is None:

                raise Exception(
                    "沒有 final.musicxml"
                )



            # =================
            # Jianpu Ly
            # =================


            st.info(
                "🎵 MusicXML → LilyPond"
            )


            run_cmd(
                [
                    sys.executable,
                    "-m",
                    "jianpu_ly",
                    final_xml
                ]
            )



            ly = "final.ly"


            if not os.path.exists(ly):

                raise Exception(
                    "沒有產生 final.ly"
                )



            # =================
            # PDF
            # =================


            if LILYPOND is None:

                raise Exception(
                    "找不到 LilyPond"
                )


            st.info(
                "📄 LilyPond PDF"
            )


            run_cmd(
                [
                    LILYPOND,
                    "-fpdf",
                    ly
                ]
            )



            pdf="final.pdf"



            if os.path.exists(pdf):


                st.success(
                    "🎉 完成!"
                )


                with open(
                    pdf,
                    "rb"
                ) as f:


                    st.download_button(
                        "⬇️ 下載簡譜 PDF",
                        f,
                        file_name="jianpu.pdf",
                        mime="application/pdf"
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