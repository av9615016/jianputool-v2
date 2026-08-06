import streamlit as st
import os
import uuid
import subprocess


from vocal_separator import separate_vocal



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



file = st.file_uploader(
    "上傳 MP3/WAV",
    [
        "mp3",
        "wav"
    ]
)



if file:


    job=str(uuid.uuid4())


    os.makedirs(
        job,
        exist_ok=True
    )


    input_file=f"{job}/input.wav"


    with open(
        input_file,
        "wb"
    ) as f:

        f.write(
            file.read()
        )


    st.success(
        "歌曲上傳完成"
    )



    if st.button(
        "開始AI製作簡譜"
    ):



        # -----------------
        # Vocal Separation
        # -----------------

        st.write(
        "🎤 人聲分離"
        )


        vocal=separate_vocal(
            input_file,
            job
        )


        if isinstance(vocal,dict):

            st.error(
                vocal["error"]
            )

            st.stop()



        st.audio(
            vocal
        )



        # -----------------
        # BasicPitch
        # -----------------

        st.write(
        "🎵 AI抓旋律"
        )


        subprocess.run(
        [
        "python",
        "basicpitch_convert.py",
        vocal,
        f"{job}/melody.mid"
        ],
        check=True
        )



        midi=f"{job}/melody.mid"



        # -----------------
        # MusicXML
        # -----------------

        st.write(
        "📄 自動簡譜"
        )


        subprocess.run(
        [
        "python",
        "midi_to_musicxml_clean_v42_pro.py",
        midi,
        f"{job}/score.musicxml"
        ],
        check=True
        )



        # -----------------
        # Jianpu
        # -----------------

        st.write(
        "🎼 產生PDF"
        )


        subprocess.run(
        [
        "python",
        "jianpu_pdf.py",
        f"{job}/score.musicxml",
        job
        ],
        check=True
        )



        pdf=f"{job}/jianpu.pdf"



        st.success(
        "🎉 完成"
        )



        # download


        if os.path.exists(pdf):

            with open(
                pdf,
                "rb"
            ) as f:


                st.download_button(
                    "⬇下載簡譜PDF",
                    f,
                    "jianpu.pdf"
                )



        if os.path.exists(midi):

            with open(
                midi,
                "rb"
            ) as f:


                st.download_button(
                    "⬇下載MIDI",
                    f,
                    "melody.mid"
                )