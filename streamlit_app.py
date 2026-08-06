import streamlit as st
import os
import uuid

from vocal_separator import separate_vocal
from pdf_generator import generate_pdf


st.set_page_config(
    page_title="JianpuTool Professional MVP 2.4",
    page_icon="🎵"
)


st.title(
    "🎵 JianpuTool Professional MVP 2.4"
)


file = st.file_uploader(
    "上傳 MP3/WAV",
    ["mp3","wav"]
)


if file:

    job=str(uuid.uuid4())

    os.makedirs(
        job,
        exist_ok=True
    )


    input_file=f"{job}/input.wav"


    with open(input_file,"wb") as f:
        f.write(file.read())


    st.success(
        "歌曲完成"
    )


    if st.button(
        "開始製作簡譜"
    ):


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



        st.write(
            "🎵 AI抓旋律"
        )


        os.system(
        f"""
        python basicpitch_convert.py \
        {vocal} \
        {job}/melody.mid
        """
        )



        st.write(
            "📄 MusicXML"
        )


        os.system(
        f"""
        python midi_to_musicxml.py \
        {job}/melody.mid \
        {job}/score.musicxml
        """
        )


        st.write(
            "📕產生PDF"
        )


        pdf=generate_pdf(
            f"{job}/score.musicxml",
            job
        )


        st.success(
            "完成"
        )


        with open(pdf,"rb") as f:

            st.download_button(
                "📕下載簡譜PDF",
                f,
                file_name="jianpu.pdf",
                mime="application/pdf"
            )
