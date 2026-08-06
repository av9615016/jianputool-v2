import sys
import os
import traceback


print("=" * 60)
print("BasicPitch Converter")
print("=" * 60)

print("Python:")
print(sys.executable)

print("Version:")
print(sys.version)

print("=" * 60)


# ==========================
# Import BasicPitch
# ==========================

try:

    import basic_pitch

    print(
        "basic_pitch:",
        basic_pitch.__file__
    )


    from basic_pitch.inference import predict


    print(
        "BasicPitch import OK"
    )


except Exception:

    print(
        "BasicPitch import failed"
    )

    traceback.print_exc()

    sys.exit(1)



# ==========================
# Arguments
# ==========================

if len(sys.argv) < 3:

    print(
        "Usage:"
    )

    print(
        "python basicpitch_convert.py input.wav output.mid"
    )

    sys.exit(1)



input_audio = sys.argv[1]

output_midi = sys.argv[2]



print("=" * 60)

print(
    "Input:",
    input_audio
)

print(
    "Output:",
    output_midi
)

print("=" * 60)



if not os.path.exists(input_audio):

    print(
        "找不到音檔:",
        input_audio
    )

    sys.exit(1)



# 建立輸出資料夾

output_dir = os.path.dirname(
    output_midi
)

if output_dir:

    os.makedirs(
        output_dir,
        exist_ok=True
    )



# ==========================
# BasicPitch Prediction
# ==========================

try:

    print(
        "開始 AI 分析..."
    )


    model_output, midi_data, note_events = predict(
        input_audio
    )


    print(
        "寫入 MIDI..."
    )


    midi_data.write(
        output_midi
    )


    print("=" * 60)

    print(
        "完成:"
    )

    print(
        output_midi
    )

    print("=" * 60)



except Exception:

    print(
        "BasicPitch 執行錯誤"
    )

    traceback.print_exc()

    sys.exit(1)