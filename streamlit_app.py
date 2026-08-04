import streamlit as st
import os
import uuid
import subprocess
import shutil
import sys


st.set_page_config(
    page_title="JianpuTool MVP 1.1",
    page_icon="🎵"
)


st.title("🎵 JianpuTool MVP 1.1")

st.write("""
MP3 / WAV / MIDI → 主旋律 → MusicXML → 數字簡譜 PDF

支援：
- MP3
- WAV
- MIDI
""")


BASE_DIR = os.path.dirname(os.path.abspath(__file__))


OUTPUT_DIR = os.path.join(BASE_DIR,"outputs")

os.makedirs(
    OUTPUT_DIR,
    exist_ok=True
)



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
        raise Exception(
            result.stdout
        )



uploaded = st.file_uploader(
    "上傳音樂檔",
    type=[
        "mp3",
        "wav",
        "mid",
        "midi"
    ]
)



if uploaded:


    job_id = str(uuid.uuid4())[:8]


    input_file = os.path.join(
        OUTPUT_DIR,
        uploaded.name
    )


    with open(input_file,"wb") as f:
        f.write(
            uploaded.getbuffer()
        )


    st.success(
        "上傳完成"
    )


    ext = uploaded.name.lower().split(".")[-1]


    try:


        #
        # STEP 1
        #
        if ext in ["mp3","wav"]:


            st.info(
                "🎤 BasicPitch 分析旋律..."
            )


            midi_file = os.path.join(
                OUTPUT_DIR,
                f"{job_id}.mid"
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



        if not os.path.exists(midi_file):

            raise Exception(
                "MIDI產生失敗"
            )



        #
        # STEP 2
        #
        st.info(
            "🎼 MIDI → MusicXML"
        )


        raw_xml=os.path.join(
            OUTPUT_DIR,
            f"{job_id}_raw.musicxml"
        )


        run_cmd(
            [
                sys.executable,
                "midi_to_musicxml_clean.py",
                midi_file,
                raw_xml
            ]
        )



        #
        # STEP 3
        #
        st.info(
            "🧹 清理 MusicXML"
        )


        clean_xml=os.path.join(
            OUTPUT_DIR,
            f"{job_id}_clean.musicxml"
        )


        run_cmd(
            [
                sys.executable,
                "clean_musicxml.py",
                raw_xml,
                clean_xml
            ]
        )



        #
        # STEP 4
        #
        st.info(
            "🎵 修正簡譜格式"
        )


        final_xml=os.path.join(
            OUTPUT_DIR,
            f"{job_id}_final.musicxml"
        )


        run_cmd(
            [
                sys.executable,
                "jianpu_fix_musicxml.py",
                clean_xml,
                final_xml
            ]
        )



        #
        # STEP 5
        #
        st.info(
            "🔢 產生 Jianpu LilyPond"
        )


        ly_file=os.path.join(
            OUTPUT_DIR,
            f"{job_id}.ly"
        )


        run_cmd(
            [
                sys.executable,
                "-m",
                "jianpu_ly",
                final_xml
            ]
        )


        generated_ly = final_xml.replace(
            ".musicxml",
            ".ly"
        )


        if os.path.exists(generated_ly):

            shutil.move(
                generated_ly,
                ly_file
            )



        #
        # STEP 6
        #
        st.info(
            "📄 LilyPond 產生 PDF"
        )


        run_cmd(
            [
                "lilypond",
                "-o",
                OUTPUT_DIR,
                ly_file
            ]
        )



        pdf_file = ly_file.replace(
            ".ly",
            ".pdf"
        )



        if os.path.exists(pdf_file):

            st.success(
                "🎉 完成！簡譜PDF產生成功"
            )


            with open(pdf_file,"rb") as f:

                st.download_button(
                    "下載簡譜 PDF",
                    f,
                    file_name=
                    os.path.basename(pdf_file)
                )


        else:

            st.error(
                "PDF沒有產生"
            )



    except Exception as e:


        st.error(
            "錯誤:"
        )

        st.exception(e)