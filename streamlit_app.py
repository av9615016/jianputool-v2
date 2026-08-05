import streamlit as st
import os
import uuid
import subprocess
import shutil
import sys


# ==========================
# Page
# ==========================

st.set_page_config(
    page_title="JianpuTool AI Vocal",
    page_icon="🎵"
)


st.title("🎵 JianpuTool AI Vocal → 簡譜")


# ==========================
# Command Runner
# ==========================

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

    return result.stdout



# ==========================
# LilyPond
# ==========================

def get_lilypond():

    # Linux / Streamlit Cloud

    lp = shutil.which(
        "lilypond"
    )

    if lp:
        return lp


    # Windows local

    win = r"C:\lilypond-2.26.0\bin\lilypond.exe"

    if os.path.exists(win):
        return win


    raise Exception(
        "找不到 LilyPond"
    )



# ==========================
# Upload
# ==========================

upload = st.file_uploader(
    "上傳 MP3 / WAV",
    type=[
        "mp3",
        "wav"
    ]
)


if upload:


    job = str(
        uuid.uuid4()
    )


    work = os.path.join(
        "outputs",
        job
    )


    os.makedirs(
        work,
        exist_ok=True
    )


    input_audio = os.path.join(
        work,
        "input.mp3"
    )


    with open(
        input_audio,
        "wb"
    ) as f:

        f.write(
            upload.read()
        )


    st.success(
        "MP3 上傳完成"
    )



    # ==========================
    # 1 Demucs
    # ==========================

    st.write(
        "🎤 分離人聲..."
    )


    run([
        "demucs",
        "-n",
        "htdemucs",
        input_audio
    ])



    vocal = os.path.join(
        "separated",
        "htdemucs",
        input_audio.replace(
            "outputs/",
            ""
        ).replace(
            "/input.mp3",
            ""
        ),
        "vocals.wav"
    )


    # Linux path fix

    if not os.path.exists(vocal):

        vocal = os.path.join(
            "separated",
            "htdemucs",
            work,
            "vocals.wav"
        )


    if not os.path.exists(vocal):

        raise Exception(
            "找不到 vocals.wav"
        )



    # ==========================
    # 2 BasicPitch
    # ==========================

    st.write(
        "🎼 AI 抓 Vocal MIDI..."
    )


    vocal_mid = os.path.join(
        work,
        "vocal.mid"
    )


    run([
        sys.executable,
        "basicpitch_convert.py",
        vocal,
        vocal_mid
    ])



    # ==========================
    # 3 MIDI Clean
    # ==========================

    st.write(
        "🎹 Vocal MIDI 清理..."
    )


    clean_mid = os.path.join(
        work,
        "vocal_clean.mid"
    )


    run([
        sys.executable,
        "vocal_midi_clean.py",
        vocal_mid,
        clean_mid
    ])



    # ==========================
    # 4 MusicXML
    # ==========================

    st.write(
        "🎼 建立 MusicXML..."
    )


    musicxml = os.path.join(
        work,
        "final.musicxml"
    )


    run([
        sys.executable,
        "midi_to_musicxml_clean.py",
        clean_mid,
        musicxml
    ])



    # ==========================
    # 5 jianpu-ly
    # ==========================

    st.write(
        "🎵 轉簡譜格式..."
    )


    run([
        sys.executable,
        "-m",
        "jianpu_ly",
        musicxml
    ])



    ly_file = os.path.join(
        "/tmp",
        "final.ly"
    )


    if not os.path.exists(ly_file):

        # jianpu_ly 會用原檔名

        temp = os.path.join(
            "/tmp",
            "final.musicxml.ly"
        )

        if os.path.exists(temp):
            shutil.copy(
                temp,
                ly_file
            )


    if not os.path.exists(ly_file):

        raise Exception(
            "找不到 final.ly"
        )



    # ==========================
    # 6 LilyPond PDF
    # ==========================

    st.write(
        "📄 LilyPond 產生 PDF..."
    )


    lilypond = get_lilypond()


    run([
        lilypond,
        ly_file
    ])



    pdf = "/tmp/final.pdf"



    if os.path.exists(pdf):

        st.success(
            "🎉 簡譜完成"
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
            "PDF產生失敗"
        )