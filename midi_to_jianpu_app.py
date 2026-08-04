import streamlit as st
import os
import uuid
import subprocess
import sys
import traceback


st.set_page_config(
    page_title="MIDI JianpuTool",
    page_icon="🎵"
)


st.title("🎵 MIDI → 簡譜 PDF")

st.write(
    "MID → MusicXML → 簡譜 PDF"
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



uploaded_file = st.file_uploader(
    "上傳 MIDI 檔",
    type=["mid", "midi"]
)



if uploaded_file:


    job_id = str(uuid.uuid4())


    midi_file = os.path.join(
        UPLOAD_DIR,
        job_id + ".mid"
    )


    raw_xml = os.path.join(
        OUTPUT_DIR,
        job_id + "_raw.musicxml"
    )


    quant_xml = os.path.join(
        OUTPUT_DIR,
        job_id + "_quant.musicxml"
    )


    fixed_xml = os.path.join(
        OUTPUT_DIR,
        job_id + "_fixed.musicxml"
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
        midi_file,
        "wb"
    ) as f:

        f.write(
            uploaded_file.getbuffer()
        )


    st.success(
        "MIDI 上傳完成"
    )



    if st.button(
        "開始轉換"
    ):


        # MIDI → MusicXML

        try:

            st.info(
                "MIDI 轉 MusicXML..."
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



        # Quantize

        try:

            st.info(
                "節拍修正..."
            )


            subprocess.run(
                [
                    sys.executable,
                    "final_quantize.py",
                    raw_xml,
                    quant_xml
                ]
            )


            st.success(
                "Quantize完成"
            )


        except Exception:

            st.error(
                "Quantize失敗"
            )

            st.stop()



        # Bar Fix

        try:

            st.info(
                "修正小節..."
            )


            subprocess.run(
                [
                    sys.executable,
                    "bar_split_fix.py",
                    quant_xml,
                    fixed_xml
                ]
            )


            st.success(
                "小節修正完成"
            )


        except Exception:

            st.error(
                "Bar Fix失敗"
            )

            st.stop()



        # MusicXML → Jianpu

        try:

            st.info(
                "產生簡譜..."
            )


            result = subprocess.run(
                [
                    sys.executable,
                    "-m",
                    "jianpu_ly",
                    fixed_xml
                ],
                capture_output=True,
                text=True
            )


            with open(
                ly_file,
                "w",
                encoding="utf-8"
            ) as f:

                f.write(
                    result.stdout
                )


            st.success(
                "簡譜檔完成"
            )


        except Exception:

            st.error(
                "jianpu失敗"
            )

            st.code(
                traceback.format_exc()
            )

            st.stop()



        st.success(
            "🎉 完成"
        )