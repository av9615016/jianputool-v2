# ============================================================
# JianpuTool Professional MVP 2.2
# Streamlit App
#
# Pipeline:
#
# MP3/WAV
# ↓
# Demucs Vocal Separation
# ↓
# BasicPitch
# ↓
# MIDI Clean
# ↓
# MusicXML
# ↓
# Jianpu Safe Fix
# ↓
# LilyPond PDF
#
# ============================================================


import streamlit as st
import os
import sys
import uuid
import glob
import subprocess
import shutil
import traceback


# ============================================================
# Page
# ============================================================

st.set_page_config(
    page_title="JianpuTool Professional MVP 2.2",
    page_icon="🎵"
)


st.title(
    "🎵 JianpuTool Professional MVP 2.2"
)


st.write(
"""
AI Vocal → MIDI → MusicXML → 數字簡譜 PDF

Professional Pipeline:

🎤 Demucs Vocal Separation
↓
🎼 BasicPitch AI Melody
↓
🎹 Melody Clean Pro
↓
📄 MusicXML
↓
🎵 Jianpu Safe Fix
↓
📘 Jianpu PDF
"""
)



# ============================================================
# Command Runner
# ============================================================


def run(cmd):

    st.write("執行:")
    st.code(
        " ".join(cmd)
    )


    result = subprocess.run(
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


    return result.stdout



# ============================================================
# Upload
# ============================================================


upload = st.file_uploader(
    "上傳 MP3 / WAV",
    type=[
        "mp3",
        "wav"
    ]
)



if upload:


    # ========================================================
    # Work Directory
    # ========================================================


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
        "input.mp3"
    )


    with open(
        input_file,
        "wb"
    ) as f:

        f.write(
            upload.read()
        )


    st.success(
        f"上傳完成: {input_file}"
    )



    # ========================================================
    # 1. Demucs
    # ========================================================


    st.subheader(
        "🎤 1. Vocal Separation"
    )


    run(
        [
            sys.executable,
            "-m",
            "demucs",
            "-n",
            "htdemucs",
            input_file
        ]
    )



    # ========================================================
    # Find vocals.wav
    # ========================================================


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
        f"找到人聲:\n{vocal_file}"
    )



    # ========================================================
    # 2. BasicPitch
    # ========================================================


    st.subheader(
        "🎼 2. BasicPitch AI Melody"
    )


    vocal_mid = os.path.join(
        work,
        "vocal.mid"
    )


    run(
        [
            sys.executable,
            "basicpitch_convert.py",
            vocal_file,
            vocal_mid
        ]
    )


    st.success(
        "BasicPitch MIDI 完成"
    )
  # ========================================================
    # 3. Melody Clean Pro
    # ========================================================


    st.subheader(
        "🎹 3. Melody Clean Pro"
    )


    clean_mid = os.path.join(
        work,
        "clean.mid"
    )


    run(
        [
            sys.executable,
            "melody_clean_pro.py",
            vocal_mid,
            clean_mid
        ]
    )


    st.success(
        "Melody Clean 完成"
    )



    # ========================================================
    # 4. MIDI -> MusicXML
    # ========================================================


    st.subheader(
        "🎼 4. MIDI → MusicXML"
    )


    raw_xml = os.path.join(
        work,
        "raw.musicxml"
    )


    run(
        [
            sys.executable,
            "midi_to_musicxml_clean.py",
            clean_mid,
            raw_xml
        ]
    )


    st.success(
        "MusicXML 建立完成"
    )



    # ========================================================
    # 5. Jianpu Safe Fix
    # ========================================================


    st.subheader(
        "🛠 5. Jianpu Safe Fix"
    )


    fixed_xml = os.path.join(
        work,
        "fixed.musicxml"
    )


    run(
        [
            sys.executable,
            "jianpu_safe_fix.py",
            raw_xml,
            fixed_xml
        ]
    )


    st.success(
        "Safe Fix 完成"
    )



    # ========================================================
    # 6. Final Quantize
    # ========================================================


    st.subheader(
        "⏱ Final Quantize"
    )


    final_xml = os.path.join(
        work,
        "final.musicxml"
    )


    run(
        [
            sys.executable,
            "final_quantize.py",
            fixed_xml,
            final_xml
        ]
    )


    st.success(
        "Final MusicXML 完成"
    )



    # ========================================================
    # 7. Measure Check
    # ========================================================


    st.subheader(
        "📏 Measure Check"
    )


    run(
        [
            sys.executable,
            "check_measure.py",
            final_xml
        ]
    )


    st.success(
        "✅ 小節檢查完成"
    )



    # ========================================================
    # Save path
    # ========================================================


    st.session_state["final_xml"] = final_xml
    st.session_state["work"] = work
 # ========================================================
    # 8. MusicXML -> jianpu.ly
    # ========================================================


    st.subheader(
        "🎵 8. MusicXML → Jianpu"
    )


    try:

        run(
            [
                sys.executable,
                "-m",
                "jianpu_ly",
                final_xml
            ]
        )


    except Exception as e:

        st.error(
            "jianpu_ly 產生失敗"
        )

        st.code(
            traceback.format_exc()
        )

        raise e



    # ========================================================
    # Find ly file
    # ========================================================


    ly_files = []


    search_paths = [
        work,
        ".",
        "/tmp"
    ]


    for p in search_paths:

        ly_files.extend(
            glob.glob(
                os.path.join(
                    p,
                    "*.ly"
                )
            )
        )



    if not ly_files:

        raise Exception(
            "找不到 jianpu.ly"
        )



    ly_file = ly_files[-1]


    st.success(
        f"找到 LilyPond 檔案:\n{ly_file}"
    )



    # ========================================================
    # 9. LilyPond PDF
    # ========================================================


    st.subheader(
        "📘 9. LilyPond PDF"
    )


    run(
        [
            "lilypond",
            ly_file
        ]
    )



    # ========================================================
    # Find PDF
    # ========================================================


    pdf_files = []


    pdf_files.extend(
        glob.glob(
            os.path.join(
                work,
                "*.pdf"
            )
        )
    )


    pdf_files.extend(
        glob.glob(
            "*.pdf"
        )
    )



    if not pdf_files:

        raise Exception(
            "找不到 PDF"
        )


    pdf = pdf_files[-1]



    st.success(
        "🎉 Jianpu PDF 完成"
    )



    # ========================================================
    # Download
    # ========================================================


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



    st.info(
        f"""
完成！

工作目錄:
{work}

PDF:
{pdf}
"""
    )