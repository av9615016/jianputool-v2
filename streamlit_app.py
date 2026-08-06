import streamlit as st
import os
import uuid
import subprocess
import glob
import traceback
import sys



# ==========================
# Page
# ==========================

st.set_page_config(
    page_title="JianpuTool AI Vocal MVP 1.3",
    page_icon="🎵"
)


st.title(
    "🎵 JianpuTool AI Vocal MVP 1.3"
)


st.write(
"""
MP3 / WAV → AI Vocal → MIDI → MusicXML → 簡譜 PDF

Pipeline:

🎤 Demucs Vocal Separation
↓
🎼 BasicPitch
↓
🎹 Vocal MIDI Clean
↓
🎼 MusicXML
↓
🧹 Clean
↓
🎵 Jianpu Fix
↓
⏱ Quantize
↓
🔍 Measure Check
↓
🎹 jianpu-ly
↓
📄 LilyPond PDF
"""
)



# ==========================
# Command
# ==========================

def run(cmd):

    st.write(
        "執行:"
    )

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



# ==========================
# Upload
# ==========================


upload=st.file_uploader(
    "上傳 MP3 / WAV",
    type=[
        "mp3",
        "wav"
    ]
)



if upload:


    job=str(uuid.uuid4())[:8]


    work=os.path.join(
        "outputs",
        job
    )


    os.makedirs(
        work,
        exist_ok=True
    )


    input_file=os.path.join(
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
        f"上傳完成: {upload.name}"
    )


    st.info(
        f"工作目錄: {work}"
    )



    try:


        # ==========================
        # Demucs
        # ==========================


        st.write(
            "🎤 Demucs 分離人聲"
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



        vocals=glob.glob(
            "separated/**/vocals.wav",
            recursive=True
        )


        if not vocals:

            raise Exception(
                "找不到 vocals.wav"
            )


        vocal_file=vocals[-1]


        st.success(
            f"找到人聲: {vocal_file}"
        )
 # ==========================
        # BasicPitch Vocal MIDI
        # ==========================


        st.write(
            "🎼 BasicPitch 抓 Vocal MIDI"
        )


        vocal_mid=os.path.join(
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


        if not os.path.exists(
            vocal_mid
        ):

            raise Exception(
                "Vocal MIDI 產生失敗"
            )



        # ==========================
        # Vocal MIDI Clean
        # ==========================


        st.write(
            "🎹 Vocal MIDI Clean"
        )


        clean_mid=os.path.join(
            work,
            "vocal_clean.mid"
        )


        run(
            [
                sys.executable,
                "vocal_midi_clean.py",
                vocal_mid,
                clean_mid
            ]
        )



        if not os.path.exists(
            clean_mid
        ):

            raise Exception(
                "MIDI Clean 失敗"
            )



        # ==========================
        # MIDI → MusicXML
        # ==========================


        st.write(
            "🎼 MIDI → MusicXML"
        )


        raw_xml=os.path.join(
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



        if not os.path.exists(
            raw_xml
        ):

            raise Exception(
                "MusicXML 產生失敗"
            )



        # ==========================
        # Clean MusicXML
        # ==========================


        st.write(
            "🧹 Clean MusicXML"
        )


        clean_xml=os.path.join(
            work,
            "clean.musicxml"
        )


        run(
            [
                sys.executable,
                "clean_musicxml.py",
                raw_xml,
                clean_xml
            ]
        )



        # ==========================
        # Jianpu Fix
        # ==========================


        st.write(
            "🎵 Jianpu Fix"
        )


        fixed_xml=os.path.join(
            work,
            "fixed.musicxml"
        )


        run(
            [
                sys.executable,
                "jianpu_fix_musicxml.py",
                clean_xml,
                fixed_xml
            ]
        )



        # ==========================
        # Final Quantize
        # ==========================


        st.write(
            "⏱ Final Quantize"
        )


        final_xml=os.path.join(
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



        if not os.path.exists(
            final_xml
        ):

            raise Exception(
                "final.musicxml 不存在"
            )



        # ==========================
        # Check Measure
        # ==========================


        st.write(
            "🔍 檢查 4/4 小節"
        )


        run(
            [
                sys.executable,
                "check_measure.py",
                final_xml
            ]
        )


        st.success(
            "✅ 小節檢查通過"
        )
  # ==========================
        # MusicXML → jianpu.ly
        # ==========================


        st.write(
            "🎵 MusicXML → jianpu.ly"
        )


        run(
            [
                sys.executable,
                "-m",
                "jianpu_ly",
                final_xml
            ]
        )



        # ==========================
        # 找 ly
        # ==========================


        ly_files=[]


        for root,dirs,files in os.walk("."):

            for file in files:

                if file.endswith(".ly"):

                    ly_files.append(
                        os.path.join(
                            root,
                            file
                        )
                    )



        if not ly_files:

            raise Exception(
                "找不到 jianpu.ly"
            )


        ly_file=ly_files[-1]


        st.success(
            f"找到 LilyPond: {ly_file}"
        )



        # ==========================
        # LilyPond
        # ==========================


        st.write(
            "📄 LilyPond 產生 PDF"
        )


        run(
            [
                "lilypond",
                "-o",
                os.path.join(
                    work,
                    "jianpu"
                ),
                ly_file
            ]
        )



        pdf_files=glob.glob(
            "*.pdf"
        )


        pdf_files+=glob.glob(
            os.path.join(
                work,
                "*.pdf"
            )
        )


        if not pdf_files:

            raise Exception(
                "找不到 PDF"
            )


        pdf=pdf_files[-1]



        st.success(
            "🎉 簡譜 PDF 完成"
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



    except Exception as e:


        st.error(
            "❌ 轉換失敗"
        )


        st.exception(
            e
        )


        st.code(
            traceback.format_exc()
        )