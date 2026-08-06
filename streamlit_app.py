import streamlit as st
import os
import uuid
import subprocess
import glob
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


st.write("Python:")
st.code(sys.executable)

st.write("Version:")
st.code(sys.version)


# ==========================
# Run Command
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
        raise Exception(
            result.stdout
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


    work = os.path.join(
        "outputs",
        str(uuid.uuid4())
    )

    os.makedirs(
        work,
        exist_ok=True
    )


    input_file = os.path.join(
        work,
        "input.wav"
    )


    with open(
        input_file,
        "wb"
    ) as f:

        f.write(
            upload.read()
        )


    st.success(
        "音訊上傳完成"
    )



    # ==========================
    # Demucs
    # ==========================


    st.write(
        "🎤 Demucs 分離人聲..."
    )


    run([
        "demucs",
        "-n",
        "htdemucs",
        input_file
    ])



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
        sys.executable,
        "basicpitch_convert.py",
        vocal_file,
        vocal_mid
    ])




    # ==========================
    # MIDI Clean
    # ==========================


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
    # MIDI → MusicXML
    # ==========================


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
    # Jianpu
    # ==========================


    st.write(
        "🎹 產生簡譜 LilyPond..."
    )


    run([
        sys.executable,
        "-m",
        "jianpu_ly",
        musicxml
    ])




    # ==========================
    # Find LY
    # ==========================


    ly_files = glob.glob(
        "**/*.ly",
        recursive=True
    )


    if not ly_files:

        raise Exception(
            "找不到 LilyPond .ly 檔案"
        )


    ly_file = ly_files[-1]


    st.success(
        f"找到 LY: {ly_file}"
    )



    # ==========================
    # LilyPond PDF
    # ==========================


    st.write(
        "📄 LilyPond 產生 PDF..."
    )


    run([
        "lilypond",
        ly_file
    ])



    pdf_files = glob.glob(
        "**/*.pdf",
        recursive=True
    )


    if pdf_files:


        pdf = pdf_files[-1]


        st.success(
            "完成 🎉"
        )


        with open(
            pdf,
            "rb"
        ) as f:


            st.download_button(
                label="下載簡譜 PDF",
                data=f,
                file_name="jianpu.pdf",
                mime="application/pdf"
            )


    else:

        raise Exception(
            "沒有產生 PDF"
        )