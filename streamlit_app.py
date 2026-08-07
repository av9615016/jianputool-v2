import zipfile
import streamlit as st
import os
import uuid
import subprocess
import sys

from vocal_separator import separate_vocal


# ==========================
# Page
# ==========================

st.set_page_config(
    page_title="JianpuTool AI 音樂助手",
    page_icon="🎵"
)


st.title(
    "🎵 JianpuTool AI 音樂助手"
)


st.write(
"""
功能：

🎤 人聲分離
🎵 AI抓旋律
📄 自動簡譜
🎹 MIDI輸出
🎼 PDF樂譜
"""
)



# ==========================
# Upload
# ==========================

upload = st.file_uploader(
    "上傳 MP3/WAV",
    type=[
        "mp3",
        "wav"
    ]
)



if upload:


    job = str(uuid.uuid4())


    os.makedirs(
        job,
        exist_ok=True
    )


    input_file = os.path.join(
        job,
        upload.name
    )


    with open(
        input_file,
        "wb"
    ) as f:

        f.write(
            upload.read()
        )


    st.success(
        "歌曲上傳完成"
    )



    if st.button(
        "開始製作簡譜"
    ):


        progress = st.progress(0)



        # ======================
        # Demucs
        # ======================

        st.write(
            "🎤 人聲分離"
        )


        try:


            vocal = separate_vocal(
                input_file,
                job
            )


            st.write(
                "取得人聲:",
                vocal
            )


        except Exception as e:


            st.error(
                f"Demucs失敗:{e}"
            )

            st.stop()



        progress.progress(25)



        # ======================
        # BasicPitch
        # ======================

        st.write(
            "🎵 AI抓旋律"
        )


        midi_file = os.path.join(
            job,
            "melody.mid"
        )


        result = subprocess.run(
            [
                sys.executable,
                "basicpitch_convert.py",
                vocal,
                midi_file
            ],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True
        )


        st.text(
            result.stdout
        )


        if result.returncode != 0:

            st.error(
                "BasicPitch失敗"
            )

            st.stop()



        progress.progress(50)



        # ======================
        # MIDI -> MusicXML
        # ======================

        st.write(
            "📄 自動簡譜"
        )


        musicxml_file = os.path.join(
            job,
            "score.musicxml"
        )


        result = subprocess.run(
            [
                sys.executable,
                "midi_to_musicxml_clean.py",
                midi_file,
                musicxml_file
            ],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True
        )


        st.text(
            result.stdout
        )


        if result.returncode != 0:

            st.error(
                "MusicXML產生失敗"
            )

            st.stop()



        progress.progress(70)
 # ======================
        # PDF
        # ======================

        st.write(
            "🎼 PDF樂譜"
        )


        # 修正：
        # pdf不能當資料夾
        # 建立專用輸出目錄

        pdf_dir = os.path.join(
            job,
            "pdf"
        )


        os.makedirs(
            pdf_dir,
            exist_ok=True
        )


        pdf_file = os.path.join(
            pdf_dir,
            "jianpu.pdf"
        )



        if os.path.exists(
            "jianpu_pdf.py"
        ):


            result = subprocess.run(
                [
                    sys.executable,
                    "jianpu_pdf.py",
                    musicxml_file,
                    pdf_file
                ],
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True
            )


            st.text(
                result.stdout
            )


            if result.returncode != 0:

                st.error(
                    "PDF產生失敗"
                )

                st.stop()



        else:


            st.warning(
                "找不到 jianpu_pdf.py"
            )



        progress.progress(100)



        st.success(
            "🎉 製作完成"
        )



        # ======================
        # Download MIDI
        # ======================

        if os.path.isfile(
            midi_file
        ):


            with open(
                midi_file,
                "rb"
            ) as f:


                st.download_button(
                    "🎹 下載 MIDI",
                    f,
                    file_name="melody.mid",
                    mime="audio/midi"
                )



        # ======================
        # Download MusicXML
        # ======================

        if os.path.isfile(
            musicxml_file
        ):


            with open(
                musicxml_file,
                "rb"
            ) as f:


                st.download_button(
                    "🎼 下載 MusicXML",
                    f,
                    file_name="score.musicxml",
                    mime="application/xml"
                )



        # ======================
        # Download PDF
        # ======================

        if os.path.isfile(
            pdf_file
        ):


            with open(
                pdf_file,
                "rb"
            ) as f:


                st.download_button(
                    "📄 下載簡譜 PDF",
                    f,
                    file_name="jianpu.pdf",
                    mime="application/pdf"
                )


        else:


            st.error(
                "PDF沒有產生，請檢查 jianpu_pdf.py / LilyPond"
            )
       # =====================
       # 📦 ZIP下載按鈕
       # =====================

       if os.path.isfile(zip_file):

        with open(
        zip_file,
        "rb"
        ) as f:

        st.download_button(

            label="📦 一次下載全部 (ZIP)",

            data=f,

            file_name="JianpuTool_result.zip",

            mime="application/zip"

        )