import streamlit as st
import os
import sys
import uuid
import subprocess


st.set_page_config(
    page_title="JianpuTool MVP 1.1",
    page_icon="🎵"
)


st.title("🎵 JianpuTool MVP 1.1")


st.write(
"""
MP3 / WAV / MIDI → MIDI → MusicXML → Jianpu PDF
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



def run_cmd(cmd):

    st.code(
        " ".join(cmd)
    )


    p = subprocess.run(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True
    )


    st.text(
        p.stdout
    )


    if p.returncode != 0:

        raise Exception(
            p.stdout
        )



uploaded = st.file_uploader(
    "上傳音樂",
    type=[
        "mp3",
        "wav",
        "mid",
        "midi"
    ]
)



if uploaded:


    job = str(uuid.uuid4())[:8]


    input_file=os.path.join(
        OUTPUT_DIR,
        uploaded.name
    )


    with open(
        input_file,
        "wb"
    ) as f:

        f.write(
            uploaded.getbuffer()
        )


    ext = uploaded.name.lower().split(".")[-1]


    try:


        # --------------------
        # Audio -> MIDI
        # --------------------

        if ext in [
            "mp3",
            "wav"
        ]:


            st.info(
                "🎤 BasicPitch分析"
            )


            midi=os.path.join(
                OUTPUT_DIR,
                f"{job}.mid"
            )


            run_cmd(
            [
                sys.executable,
                "basicpitch_convert.py",
                input_file,
                midi
            ]
            )


        else:


            midi=input_file




        # --------------------
        # Quantize
        # --------------------

        st.info(
            "🎚 MIDI量化"
        )


        quant=os.path.join(
            OUTPUT_DIR,
            f"{job}_quant.mid"
        )


        run_cmd(
        [
            sys.executable,
            "midi_quantize.py",
            midi,
            quant
        ]
        )




        # --------------------
        # MIDI -> MusicXML
        # --------------------

        st.info(
            "🎼 MIDI轉MusicXML"
        )


        raw=os.path.join(
            OUTPUT_DIR,
            f"{job}_raw.musicxml"
        )


        run_cmd(
        [
            sys.executable,
            "midi_to_musicxml_clean.py",
            quant,
            raw
        ]
        )




        # --------------------
        # Clean
        # --------------------

        st.info(
            "🧹 清理MusicXML"
        )


        clean=os.path.join(
            OUTPUT_DIR,
            f"{job}_clean.musicxml"
        )


        run_cmd(
        [
            sys.executable,
            "clean_musicxml.py",
            raw,
            clean
        ]
        )




        # --------------------
        # Fix
        # --------------------

        st.info(
            "🔧 修正MusicXML"
        )


        fixed=os.path.join(
            OUTPUT_DIR,
            f"{job}_fixed.musicxml"
        )


        run_cmd(
        [
            sys.executable,
            "jianpu_fix_musicxml.py",
            clean,
            fixed
        ]
        )




        # --------------------
        # Rebuild measures
        # --------------------

        st.info(
            "📐 重建4/4小節"
        )


        rebuild=os.path.join(
            OUTPUT_DIR,
            f"{job}_rebuild.musicxml"
        )


        run_cmd(
        [
            sys.executable,
            "rebuild_measures.py",
            fixed,
            rebuild
        ]
        )


        final_xml=rebuild




        # --------------------
        # Check
        # --------------------

        st.info(
            "📏 檢查小節"
        )


        run_cmd(
        [
            sys.executable,
            "check_measure.py",
            final_xml
        ]
        )




        # --------------------
        # Jianpu ly
        # --------------------

        st.info(
            "🔢 產生 Jianpu LilyPond"
        )


        run_cmd(
        [
            sys.executable,
            "-m",
            "jianpu_ly",
            final_xml
        ]
        )



        ly_file=final_xml.replace(
            ".musicxml",
            ".ly"
        )



        # --------------------
        # PDF
        # --------------------

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



        pdf=ly_file.replace(
            ".ly",
            ".pdf"
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
                    "下載簡譜PDF",
                    f,
                    file_name=os.path.basename(pdf)
                )


        else:

            st.error(
                "PDF不存在"
            )



    except Exception as e:

        st.error(
            "轉換錯誤"
        )

        st.exception(e)