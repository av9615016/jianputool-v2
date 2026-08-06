# =====================================================
# JianpuTool Professional MVP 2.3
# 🎤 Demucs Vocal Separation
# Python 3.10 / 3.11
# =====================================================

import os
import subprocess


def separate_vocal(input_audio, output_dir):

    print("=" * 60)
    print("🎤 Demucs Vocal Separation")
    print("=" * 60)


    # 取得檔名
    filename = os.path.basename(input_audio)

    name = os.path.splitext(filename)[0]


    print("Input:")
    print(input_audio)


    # Demucs command
    cmd = [
        "demucs",
        "--two-stems=vocals",
        "-n",
        "htdemucs",
        input_audio
    ]


    print("Running:")
    print(" ".join(cmd))


    try:

        result = subprocess.run(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True
        )


    except Exception as e:

        return {
            "error":
            f"Demucs啟動失敗:\n{str(e)}"
        }



    print(result.stdout)


    # Demucs失敗
    if result.returncode != 0:

        return {
            "error":
            "Demucs執行失敗:\n\n"
            + result.stdout
        }



    # Demucs輸出位置

    possible_paths = [

        os.path.join(
            "separated",
            "htdemucs",
            name,
            "vocals.wav"
        ),


        os.path.join(
            "separated",
            "htdemucs",
            name,
            "vocals.wav"
        ),


        os.path.join(
            os.path.dirname(input_audio),
            "separated",
            "htdemucs",
            name,
            "vocals.wav"
        )

    ]



    for path in possible_paths:

        if os.path.exists(path):

            print("取得人聲:")
            print(path)

            return path



    return {

        "error":
        "Demucs完成，但是找不到 vocals.wav\n\n"
        "輸出:\n"
        + result.stdout

    }