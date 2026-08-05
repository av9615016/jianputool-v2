import streamlit as st
import os
import uuid
import subprocess
import shutil


st.set_page_config(
    page_title="JianpuTool AI",
    page_icon="🎵"
)


st.title(
    "🎵 JianpuTool AI Vocal → 簡譜"
)


upload = st.file_uploader(
    "上傳 MP3",
    type=["mp3","wav"]
)



def run(cmd):

    st.write(
        "執行:",
        " ".join(cmd)
    )

    result=subprocess.run(
        cmd,
        capture_output=True,
        text=True
    )

    if result.stdout:
        st.text(result.stdout)

    if result.stderr:
        st.text(result.stderr)



if upload:


    job=str(uuid.uuid4())

    work=f"outputs/{job}"

    os.makedirs(
        work,
        exist_ok=True
    )


    mp3=f"{work}/input.mp3"


    with open(mp3,"wb") as f:

        f.write(
            upload.read()
        )


    st.success(
        "MP3 上傳完成"
    )


    # ===================
    # Demucs
    # ===================

    st.write(
        "🎤 分離人聲..."
    )


    run([
        "demucs",
        "-n",
        "htdemucs",
        mp3
    ])



    vocals=(
        f"separated/htdemucs/"
        f"{work}/vocals.wav"
    )


    # ===================
    # BasicPitch
    # ===================

    st.write(
        "🎼 AI 抓 Vocal MIDI..."
    )


    vocal_mid=f"{work}/vocal.mid"


    run([
        "python",
        "basicpitch_convert.py",
        vocals,
        vocal_mid
    ])



    # ===================
    # MIDI Clean
    # ===================


    clean_mid=f"{work}/vocal_clean.mid"


    run([
        "python",
        "vocal_midi_clean.py",
        vocal_mid,
        clean_mid
    ])



    # ===================
    # MusicXML
    # ===================


    xml=f"{work}/final.musicxml"


    run([
        "python",
        "midi_to_musicxml_clean.py",
        clean_mid,
        xml
    ])



    # ===================
    # Jianpu
    # ===================


    st.write(
        "🎹 產生簡譜..."
    )


    run([
        "python",
        "-m",
        "jianpu_ly",
        xml
    ])



    ly="/tmp/final.ly"


    pdf=f"{work}/jianpu.pdf"



    run([
        r"C:\lilypond-2.26.0\bin\lilypond.exe",
        ly
    ])



    st.success(
        "完成！"
    )


    if os.path.exists(pdf):

        with open(pdf,"rb") as f:

            st.download_button(
                "下載簡譜 PDF",
                f,
                "jianpu.pdf"
            )