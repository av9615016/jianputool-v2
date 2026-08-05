import streamlit as st
import os
import uuid
import subprocess
import sys
import shutil


st.set_page_config(
    page_title="JianpuTool MVP 1.4",
    page_icon="🎵"
)


st.title("🎵 JianpuTool MVP 1.4")

st.write("""
MP3 / WAV / MIDI → MIDI → MusicXML → Jianpu PDF

Pipeline:

Audio
↓
BasicPitch MIDI
↓
MusicXML Clean
↓
jianpu_ly
↓
LilyPond PDF
""")


BASE = "outputs"

os.makedirs(BASE,exist_ok=True)


def run_cmd(cmd):

    st.code(" ".join(cmd))

    result=subprocess.run(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True
    )

    st.text(result.stdout)

    if result.returncode !=0:
        raise Exception(result.stdout)



upload=st.file_uploader(
    "上傳 MP3 / WAV / MIDI",
    type=[
        "mp3",
        "wav",
        "mid",
        "midi"
    ]
)



if upload:


    job=str(uuid.uuid4())[:8]

    outdir=os.path.join(
        BASE,
        job
    )

    os.makedirs(outdir,exist_ok=True)


    input_file=os.path.join(
        outdir,
        upload.name
    )


    with open(input_file,"wb") as f:
        f.write(upload.getbuffer())


    st.success(
        f"上傳完成: {upload.name}"
    )


    try:


        ext=upload.name.lower()


        # =====================
        # MIDI
        # =====================

        if ext.endswith(
            (".mid",".midi")
        ):

            midi=input_file


        else:

            midi=os.path.join(
                outdir,
                "melody.mid"
            )


            run_cmd(
            [
                sys.executable,
                "basicpitch_convert.py",
                input_file,
                midi
            ]
            )



        # =====================
        # MIDI
        # MusicXML
        # =====================


        raw_xml=os.path.join(
            outdir,
            "raw.musicxml"
        )


        run_cmd(
        [
            sys.executable,
            "midi_to_musicxml_clean.py",
            midi,
            raw_xml
        ]
        )



        clean_xml=os.path.join(
            outdir,
            "clean.musicxml"
        )


        run_cmd(
        [
            sys.executable,
            "clean_musicxml.py",
            raw_xml,
            clean_xml
        ]
        )



        final_xml=os.path.join(
            outdir,
            "final.musicxml"
        )


        run_cmd(
        [
            sys.executable,
            "jianpu_fix_musicxml.py",
            clean_xml,
            final_xml
        ]
        )



        # =====================
        # Jianpu LY
        # =====================


        ly=os.path.join(
            outdir,
            "final.ly"
        )


        run_cmd(
        [
            sys.executable,
            "-m",
            "jianpu_ly",
            final_xml
        ]
        )


        generated="final.ly"


        if os.path.exists(
            generated
        ):

            shutil.move(
                generated,
                ly
            )



        fixed_ly=os.path.join(
            outdir,
            "final_fix.ly"
        )


        run_cmd(
        [
            sys.executable,
            "ly_fix_v1.py",
            ly,
            fixed_ly
        ]
        )



        # =====================
        # Lilypond
        # =====================


        run_cmd(
        [
            "lilypond",
            "-o",
            os.path.join(
                outdir,
                "jianpu"
            ),
            "--pdf",
            fixed_ly
        ]
        )


        st.success(
            "🎉 轉換完成"
        )



        st.subheader(
            "下載"
        )


        files=[

            (
            "🎹 MIDI",
            midi
            ),

            (
            "🎼 MusicXML",
            final_xml
            ),

            (
            "🔢 簡譜 PDF",
            os.path.join(
                outdir,
                "jianpu.pdf"
            )
            ),

        ]



        for title,path in files:


            if os.path.exists(path):

                with open(
                    path,
                    "rb"
                ) as f:


                    st.download_button(
                        title,
                        f,
                        file_name=os.path.basename(path)
                    )



    except Exception as e:


        st.error(
            "❌ 轉換失敗"
        )

        st.exception(e)