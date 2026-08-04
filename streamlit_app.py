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
MP3 / WAV / MIDI

↓

主旋律分析

↓

MusicXML

↓

數字簡譜 PDF
"""
)


BASE_DIR=os.path.dirname(
    os.path.abspath(__file__)
)


OUTPUT_DIR=os.path.join(
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


    result=subprocess.run(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True
    )


    st.text(
        result.stdout
    )


    if result.returncode !=0:

        raise Exception(
            result.stdout
        )





upload=st.file_uploader(
    "上傳音樂",
    type=[
        "mp3",
        "wav",
        "mid",
        "midi"
    ]
)



if upload:


    job=str(uuid.uuid4())[:8]


    input_file=os.path.join(
        OUTPUT_DIR,
        upload.name
    )


    with open(input_file,"wb") as f:

        f.write(
            upload.getbuffer()
        )


    st.success(
        "上傳完成"
    )


    ext=upload.name.lower().split(".")[-1]


    try:


        # =====================
        # 1. Audio → MIDI
        # =====================

        if ext in [
            "mp3",
            "wav"
        ]:


            st.info(
                "🎤 BasicPitch 分析旋律"
            )


            midi_file=os.path.join(
                OUTPUT_DIR,
                f"{job}.mid"
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


            st.info(
                "🎹 使用 MIDI"
            )


            midi_file=input_file




        # =====================
        # 2. MIDI → MusicXML
        # =====================

        st.info(
            "🎼 MIDI轉MusicXML"
        )


        raw_xml=os.path.join(
            OUTPUT_DIR,
            f"{job}_raw.musicxml"
        )


        run_cmd(
            [
                sys.executable,
                "midi_to_musicxml_clean.py",
                midi_file,
                raw_xml
            ]
        )




        # =====================
        # 3. Clean MusicXML
        # =====================


        st.info(
            "🧹 清理MusicXML"
        )


        clean_xml=os.path.join(
            OUTPUT_DIR,
            f"{job}_clean.musicxml"
        )


        run_cmd(
            [
                sys.executable,
                "clean_musicxml.py",
                raw_xml,
                clean_xml
            ]
        )





        # =====================
        # 4. Fix Measure
        # =====================


        st.info(
            "🔧 修正節拍"
        )


        final_xml=os.path.join(
            OUTPUT_DIR,
            f"{job}_final.musicxml"
        )


        run_cmd(
            [
                sys.executable,
                "jianpu_fix_musicxml.py",
                clean_xml,
                final_xml
            ]
        )




        # =====================
        # 5. Check Measure
        # =====================


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





        # =====================
        # 6. Jianpu LY
        # =====================


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



        # =====================
        # 7. LilyPond PDF
        # =====================


        st.info(
            "📄 LilyPond產生PDF"
        )


        run_cmd(
            [
                "lilypond",
                "-o",
                OUTPUT_DIR,
                ly_file
            ]
        )



        pdf_file=ly_file.replace(
            ".ly",
            ".pdf"
        )



        if os.path.exists(pdf_file):


            st.success(
                "🎉 完成"
            )


            with open(pdf_file,"rb") as f:


                st.download_button(
                    "下載簡譜PDF",
                    f,
                    file_name=
                    os.path.basename(pdf_file)
                )


        else:


            st.error(
                "PDF產生失敗"
            )



    except Exception as e:


        st.error(
            "轉換錯誤"
        )


        st.exception(e)