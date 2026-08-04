import streamlit as st
import os
import uuid
import subprocess
import sys
import shutil
import traceback


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


BASE_DIR = os.path.dirname(os.path.abspath(__file__))

OUTPUT_DIR = os.path.join(
    BASE_DIR,
    "outputs"
)

os.makedirs(
    OUTPUT_DIR,
    exist_ok=True
)


# =========================
# 找 LilyPond
# =========================

def find_lilypond():

    path = shutil.which("lilypond")

    if path:
        return path


    candidates = [
        "/usr/bin/lilypond",
        "/usr/local/bin/lilypond",
        "C:\\lilypond-2.26.0\\bin\\lilypond.exe"
    ]


    for p in candidates:

        if os.path.exists(p):
            return p


    return None



LILYPOND = find_lilypond()


st.write(
    "🎼 LilyPond:",
    LILYPOND
)


if LILYPOND is None:

    st.warning(
        "找不到 LilyPond，請確認 packages.txt 已加入 lilypond"
    )



# =========================
# 執行指令
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
# 上傳
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

    input_file = os.path.join(
        OUTPUT_DIR,
        uid + "_" + uploaded.name
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
        "🎼 開始轉換"
    ):


        try:

            work = os.path.join(
                OUTPUT_DIR,
                uid
            )

            os.makedirs(
                work,
                exist_ok=True
            )


            current = input_file



            # =====================
            # MP3/WAV → MIDI
            # =====================

            if uploaded.name.lower().endswith(
                (".mp3",".wav")
            ):

                st.write(
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


                current = os.path.join(
                    work,
                    "melody.mid"
                )



            # =====================
            # MIDI → MusicXML
            # =====================

            st.write(
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


            musicxml = os.path.join(
                work,
                "raw.musicxml"
                "output.musicxml",
                "melody.musicxml",
                "fixed.musicxml",
]
            )



            # =====================
            # Clean
            # =====================

            st.write(
                "🧹 修正 MusicXML"
            )


            run_cmd(
                [
                    sys.executable,
                    "clean_musicxml.py",
                    musicxml,
                    work
                ]
            )


            clean_xml = os.path.join(
                work,
                "clean.musicxml"
            )



            # =====================
            # Final Fix
            # =====================

            st.write(
                "🎼 最終修正"
            )


            run_cmd(
                [
                    sys.executable,
                    "jianpu_fix_musicxml.py",
                    clean_xml,
                    work
                ]
            )


            final_xml = os.path.join(
                work,
                "final.musicxml"
            )



            # =====================
            # jianpu-ly
            # =====================

            st.write(
                "🎵 產生簡譜 LilyPond"
            )


            run_cmd(
                [
                    sys.executable,
                    "-m",
                    "jianpu_ly",
                    final_xml
                ]
            )



            ly_file = "final.ly"


            if not os.path.exists(
                ly_file
            ):

                raise Exception(
                    "jianpu-ly 沒產生 final.ly"
                )



            # =====================
            # LilyPond PDF
            # =====================

            if LILYPOND is None:

                raise Exception(
                    "找不到 LilyPond"
                )


            st.write(
                "📄 LilyPond 產生 PDF"
            )


            run_cmd(
                [
                    LILYPOND,
                    "-fpdf",
                    ly_file
                ]
            )



            pdf = "final.pdf"


            if os.path.exists(pdf):

                st.success(
                    "🎉 完成!"
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
                    "PDF沒有產生"
                )



        except Exception as e:

            st.error(
                "轉換錯誤"
            )

            st.exception(e)