import subprocess
import os


def separate_vocal(input_audio, output_dir):

    name = os.path.splitext(
        os.path.basename(input_audio)
    )[0]


    cmd = [
        "python",
        "-m",
        "demucs",
        "--two-stems=vocals",
        "-n",
        "htdemucs",
        input_audio
    ]


    result = subprocess.run(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True
    )


    print(result.stdout)


    if result.returncode != 0:

        return {
            "error": result.stdout
        }


    vocal = os.path.join(
        "separated",
        "htdemucs",
        name,
        "vocals.wav"
    )


    return vocal