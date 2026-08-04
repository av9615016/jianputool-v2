import streamlit as st
import os
import uuid
import subprocess
import shutil


st.set_page_config(
    page_title="JianpuTool",
    page_icon="🎵"
)

st.title("🎵 JianpuTool")
st.write("MP3 / WAV → MIDI → 主旋律 → 簡譜 PDF")


BASE_DIR = os.path.dirname(os.path.abspath(__file__))


UPLOAD_DIR = os.path.join(BASE_DIR, "uploads")
OUTPUT_DIR = os.path.join(BASE_DIR, "outputs")


os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(OUTPUT_DIR, exist_ok=True)



def run_cmd(cmd):

    st.write("執行:")
    st.code(" ".join(cmd))

    result = subprocess.run(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True
    )

    st.text(result.stdout)

    if result.returncode != 0:
        raise Exception(result.stdout)



uploaded = st.file_uploader(
    "上傳 MP3 / WAV",
    type=["mp3", "wav"]
)


if uploaded:

    job_id = str(uuid.uuid4())[:8]

    workdir = os.path.join(
        OUTPUT_DIR,
        job_id
    )

    os.makedirs(workdir, exist_ok=True)


    input_audio = os.path.join(
        workdir,
        uploaded.name
    )


    with open(input_audio, "wb") as f:
        f.write(uploaded.read())


    st.success("上傳完成")


    raw_mid = os.path.join(
        workdir,
        "raw.mid"
    )


    melody_mid = os.path.join(
        workdir,
        "melody.mid"
    )


    musicxml = os.path.join(
        workdir,
        "final.musicxml"
    )



    try:


        # 1. Audio -> MIDI
        st.info("1. BasicPitch 轉 MIDI")

        run_cmd([
            "python",
            "basicpitch_convert.py",
            input_audio,
            raw_mid
        ])


        if not os.path.exists(raw_mid):
            raise Exception(
                "raw.mid 產生失敗"
            )



        # 2. MIDI 主旋律抽取
        st.info("2. 抽取主旋律")

        run_cmd([
            "python",
            "extract_piano_melody_v5.py",
            raw_mid,
            melody_mid
        ])


        if not os.path.exists(melody_mid):
            raise Exception(
                "melody.mid 產生失敗"
            )



        # 3. MIDI -> MusicXML

        st.info("3. MIDI 轉 MusicXML")


        run_cmd([
            "python",
            "midi_to_musicxml_simple_v3.py",
            melody_mid,
            musicxml
        ])



        if not os.path.exists(musicxml):
            raise Exception(
                "MusicXML 產生失敗"
            )



        # 4. jianpu-ly

        st.info("4. 產生簡譜 LilyPond")


        run_cmd([
            "python",
            "-m",
            "jianpu_ly",
            musicxml
        ])



        ly_file = os.path.join(
            workdir,
            "final.ly"
        )


        # jianpu_ly 預設輸出 temp
        # 找最新 ly

        temp_dir = os.path.join(
            os.environ["LOCALAPPDATA"],
            "Temp"
        )


        found = None

        for f in os.listdir(temp_dir):

            if f.endswith(".ly"):

                if musicxml.replace(".musicxml","") in f:
                    found = os.path.join(
                        temp_dir,
                        f
                    )


        if found:

            shutil.copy(
                found,
                ly_file
            )

        else:
            raise Exception(
                "找不到 ly"
            )



        # 5. LilyPond

        st.info("5. LilyPond 產生 PDF")


        run_cmd([
            r"C:\lilypond-2.26.0\bin\lilypond.exe",
            ly_file
        ])



        pdf = ly_file.replace(
            ".ly",
            ".pdf"
        )


        if os.path.exists(pdf):

            st.success(
                "🎉 簡譜 PDF 完成"
            )


            with open(pdf,"rb") as f:

                st.download_button(
                    "下載簡譜 PDF",
                    f,
                    file_name="jianpu.pdf"
                )


        else:

            raise Exception(
                "PDF 產生失敗"
            )


    except Exception as e:

        st.error(
            str(e)
        )