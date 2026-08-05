import streamlit as st
import os
import uuid
import subprocess
import glob
import shutil


st.set_page_config(
    page_title="JianpuTool AI Vocal",
    page_icon="🎵"
)


st.title("🎵 JianpuTool AI Vocal → 簡譜")


def run(cmd):

    st.write("執行:")
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





upload = st.file_uploader(
    "上傳 MP3",
    type=["mp3","wav"]
)


if upload:


    work = "outputs/" + str(uuid.uuid4())

    os.makedirs(work,exist_ok=True)


    input_file = os.path.join(
        work,
        "input.mp3"
    )


    with open(input_file,"wb") as f:
        f.write(upload.read())


    st.success("MP3 上傳完成")



    # ==========================
    # Demucs
    # ==========================

    st.write("🎤 分離人聲...")


    run([
        "demucs",
        "-n",
        "htdemucs",
        input_file
    ])



    # 搜尋 vocal

    vocals = glob.glob(
        "separated/**/vocals.wav",
        recursive=True
    )


    if not vocals:
        raise Exception(
            "找不到 vocals.wav"
        )


    vocal_file = vocals[-1]


    st.success(
        f"找到人聲: {vocal_file}"
    )



    # ==========================
    # BasicPitch
    # ==========================

    st.write(
        "🎼 AI 抓 Vocal MIDI..."
    )


    vocal_mid = os.path.join(
        work,
        "vocal.mid"
    )


    run([
        "python",
        "basicpitch_convert.py",
        vocal_file,
        vocal_mid
    ])




    # ==========================
    # MIDI Clean
    # ==========================


    clean_mid=os.path.join(
        work,
        "vocal_clean.mid"
    )


    run([
        "python",
        "vocal_midi_clean.py",
        vocal_mid,
        clean_mid
    ])




    # ==========================
    # MusicXML
    # ==========================


    musicxml=os.path.join(
        work,
        "final.musicxml"
    )


    run([
        "python",
        "midi_to_musicxml_clean.py",
        clean_mid,
        musicxml
    ])




    # ==========================
    # Jianpu
    # ==========================


    st.write(
        "🎹 產生簡譜..."
    )


    run([
        "python",
        "-m",
        "jianpu_ly",
        musicxml
    ])



    ly_files=glob.glob(
        "/tmp/*.ly"
    )


    if not ly_files:
        raise Exception(
            "找不到 ly"
        )


    ly_file=ly_files[-1]



    # ==========================
    # LilyPond PDF
    # ==========================


    run([
        "lilypond",
        ly_file
    ])



    pdf_files=glob.glob(
        "*.pdf"
    )


    if pdf_files:

        pdf=pdf_files[-1]

        st.success(
            "完成 🎉"
        )


        with open(pdf,"rb") as f:

            st.download_button(
                "下載簡譜 PDF",
                f,
                file_name="jianpu.pdf"
            )