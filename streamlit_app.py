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
    直接轉換
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
# 套件測試
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
    "請上傳 MP3 / WAV / MIDI",
    type=[
        "mp3",
        "wav",
        "mid",
        "midi"
    ]
)



if uploaded_file:


    st.success(
        f"{uploaded_file.name} 上傳完成"
    )


    job_id = str(uuid.uuid4())


    # 取得副檔名

    ext = os.path.splitext(
        uploaded_file.name
    )[1].lower()



    # 原始檔

    input_file = os.path.join(
        UPLOAD_DIR,
        job_id + ext
    )


    # MIDI

    midi_file = os.path.join(
        OUTPUT_DIR,
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



    # 儲存上傳檔案

    with open(
        input_file,
        "wb"
    ) as f:

        f.write(
            uploaded_file.getbuffer()
        )



    if st.button(
        "開始轉換"
    ):
 # ======================
        # MP3 / WAV / MIDI 分流
        # ======================

        try:

            if ext in [".mp3", ".wav"]:

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
                    "MIDI 產生成功"
                )


            elif ext in [".mid", ".midi"]:

                st.info(
                    "偵測到 MIDI，直接使用"
                )


                shutil.copy(
                    input_file,
                    midi_file
                )


                st.success(
                    "MIDI 載入成功"
                )


            else:

                st.error(
                    "不支援的檔案格式"
                )

                st.stop()



        except Exception:

            st.error(
                "音訊/MIDI 處理失敗"
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
                    "MusicXML 產生失敗"
                )


                st.code(
                    result.stderr
                )


                st.stop()



            st.success(
                "MusicXML 產生成功"
            )



        except Exception:


            st.error(
                "MusicXML 錯誤"
            )


            st.code(
                traceback.format_exc()
            )


            st.stop()
 # ======================
        # Final Quantize
        # ======================

        try:

            st.info(
                "節拍量化修正..."
            )


            result = subprocess.run(
                [
                    sys.executable,
                    "final_quantize.py",
                    raw_xml,
                    quant_xml
                ],
                capture_output=True,
                text=True
            )


            if result.returncode != 0:

                st.error(
                    "final_quantize 失敗"
                )


                st.code(
                    result.stderr
                )


                st.stop()



            st.success(
                "節拍修正完成"
            )



        except Exception:


            st.error(
                "Quantize錯誤"
            )


            st.code(
                traceback.format_exc()
            )


            st.stop()



        # ======================
        # 修正小節線
        # ======================

        try:

            st.info(
                "修正小節線..."
            )


            result = subprocess.run(
                [
                    sys.executable,
                    "bar_split_fix.py",
                    quant_xml,
                    fixed_xml
                ],
                capture_output=True,
                text=True
            )


            if result.returncode != 0:

                st.error(
                    "小節修正失敗"
                )


                st.code(
                    result.stderr
                )


                st.stop()



            st.success(
                "小節修正完成"
            )



        except Exception:


            st.error(
                "小節修正錯誤"
            )


            st.code(
                traceback.format_exc()
            )


            st.stop()



        # ======================
        # MusicXML → Jianpu Lily
        # ======================

        try:

            st.info(
                "MusicXML 轉簡譜..."
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


            if result.returncode != 0:

                st.error(
                    "jianpu_ly 失敗"
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
                "簡譜 Lily 產生成功"
            )



        except Exception:


            st.error(
                "簡譜產生錯誤"
            )


            st.code(
                traceback.format_exc()
            )


            st.stop()
# ======================
        # LilyPond 產生 PDF
        # ======================

        try:

            st.info(
                "LilyPond 產生 PDF..."
            )


            lilypond = shutil.which(
                "lilypond"
            )


            st.write(
                "LilyPond path:",
                lilypond
            )


            if lilypond is None:

                st.error(
                    "找不到 LilyPond"
                )

                st.stop()



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
                    "PDF產生失敗"
                )


                st.code(
                    result.stderr
                )


                st.stop()



            st.success(
                "🎉 簡譜 PDF 完成"
            )



        except Exception:


            st.error(
                "PDF錯誤"
            )


            st.code(
                traceback.format_exc()
            )


            st.stop()



        # ======================
        # 下載 PDF
        # ======================

        if os.path.exists(
            pdf_file
        ):


            with open(
                pdf_file,
                "rb"
            ) as f:


                st.download_button(
                    "下載簡譜 PDF",
                    f,
                    file_name="jianpu.pdf",
                    mime="application/pdf"
                )



        # ======================
        # 下載 MIDI
        # ======================

        if os.path.exists(
            midi_file
        ):


            with open(
                midi_file,
                "rb"
            ) as f:


                st.download_button(
                    "下載 MIDI",
                    f,
                    file_name="output.mid",
                    mime="audio/midi"
                )



        # ======================
        # 下載 MusicXML
        # ======================

        if os.path.exists(
            fixed_xml
        ):


            with open(
                fixed_xml,
                "rb"
            ) as f:


                st.download_button(
                    "下載 MusicXML",
                    f,
                    file_name="output.musicxml",
                    mime="application/xml"
                )