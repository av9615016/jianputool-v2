import basic_pitch
import streamlit as st
import os
import uuid
import subprocess
import shutil


from vocal_separator import separate_vocal


# =========================
# 設定
# =========================

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


# =========================
# 上傳
# =========================


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



        # =====================
        # 人聲分離
        # =====================

        st.write(
            "🎤 人聲分離"
        )


        try:

            vocal = separate_vocal(
                input_file,
                job
            )


        except Exception as e:

            st.error(
                f"Demucs失敗:\n{e}"
            )

            st.stop()



        progress.progress(25)



        # =====================
        # BasicPitch MIDI
        # =====================


        st.write(
            "🎵 AI抓旋律"
        )


        midi_file = os.path.join(
            job,
            "melody.mid"
        )


        cmd = [

            "python",

            "basicpitch_convert.py",

            vocal,

            midi_file

        ]


        result = subprocess.run(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True
        )
        st.text(result.stdout)

        if result.returncode != 0:

            st.error(
                result.stderr
            )

            st.stop()



        progress.progress(50)



        # =====================
        # MIDI MusicXML
        # =====================


        st.write(
            "📄 自動簡譜"
        )


        musicxml = os.path.join(
            job,
            "score.musicxml"
        )


        subprocess.run(
            [
                "python",
                "midi_to_musicxml_clean.py",
                midi_file,
                musicxml
            ],
            check=True
        )


        progress.progress(70)



        # =====================
        # Jianpu PDF
        # =====================


        st.write(
            "🎼 PDF樂譜"
        )


        pdf_file = os.path.join(
            job,
            "jianpu.pdf"
        )


        try:

            subprocess.run(
                [
                    "python",
                    "jianpu_pdf.py",
                    musicxml,
                    pdf_file
                ],
                check=True
            )


        except Exception as e:

            st.warning(
                f"PDF產生失敗:{e}"
            )


        progress.progress(100)



        st.success(
            "🎉 製作完成"
        )



        # =====================
        # 下載
        # =====================


        if os.path.exists(
            midi_file
        ):


            with open(
                midi_file,
                "rb"
            ) as f:

                st.download_button(
                    "🎹 下載 MIDI",
                    f,
                    file_name="melody.mid"
                )



        if os.path.exists(
            musicxml
        ):


            with open(
                musicxml,
                "rb"
            ) as f:

                st.download_button(
                    "🎼 下載 MusicXML",
                    f,
                    file_name="score.musicxml"
                )



        if os.path.exists(
            pdf_file
        ):


            with open(
                pdf_file,
                "rb"
            ) as f:

                st.download_button(
                    "📄 下載簡譜 PDF",
                    f,
                    file_name="jianpu.pdf"
                )