import streamlit as st
import os
import uuid
import subprocess
import glob
import sys
import shutil


# =====================================
# Page
# =====================================

st.set_page_config(
    page_title="JianpuTool Professional MVP 2.0",
    page_icon="🎵"
)


st.title(
    "🎵 JianpuTool Professional MVP 2.0"
)


st.write(
"""
AI Vocal → Melody → Jianpu PDF

Professional Pipeline

MP3/WAV
 ↓
Demucs FT Vocal Separation
 ↓
Vocal Enhancement
 ↓
BasicPitch AI
 ↓
Melody AI V32
 ↓
MusicXML
 ↓
Quantize
 ↓
Jianpu Safe Fix
 ↓
Jianpu PDF
"""
)



# =====================================
# Runner
# =====================================

def run(cmd):

    st.write("執行:")
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


    if result.returncode != 0:

        raise Exception(
            result.stdout
        )



# =====================================
# Upload
# =====================================

upload=st.file_uploader(
    "上傳 MP3 / WAV",
    type=[
        "mp3",
        "wav"
    ]
)



if upload:


    work=os.path.join(
        "outputs",
        str(uuid.uuid4())
    )


    os.makedirs(
        work,
        exist_ok=True
    )


    input_audio=os.path.join(
        work,
        upload.name
    )


    with open(
        input_audio,
        "wb"
    ) as f:

        f.write(
            upload.read()
        )


    st.success(
        "上傳完成"
    )



    # =====================================
    # Demucs FT
    # =====================================

    st.subheader(
        "🎤 Demucs Professional Vocal"
    )


    run(
        [
            sys.executable,
            "-m",
            "demucs",
            "-n",
            "htdemucs_ft",
            "--two-stems",
            "vocals",
            input_audio
        ]
    )


    vocal_list=glob.glob(
        "separated/**/vocals.wav",
        recursive=True
    )


    if not vocal_list:

        raise Exception(
            "找不到 vocals.wav"
        )


    vocal=vocal_list[-1]


    st.success(
        vocal
    )



    # =====================================
    # Vocal Enhance
    # =====================================

    st.subheader(
        "🔊 Vocal Enhancement"
    )


    clean_vocal=os.path.join(
        work,
        "clean_vocal.wav"
    )


    run(
        [
            "ffmpeg",
            "-y",
            "-i",
            vocal,
            "-af",
            "highpass=f=80,loudnorm",
            clean_vocal
        ]
    )


    st.success(
        "Vocal 清理完成"
    )
 # =====================================
    # BasicPitch AI
    # =====================================

    st.subheader(
        "🎼 BasicPitch AI MIDI"
    )


    vocal_mid=os.path.join(
        work,
        "vocal.mid"
    )


    run(
        [
            sys.executable,
            "basicpitch_convert.py",
            clean_vocal,
            vocal_mid
        ]
    )


    st.success(
        "BasicPitch MIDI 完成"
    )



    # =====================================
    # Melody AI V32
    # =====================================

    st.subheader(
        "🎹 Melody AI V32 Tracking"
    )


    melody_mid=os.path.join(
        work,
        "melody.mid"
    )


    run(
        [
            sys.executable,
            "midi_note_filter_v8.py",
            vocal_mid,
            melody_mid
        ]
    )


    st.success(
        "旋律追蹤完成"
    )



    # =====================================
    # MIDI → MusicXML
    # =====================================

    st.subheader(
        "🎼 MIDI → MusicXML"
    )


    musicxml=os.path.join(
        work,
        "raw.musicxml"
    )


    run(
        [
            sys.executable,
            "midi_to_musicxml_clean.py",
            melody_mid,
            musicxml
        ]
    )


    st.success(
        "MusicXML 建立完成"
    )



    # =====================================
    # Quantize
    # =====================================

    st.subheader(
        "⏱ Final Quantize"
    )


    quant_xml=os.path.join(
        work,
        "fixed.musicxml"
    )


    run(
        [
            sys.executable,
            "final_quantize.py",
            musicxml,
            quant_xml
        ]
    )


    st.success(
        "Quantize 完成"
    )



    # =====================================
    # Measure Check
    # =====================================

    st.subheader(
        "📏 Measure Check"
    )


    run(
        [
            sys.executable,
            "check_measure.py",
            quant_xml
        ]
    )


    st.success(
        "小節檢查完成"
    )



    # =====================================
    # Jianpu Safe Fix
    # =====================================

    st.subheader(
        "🛠 Jianpu Safe Fix"
    )


    safe_xml=os.path.join(
        work,
        "jianpu_safe.musicxml"
    )


    run(
        [
            sys.executable,
            "jianpu_safe_fix.py",
            quant_xml,
            safe_xml
        ]
    )


    st.success(
        "jianpu 防呆修正完成"
    )
    # =====================================
    # MusicXML → jianpu.ly
    # =====================================

    st.subheader(
        "🎵 MusicXML → Jianpu"
    )


    run(
        [
            sys.executable,
            "-m",
            "jianpu_ly",
            safe_xml
        ]
    )



    # =====================================
    # 找 ly
    # =====================================

    ly_files=[]


    for root,dirs,files in os.walk("."):

        for file in files:

            if file.endswith(".ly"):

                path=os.path.join(
                    root,
                    file
                )

                ly_files.append(
                    path
                )


    if not ly_files:

        raise Exception(
            "找不到 LilyPond .ly"
        )


    ly_file=ly_files[-1]


    st.success(
        f"找到:{ly_file}"
    )



    # =====================================
    # LilyPond PDF
    # =====================================

    st.subheader(
        "📄 LilyPond PDF"
    )


    run(
        [
            "lilypond",
            ly_file
        ]
    )



    # =====================================
    # 找 PDF
    # =====================================

    pdf_files=[]


    for root,dirs,files in os.walk("."):

        for file in files:

            if file.endswith(".pdf"):

                pdf_files.append(
                    os.path.join(
                        root,
                        file
                    )
                )


    if pdf_files:


        pdf=pdf_files[-1]


        st.success(
            "🎉 Jianpu PDF 完成"
        )


        with open(
            pdf,
            "rb"
        ) as f:


            st.download_button(
                label="⬇️ 下載簡譜 PDF",
                data=f,
                file_name="jianpu.pdf",
                mime="application/pdf"
            )


    else:

        raise Exception(
            "PDF 產生失敗"
        )