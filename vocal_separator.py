import subprocess
import os


def separate_vocal(input_audio, output_dir):

    cmd = [
        "python",
        "-m",
        "demucs",
        "--two-stems=vocals",
        "-n",
        "htdemucs",
        input_audio
    ]

    subprocess.run(cmd, check=True)


    name = os.path.splitext(
        os.path.basename(input_audio)
    )[0]


    vocal = (
        f"separated/htdemucs/"
        f"{name}/vocals.wav"
    )


    return vocal