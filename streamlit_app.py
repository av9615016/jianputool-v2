import streamlit as st
import os
import uuid
import subprocess
import sys
import traceback


# ==========================
# Page
# ==========================

st.set_page_config(
    page_title="JianpuTool MVP 1.2.4",
    page_icon="🎵"
)


st.title("🎵 JianpuTool MVP 1.2.4")


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
Jianpu Fix
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
# Execute
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
        # Audio → MIDI
        # ==========================

        if ext in [
            "mid",
            "midi"
        ]:

            midi_file = input_file

            st.info(
                "使用 MIDI 輸入"
            )


        else:

            st.info(
                "🎧 BasicPitch Audio → MIDI"
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


            run_command(
                cmd
            )


        if not os.path.exists(
            midi_file
        ):

            raise Exception(
                "MIDI 產生失敗"
            )


        st.success(
            "MIDI 完成"
        )



        # ==========================
        # MIDI → MusicXML
        # ==========================

        st.info(
            "🎼 MIDI → MusicXML"
        )


        raw_xml = os.path.join(
            workdir,
            "raw.musicxml"
        )


        cmd = [
            sys.executable,
            "midi_to_musicxml_clean.py",
            midi_file,
            raw_xml
        ]


        run_command(
            cmd
        )



        # ==========================
        # Clean MusicXML
        # ==========================

        clean_xml = os.path.join(
            workdir,
            "clean.musicxml"
        )


        st.info(
            "🧹 Clean MusicXML"
        )


        cmd = [
            sys.executable,
            "clean_musicxml.py",
            raw_xml,
            clean_xml
        ]


        run_command(
            cmd
        )



        # ==========================
        # Jianpu Fix
        # ==========================

        final_xml = os.path.join(
            workdir,
            "final.musicxml"
        )


        st.info(
            "🎵 Jianpu MusicXML Fix"
        )


        cmd = [
            sys.executable,
            "jianpu_fix_musicxml.py",
            clean_xml,
            final_xml
        ]


        run_command(
            cmd
        )



        # ==========================
        # jianpu-ly
        # ==========================

        st.info(
            "🎵 MusicXML → jianpu.ly"
        )


        cmd = [
            sys.executable,
            "-m",
            "jianpu_ly",
            final_xml
        ]


        run_command(
            cmd
        )


        ly_file = None


        for f in os.listdir(workdir):

            if f.endswith(".ly"):

                ly_file = os.path.join(
                    workdir,
                    f
                )

                break


        if ly_file is None:

            raise Exception(
                "找不到 .ly 檔案"
            )



        # ==========================
        # LilyPond
        # ==========================

        st.info(
            "📄 LilyPond PDF"
        )


        cmd = [
            "lilypond",
            "-o",
            os.path.join(
                workdir,
                "jianpu"
            ),
            ly_file
        ]


        run_command(
            cmd
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


        with open(
            pdf_file,
            "rb"
        ) as f:

            st.download_button(
                "⬇️ 下載簡譜 PDF",
                f,
                file_name="jianpu.pdf",
                mime="application/pdf"
            )


        st.balloons()



    except Exception as e:


        st.error(
            "❌ 轉換錯誤"
        )


        st.exception(
            e
        )


        st.code(
            traceback.format_exc()
        )