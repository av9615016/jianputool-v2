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
MP3 / WAV / MIDI → 主旋律 → MusicXML → 簡譜 PDF

流程：

Audio
↓
BasicPitch
↓
extract_piano_melody_v5
↓
MIDI
↓
MusicXML
↓
Jianpu PDF
"""
)


UPLOAD_DIR="uploads"
OUTPUT_DIR="outputs"


os.makedirs(
    UPLOAD_DIR,
    exist_ok=True
)

os.makedirs(
    OUTPUT_DIR,
    exist_ok=True
)



# ======================
# 檢查套件
# ======================

try:

    from basic_pitch.inference import predict
    import music21

    st.success(
        "BasicPitch + music21 載入成功"
    )

except Exception:

    st.error(
        "套件錯誤"
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


    ext=os.path.splitext(
        uploaded_file.name
    )[1].lower()


    job=str(uuid.uuid4())[:8]


    workdir=os.path.join(
        OUTPUT_DIR,
        job
    )


    os.makedirs(
        workdir,
        exist_ok=True
    )


    input_file=os.path.join(
        workdir,
        uploaded_file.name
    )


    raw_mid=os.path.join(
        workdir,
        "raw.mid"
    )


    melody_mid=os.path.join(
        workdir,
        "melody.mid"
    )


    musicxml=os.path.join(
        workdir,
        "output.musicxml"
    )



    with open(
        input_file,
        "wb"
    ) as f:

        f.write(
            uploaded_file.getbuffer()
        )



    st.success(
        "上傳完成"
    )



    if st.button(
        "開始轉換"
    ):


        try:


            # ======================
            # Audio -> MIDI
            # ======================


            if ext in [
                ".mp3",
                ".wav"
            ]:


                st.info(
                    "BasicPitch分析..."
                )


                _, midi_data, _ = predict(
                    input_file
                )


                midi_data.write(
                    raw_mid
                )


                st.success(
                    "raw.mid完成"
                )


            else:


                shutil.copy(
                    input_file,
                    raw_mid
                )


                st.success(
                    "MIDI載入完成"
                )




            # ======================
            # 主旋律抽取
            # ======================


            st.info(
                "抽取主旋律..."
            )


            result=subprocess.run(
                [
                    sys.executable,
                    "extract_piano_melody_v5.py",
                    raw_mid,
                    melody_mid
                ],
                capture_output=True,
                text=True
            )


            st.code(
                result.stdout
            )


            if result.returncode!=0:

                st.error(
                    "主旋律抽取失敗"
                )

                st.code(
                    result.stderr
                )

                st.stop()



            st.success(
                "melody.mid完成"
            )




            # ======================
            # MIDI -> MusicXML
            # ======================


            st.info(
                "MIDI轉MusicXML..."
            )


            result=subprocess.run(
                [
                    sys.executable,
                    "midi_to_musicxml_simple_v3.py",
                    melody_mid,
                    musicxml
                ],
                capture_output=True,
                text=True
            )


            st.code(
                result.stdout
            )


            if result.returncode!=0:

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




            # ======================
            # Jianpu
            # ======================


            st.info(
                "產生簡譜..."
            )


            result=subprocess.run(
                [
                    sys.executable,
                    "-m",
                    "jianpu_ly",
                    musicxml
                ],
                capture_output=True,
                text=True
            )


            st.code(
                result.stdout
            )


            if result.returncode!=0:

                st.error(
                    "jianpu_ly失敗"
                )

                st.code(
                    result.stderr
                )

                st.stop()



            ly_path=None


            for root,dirs,files in os.walk(
                os.path.expanduser(
                    "tmp",
                )
            ):

                for f in files:

                    if f.endswith(".ly"):

                        ly_path=os.path.join(
                            root,
                            f
                        )



            if ly_path is None:

                st.error(
                    "找不到ly"
                )

                st.stop()




            # ======================
            # LilyPond
            # ======================


            st.info(
                "LilyPond產生PDF..."
            )


            if os.nam         

            else:

                lilypond="/usr/bin/lilypond"



            result=subprocess.run(
                [
                    lilypond,
                    ly_path
                ],
                capture_output=True,
                text=True
            )


            st.code(
                result.stdout
            )



            if result.returncode!=0:

                st.error(
                    "PDF失敗"
                )

                st.code(
                    result.stderr
                )

                st.stop()



            pdf=ly_path.replace(
                ".ly",
                ".pdf"
            )


            st.success(
                "🎉 PDF完成"
            )



            if os.path.exists(pdf):


                with open(
                    pdf,
                    "rb"
                ) as f:


                    st.download_button(
                        "下載簡譜PDF",
                        f,
                        file_name="jianpu.pdf",
                        mime="application/pdf"
                    )



            if os.path.exists(melody_mid):

                with open(
                    melody_mid,
                    "rb"
                ) as f:


                    st.download_button(
                        "下載主旋律 MIDI",
                        f,
                        file_name="melody.mid"
                    )



            if os.path.exists(musicxml):

                with open(
                    musicxml,
                    "rb"
                ) as f:


                    st.download_button(
                        "下載 MusicXML",
                        f,
                        file_name="output.musicxml"
                    )



        except Exception:


            st.error(
                "轉換錯誤"
            )

            st.code(
                traceback.format_exc()
            )