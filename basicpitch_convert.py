import sys

from basic_pitch.inference import predict
from basic_pitch import ICASSP_2022_MODEL_PATH


from basic_pitch import inference


def convert(audio, output):

    print("BasicPitch AI")


    model_output = predict(
        audio,
        ICASSP_2022_MODEL_PATH
    )


    midi = model_output[1]

    midi.write(
        output
    )


if __name__=="__main__":

    convert(
        sys.argv[1],
        sys.argv[2]
    )