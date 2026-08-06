import streamlit as st
import os
import uuid


from vocal_separator import separate_vocal


st.title(
"🎵 JianpuTool Professional MVP 2.3"
)


file=st.file_uploader(
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


    audio=f"{job}/input.wav"


    open(
        audio,
        "wb"
    ).write(
        file.read()
    )


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
            audio,
            job
        )


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
        "📄 產生MusicXML"
        )


        os.system(
        f"""
        python midi_to_musicxml.py \
        {job}/melody.mid \
        {job}/score.musicxml
        """
        )


        st.success(
        "完成"
        )