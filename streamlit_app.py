import streamlit as st
import os
import uuid
import traceback
import subprocess
import sys
import shutil


st.set_page_config(
    page_title="JianpuTool MVP 1.1",
    page_icon="🎵"
)


st.title("🎵 JianpuTool MVP 1.1")


st.write(
    """
    MP3 / WAV / MIDI → MusicXML → 簡譜 PDF

    MP3/WAV:
    BasicPitch → MIDI

    MIDI:
    直接轉簡譜
    """
)


UPLOAD_DIR = "uploads"
OUTPUT_DIR = "outputs"


os.makedirs(
    UPLOAD_DIR,
    exist_ok=True
)

os.makedirs(
    OUTPUT_DIR,
    exist_ok=True
)



# ======================
# 套件
# ======================

try:

    from basic_pitch.inference import predict
    import music21

    st.success(
        "BasicPitch + music21 載入成功"
    )

except Exception:

    st.error(
        "套件載入失敗"
    )

    st.code(
        traceback.format_exc()
    )

    st.stop()



uploaded_file = st.file_uploader(
    "上傳 MP3 / WAV / MIDI",
    type=[
        "mp3",
        "wav",
        "mid",
        "midi"
    ]
)



if uploaded_file:


    ext = os.path.splitext(
        uploaded_file.name
    )[1].lower()


    job_id = str(uuid.uuid4())



    input_file = os.path.join(
        UPLOAD_DIR,
        job_id + ext
    )


    midi_file = os.path.join(
        OUTPUT_DIR,
        job_id + ".mid"
    )


    raw_xml = os.path.join(
        OUTPUT_DIR,
        job_id + ".musicxml"
    )


    ly_file = os.path.join(
        OUTPUT_DIR,
        job_id + ".ly"
    )


    pdf_file = os.path.join(
        OUTPUT_DIR,
        job_id + ".pdf"
    )



    with open(
        input_file,
        "wb"
    ) as f:

        f.write(
            uploaded_file.getbuffer()
        )


    st.success(
        f"{uploaded_file.name} 上傳完成"
    )



    if st.button(
        "開始轉換"
    ):



        # ======================
        # MP3/WAV/MIDI
        # ======================

        try:


            if ext in [
                ".mp3",
                ".wav"
            ]:


                st.info(
                    "BasicPitch 分析音樂..."
                )


                _, midi_data, _ = predict(
                    input_file
                )


                midi_data.write(
                    midi_file
                )


                st.success(
                    "MIDI產生成功"
                )



            elif ext in [
                ".mid",
                ".midi"
            ]:


                st.info(
                    "直接使用 MIDI"
                )


                shutil.copy(
                    input_file,
                    midi_file
                )


                st.success(
                    "MIDI載入成功"
                )


        except Exception:


            st.error(
                "MIDI處理失敗"
            )

            st.code(
                traceback.format_exc()
            )

            st.stop()



        # ======================
        # MIDI → MusicXML
        # ======================

        try:


            st.info(
                "MIDI轉MusicXML..."
            )


            result = subprocess.run(
                [
                    sys.executable,
                    "midi_to_musicxml_clean.py",
                    midi_file,
                    raw_xml
                ],
                capture_output=True,
                text=True
            )


            if result.returncode != 0:


                st.error(
                    "MusicXML失敗"
                )


                st.code(
                    result.stderr
                )


                st.stop()



            st.success(
                "MusicXML完成"
            )


        except Exception:


            st.error(
                "MusicXML錯誤"
            )

            st.code(
                traceback.format_exc()
            )

            st.stop()



        # ======================
        # MusicXML → Jianpu
        # ======================

        try:


            st.info(
                "MusicXML轉簡譜..."
            )


            result = subprocess.run(
                [
                    sys.executable,
                    "-m",
                    "jianpu_ly",
                    raw_xml
                ],
                capture_output=True,
                text=True
            )


            if result.returncode != 0:


                st.error(
                    "jianpu_ly失敗"
                )


                st.code(
                    result.stderr
                )

                st.stop()



            with open(
                ly_file,
                "w",
                encoding="utf-8"
            ) as f:

                f.write(
                    result.stdout
                )


            st.success(
                "簡譜產生成功"
            )



        except Exception:


            st.error(
                "簡譜錯誤"
            )

            st.code(
                traceback.format_exc()
            )

            st.stop()



        # ======================
        # LilyPond PDF
        # ======================

        try:


            st.info(
                "LilyPond產生PDF..."
            )


            lilypond = shutil.which(
                "lilypond"
            )


            if lilypond is None:


                lilypond = (
                    r"C:\lilypond-2.26.0\bin\lilypond.exe"
                )



            result = subprocess.run(
                [
                    lilypond,
                    "-o",
                    pdf_file[:-4],
                    ly_file
                ],
                capture_output=True,
                text=True
            )



            if result.returncode != 0:


                st.error(
                    "PDF失敗"
                )


                st.code(
                    result.stderr
                )


                st.stop()



            st.success(
                "🎉 簡譜PDF完成"
            )



        except Exception:


            st.error(
                "LilyPond錯誤"
            )

            st.code(
                traceback.format_exc()
            )

            st.stop()



        # ======================
        # Download
        # ======================


        if os.path.exists(pdf_file):


            with open(
                pdf_file,
                "rb"
            ) as f:


                st.download_button(
                    "下載簡譜PDF",
                    f,
                    file_name="jianpu.pdf",
                    mime="application/pdf"
                )


        if os.path.exists(midi_file):


            with open(
                midi_file,
                "rb"
            ) as f:


                st.download_button(
                    "下載MIDI",
                    f,
                    file_name="output.mid",
                    mime="audio/midi"
                )


        if os.path.exists(raw_xml):


            with open(
                raw_xml,
                "rb"
            ) as f:


                st.download_button(
                    "下載MusicXML",
                    f,
                    file_name="output.musicxml",
                    mime="application/xml"
                )