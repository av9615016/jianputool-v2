import streamlit as st
import os
import uuid
import subprocess
import shutil
import glob


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


    work = f"outputs/{uuid.uuid4()}"

    os.makedirs(
        work,
        exist_ok=True
    )


    input_audio = f"{work}/input.mp3"


    with open(input_audio,"wb") as f:
        f.write(upload.read())


    st.success("MP3 上傳完成")


    #
    # 1 Demucs 分離人聲
    #

    st.write("🎤 分離人聲...")


    run([
        "demucs",
        "-n",
        "htdemucs",
        input_audio
    ])



    #
    # 搜尋 vocals.wav
    #

    vocals_list = glob.glob(
        "separated/**/vocals.wav",
        recursive=True
    )


    if not vocals_list:

        raise Exception(
            "找不到 vocals.wav"
        )


    vocals = vocals_list[-1]


    st.success(
        f"找到人聲: {vocals}"
    )



    #
    # 2 BasicPitch
    #

    st.write(
        "🎼 AI 抓 Vocal MIDI..."
    )


    vocal_mid = f"{work}/vocal.mid"


    run([
        "python",
        "basicpitch_convert.py",
        vocals,
        vocal_mid
    ])



    #
    # 3 MIDI Clean
    #

    clean_mid=f"{work}/vocal_clean.mid"


    run([
        "python",
        "vocal_midi_clean.py",
        vocal_mid,
        clean_mid
    ])




    #
    # 4 MIDI → MusicXML V34
    #

    musicxml=f"{work}/final.musicxml"


    run([
        "python",
        "midi_to_musicxml_clean.py",
        clean_mid,
        musicxml
    ])




    #
    # 5 Jianpu
    #

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
            "找不到 ly 檔"
        )


    ly=ly_files[-1]


    pdf=f"{work}/jianpu.pdf"



    #
    # LilyPond Cloud版
    #

    run([
        "lilypond",
        "-o",
        pdf.replace(".pdf",""),
        ly
    ])



    if os.path.exists(pdf):

        st.success(
            "完成 🎉"
        )


        with open(pdf,"rb") as f:

            st.download_button(
                "下載簡譜 PDF",
                f,
                "jianpu.pdf",
                "application/pdf"
            )