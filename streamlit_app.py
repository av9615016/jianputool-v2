import streamlit as st
import os
import uuid
import subprocess
import sys
import shutil


# ============================================================
# Page
# ============================================================

st.set_page_config(
    page_title="JianpuTool Professional MVP 2.3.1",
    page_icon="🎵"
)


st.title(
    "🎵 JianpuTool Professional MVP 2.3.1"
)


st.write(
"""
AI Vocal → MIDI → MusicXML → Jianpu PDF

每次歌曲使用獨立工作目錄
避免不同歌曲輸出相同 PDF
"""
)



# ============================================================
# Tools
# ============================================================


BASE_DIR="outputs"


os.makedirs(
    BASE_DIR,
    exist_ok=True
)



def new_job():

    job_id=str(
        uuid.uuid4()
    )

    folder=os.path.join(
        BASE_DIR,
        job_id
    )

    os.makedirs(
        folder,
        exist_ok=True
    )

    return folder



def run(cmd):

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



# ============================================================
# Upload
# ============================================================


uploaded=st.file_uploader(
    "上傳 MP3 / WAV",
    type=[
        "mp3",
        "wav"
    ]
)



if uploaded:


    job_dir=new_job()


    ext=os.path.splitext(
        uploaded.name
    )[1]


    input_file=os.path.join(
        job_dir,
        "input"+ext
    )


    with open(
        input_file,
        "wb"
    ) as f:

        f.write(
            uploaded.getbuffer()
        )


    st.success(
        "歌曲上傳完成"
    )


    st.write(
        "Job:",
        job_dir
    )



    # ========================================================
    # 1 Vocal
    # ========================================================


    st.subheader(
        "🎤 Vocal Separation"
    )


    vocal_file=os.path.join(
        job_dir,
        "vocal.wav"
    )


    if not os.path.exists(
        vocal_file
    ):


        st.info(
            "開始抽取人聲"
        )


        # 你的 Demucs 程式放這裡
        #
        # 範例:
        #
        # run([
        # sys.executable,
        # "-m",
        # "demucs",
        # input_file
        # ])


    else:

        st.info(
            "使用本歌曲 Vocal 快取"
        )



    # ========================================================
    # 2 BasicPitch
    # ========================================================


    st.subheader(
        "🎼 BasicPitch AI"
    )


    midi_file=os.path.join(
        job_dir,
        "vocal.mid"
    )



    if not os.path.exists(
        midi_file
    ):


        run([

            sys.executable,

            "basicpitch_convert.py",

            input_file,

            midi_file

        ])


    else:

        st.info(
            "使用本歌曲 MIDI 快取"
        )



    # ========================================================
    # 3 Melody Preserve
    # ========================================================


    st.subheader(
        "🎹 Melody Preserve Pro"
    )


    clean_mid=os.path.join(
        job_dir,
        "clean.mid"
    )


    run([

        sys.executable,

        "melody_preserve_pro_v1.py",

        midi_file,

        clean_mid

    ])



    # ========================================================
    # 4 MIDI XML
    # ========================================================


    st.subheader(
        "🎵 MIDI → MusicXML"
    )


    raw_xml=os.path.join(
        job_dir,
        "raw.musicxml"
    )


    run([

        sys.executable,

        "midi_to_musicxml_clean.py",

        clean_mid,

        raw_xml

    ])



    # ========================================================
    # 5 Safe Fix
    # ========================================================


    st.subheader(
        "🛠 Jianpu Safe Fix"
    )


    fixed_xml=os.path.join(
        job_dir,
        "fixed.musicxml"
    )


    run([

        sys.executable,

        "jianpu_safe_fix.py",

        raw_xml,

        fixed_xml

    ])



    # ========================================================
    # 6 jianpu
    # ========================================================


    st.subheader(
        "🎼 MusicXML → Jianpu"
    )


    ly_file=os.path.join(
        job_dir,
        "fixed.ly"
    )


    run([

        sys.executable,

        "-m",

        "jianpu_ly",

        fixed_xml

    ])



    # 找 ly

    for f in os.listdir(job_dir):

        if f.endswith(".ly"):

            ly_file=os.path.join(
                job_dir,
                f
            )



    # ========================================================
    # 7 LilyPond PDF
    # ========================================================


    st.subheader(
        "📄 PDF"
    )


    run([

        "lilypond",

        "-o",

        os.path.join(
            job_dir,
            "jianpu"
        ),

        ly_file

    ])



    pdf_file=os.path.join(
        job_dir,
        "jianpu.pdf"
    )



    if os.path.exists(
        pdf_file
    ):


        st.success(
            "完成"
        )


        st.download_button(

            "⬇️ 下載簡譜 PDF",

            open(
                pdf_file,
                "rb"
            ),

            file_name=
            "jianpu.pdf",

            mime=
            "application/pdf"

        )


    else:

        st.error(
            "找不到 PDF"
        )



    # Debug

    st.write(
        "---"
    )

    st.write(
        "Input:",
        input_file
    )

    st.write(
        "MIDI:",
        midi_file
    )

    st.write(
        "XML:",
        fixed_xml
    )

    st.write(
        "PDF:",
        pdf_file
    )