import streamlit as st
import os
import uuid
import subprocess
import sys


# =====================================================
# Page
# =====================================================

st.set_page_config(
    page_title="JianpuTool Professional MVP 2.3.2",
    page_icon="🎵"
)


st.title(
    "🎵 JianpuTool Professional MVP 2.3.2"
)


st.write(
"""
AI Vocal → MIDI → MusicXML → Jianpu PDF

Professional Pipeline:

MP3/WAV
↓
BasicPitch AI
↓
Melody Preserve Pro
↓
MusicXML
↓
Safe Fix
↓
Measure Fix
↓
Jianpu PDF
"""
)



BASE_DIR="outputs"

os.makedirs(
    BASE_DIR,
    exist_ok=True
)



def new_job():

    job=str(uuid.uuid4())

    folder=os.path.join(
        BASE_DIR,
        job
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



# =====================================================
# Upload
# =====================================================


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



    # =================================================
    # BasicPitch
    # =================================================


    st.subheader(
        "🎼 BasicPitch AI"
    )


    midi_file=os.path.join(
        job_dir,
        "vocal.mid"
    )


    run([

        sys.executable,

        "basicpitch_convert.py",

        input_file,

        midi_file

    ])




    # =================================================
    # Melody Preserve
    # =================================================


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




    # =================================================
    # MIDI -> MusicXML
    # =================================================


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




    # =================================================
    # Safe Fix
    # =================================================


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




    # =================================================
    # Measure Fix NEW
    # =================================================


    st.subheader(
        "🎼 Measure Quantize Fix"
    )


    final_xml=os.path.join(
        job_dir,
        "final.musicxml"
    )


    run([

        sys.executable,

        "jianpu_measure_fix.py",

        fixed_xml,

        final_xml

    ])




    # =================================================
    # Jianpu
    # =================================================


    st.subheader(
        "🎼 MusicXML → Jianpu"
    )


    run([

        sys.executable,

        "-m",

        "jianpu_ly",

        final_xml

    ])




    # 找 ly

    ly_file=None


    for f in os.listdir(job_dir):

        if f.endswith(".ly"):

            ly_file=os.path.join(
                job_dir,
                f
            )



    if ly_file is None:

        raise Exception(
            "找不到 ly"
        )




    # =================================================
    # LilyPond
    # =================================================


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



    pdf=os.path.join(
        job_dir,
        "jianpu.pdf"
    )



    if os.path.exists(pdf):


        st.success(
            "🎉 完成"
        )


        st.download_button(

            "⬇️下載簡譜 PDF",

            open(
                pdf,
                "rb"
            ),

            file_name="jianpu.pdf",

            mime="application/pdf"

        )

    else:

        st.error(
            "PDF不存在"
        )



    st.write(
        "MIDI:",
        midi_file
    )

    st.write(
        "MusicXML:",
        final_xml
    )

    st.write(
        "PDF:",
        pdf
    )