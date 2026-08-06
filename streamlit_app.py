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
    page_title="JianpuTool MVP 1.2.6",
    page_icon="🎵"
)


st.title(
    "🎵 JianpuTool MVP 1.2.6"
)


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
Final Quantize
↓
Check Measure
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
# Run Command
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


        run_command(
            [
                sys.executable,
                "midi_to_musicxml_clean.py",
                midi_file,
                raw_xml
            ]
        )


        if not os.path.exists(
            raw_xml
        ):

            raise Exception(
                "raw MusicXML 產生失敗"
            )


        st.success(
            "raw MusicXML 完成"
        )



        # ==========================
        # Clean MusicXML
        # ==========================

        st.info(
            "🧹 Clean MusicXML"
        )


        clean_xml = os.path.join(
            workdir,
            "clean.musicxml"
        )


        run_command(
            [
                sys.executable,
                "clean_musicxml.py",
                raw_xml,
                clean_xml
            ]
        )


        if not os.path.exists(
            clean_xml
        ):

            raise Exception(
                "clean MusicXML 失敗"
            )



        # ==========================
        # Jianpu Fix
        # ==========================

        st.info(
            "🎵 Jianpu Fix MusicXML"
        )


        fixed_xml = os.path.join(
            workdir,
            "fixed.musicxml"
        )


        run_command(
            [
                sys.executable,
                "jianpu_fix_musicxml.py",
                clean_xml,
                fixed_xml
            ]
        )


        if not os.path.exists(
            fixed_xml
        ):

            raise Exception(
                "fixed MusicXML 失敗"
            )



        # ==========================
        # Final Quantize
        # ==========================

        st.info(
            "⏱ Final Quantize"
        )


        final_xml = os.path.join(
            workdir,
            "final.musicxml"
        )


        run_command(
            [
                sys.executable,
                "final_quantize.py",
                fixed_xml,
                final_xml
            ]
        )


        if not os.path.exists(
            final_xml
        ):

            raise Exception(
                "final MusicXML 失敗"
            )



        # ==========================
        # Check Measure
        # ==========================

        st.info(
            "🔍 檢查小節拍數"
        )


        run_command(
            [
                sys.executable,
                "check_measure.py",
                final_xml
            ]
        )


        st.success(
            "✅ 小節檢查完成"
        )
 # ==========================
        # MusicXML → jianpu.ly
        # ==========================

        st.info(
            "🎵 MusicXML → jianpu.ly"
        )


        run_command(
            [
                sys.executable,
                "-m",
                "jianpu_ly",
                final_xml
            ]
        )



        # 找 ly

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
                "找不到 jianpu.ly"
            )


        st.success(
            "jianpu.ly 完成"
        )



        # ==========================
        # LilyPond PDF
        # ==========================

        st.info(
            "📄 LilyPond PDF"
        )


        pdf_output = os.path.join(
            workdir,
            "jianpu"
        )


        run_command(
            [
                "lilypond",
                "-o",
                pdf_output,
                ly_file
            ]
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



        # ==========================
        # Download
        # ==========================

        with open(
            pdf_file,
            "rb"
        ) as f:


            st.download_button(
                label="⬇️ 下載簡譜 PDF",
                data=f,
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