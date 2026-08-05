import streamlit as st
import os
import uuid
import subprocess
import sys
import shutil


# ==========================
# Page
# ==========================

st.set_page_config(
    page_title="JianpuTool MVP 1.5",
    page_icon="🎵"
)


st.title("🎵 JianpuTool MVP 1.5")

st.write(
"""
MP3 / WAV / MIDI → Jianpu PDF

Pipeline:

Audio
↓
MIDI
↓
MusicXML
↓
Jianpu
↓
LilyPond PDF
"""
)



# ==========================
# Command
# ==========================

def run_cmd(cmd):

    st.code(" ".join(cmd))

    result = subprocess.run(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True
    )

    st.text(result.stdout)

    if result.returncode != 0:
        raise Exception(result.stdout)



# ==========================
# Upload
# ==========================

upload = st.file_uploader(
    "上傳 MP3 / WAV / MIDI",
    type=[
        "mp3",
        "wav",
        "mid",
        "midi"
    ]
)



if upload:


    uid = str(uuid.uuid4())[:8]

    output_dir = os.path.join(
        "outputs",
        uid
    )

    os.makedirs(
        output_dir,
        exist_ok=True
    )


    input_file = os.path.join(
        output_dir,
        upload.name
    )


    with open(
        input_file,
        "wb"
    ) as f:

        f.write(
            upload.getbuffer()
        )


    st.success(
        "上傳完成"
    )


    try:


        # ======================
        # MIDI
        # ======================

        if upload.name.lower().endswith(
            (".mid",".midi")
        ):

            midi_file = input_file


        else:

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
        # MIDI -> MusicXML
        # ======================

        raw_xml = os.path.join(
            output_dir,
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



        # ======================
        # clean
        # ======================

        clean_xml = os.path.join(
            output_dir,
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



        # ======================
        # final fix
        # ======================

        final_xml = os.path.join(
            output_dir,
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



        # ======================
        # jianpu-ly
        # ======================

        run_cmd(
            [
                sys.executable,
                "-m",
                "jianpu_ly",
                final_xml
            ]
        )



        # ======================
        # 找 ly
        # ======================

        ly_files = []


        for f in os.listdir(output_dir):

            if f.endswith(".ly"):

                ly_files.append(f)



        if not ly_files:

            raise Exception(
                "jianpu_ly 沒有產生 .ly"
            )



        source_ly = os.path.join(
            output_dir,
            ly_files[0]
        )


        fixed_ly = os.path.join(
            output_dir,
            "final_fix.ly"
        )



        # ======================
        # ly fix
        # ======================

        run_cmd(
            [
                sys.executable,
                "ly_fix_v1.py",
                source_ly,
                fixed_ly
            ]
        )



        if not os.path.exists(
            fixed_ly
        ):

            raise Exception(
                "final_fix.ly 不存在"
            )



        # ======================
        # LilyPond
        # ======================

        run_cmd(
            [
                "lilypond",
                "-o",
                os.path.join(
                    output_dir,
                    "jianpu"
                ),
                fixed_ly
            ]
        )



        pdf = os.path.join(
            output_dir,
            "jianpu.pdf"
        )


        if os.path.exists(pdf):

            st.success(
                "🎉 完成"
            )


            with open(
                pdf,
                "rb"
            ) as f:

                st.download_button(
                    "下載簡譜 PDF",
                    f,
                    file_name="jianpu.pdf",
                    mime="application/pdf"
                )


        else:

            raise Exception(
                "PDF 沒有產生"
            )



    except Exception as e:


        st.error(
            "轉換失敗"
        )

        st.exception(e)