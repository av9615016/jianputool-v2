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
    page_title="JianpuTool MVP 1.3",
    page_icon="🎵"
)


st.title("🎵 JianpuTool MVP 1.3")

st.write(
"""
MP3 / WAV / MIDI → MIDI → MusicXML → Jianpu PDF

Pipeline:

Audio
↓
BasicPitch MIDI
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


OUTPUT_ROOT = os.path.join(
    BASE_DIR,
    "outputs"
)


os.makedirs(
    OUTPUT_ROOT,
    exist_ok=True
)



# ==========================
# run command
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


    st.text(
        result.stdout
    )


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


    job_id = str(
        uuid.uuid4()
    )[:8]


    output_dir = os.path.join(
        OUTPUT_ROOT,
        job_id
    )


    os.makedirs(
        output_dir,
        exist_ok=True
    )


    input_file = os.path.join(
        output_dir,
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



    try:


        ext = uploaded.name.lower()



        # ======================
        # MIDI
        # ======================

        if ext.endswith(
            (".mid",".midi")
        ):

            midi_file = input_file


        else:

            st.info(
                "🎧 Audio → MIDI"
            )


            midi_file = os.path.join(
                output_dir,
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




        # ======================
        # MIDI → MusicXML
        # ======================


        raw_xml = os.path.join(
            output_dir,
            "raw.musicxml"
        )


        st.info(
            "🎼 MIDI → MusicXML"
        )


        run_cmd(
            [
                sys.executable,
                "midi_to_musicxml_clean.py",
                midi_file,
                raw_xml
            ]
        )



        # ======================
        # CLEAN
        # ======================


        clean_xml = os.path.join(
            output_dir,
            "clean.musicxml"
        )


        st.info(
            "🧹 Clean MusicXML"
        )


        run_cmd(
            [
                sys.executable,
                "clean_musicxml.py",
                raw_xml,
                clean_xml
            ]
        )



        # ======================
        # JIANPU FIX
        # ======================


        final_xml = os.path.join(
            output_dir,
            "final.musicxml"
        )


        st.info(
            "🔢 Jianpu Fix"
        )


        run_cmd(
            [
                sys.executable,
                "jianpu_fix_musicxml.py",
                clean_xml,
                final_xml
            ]
        )



        # ======================
        # jianpu-ly
        # ======================


        st.info(
            "🎼 產生 LilyPond"
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

        ly_file = None


        for f in os.listdir(BASE_DIR):

            if f.endswith(".ly"):

                ly_file = os.path.join(
                    BASE_DIR,
                    f
                )


        if ly_file:

            shutil.move(
                ly_file,
                os.path.join(
                    output_dir,
                    "final.ly"
                )
            )



        ly_file = os.path.join(
            output_dir,
            "final.ly"
        )



        # ======================
        # LilyPond PDF
        # ======================


        st.info(
            "📄 LilyPond PDF"
        )


        run_cmd(
            [
                "lilypond",
                "-o",
                os.path.join(
                    output_dir,
                    "final"
                ),
                "--pdf",
                ly_file
            ]
        )



        st.success(
            "🎉 完成"
        )



        # ======================
        # DOWNLOAD
        # ======================


        st.subheader(
            "⬇️ 下載輸出"
        )



        files = [

            (
                "🎹 MIDI",
                midi_file,
                "melody.mid"
            ),


            (
                "🎼 MusicXML",
                final_xml,
                "score.musicxml"
            ),


            (
                "📄 PDF",
                os.path.join(
                    output_dir,
                    "final.pdf"
                ),
                "score.pdf"
            ),

        ]



        for title,path,name in files:


            if os.path.exists(path):


                with open(
                    path,
                    "rb"
                ) as f:


                    st.download_button(

                        title,

                        f,

                        file_name=name

                    )


            else:

                st.warning(
                    f"找不到 {name}"
                )




    except Exception:


        st.error(
            "❌ 轉換失敗"
        )


        st.code(
            traceback.format_exc()
        )