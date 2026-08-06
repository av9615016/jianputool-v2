import os
import sys
import pkgutil
import traceback

print("=" * 60)
print("Python Executable:")
print(sys.executable)
print("=" * 60)

print("Python Version:")
print(sys.version)
print("=" * 60)

print("sys.path:")
for p in sys.path:
    print(p)
print("=" * 60)

print("Searching basic_pitch package...")
print("Found:",
      any(m.name == "basic_pitch" for m in pkgutil.iter_modules()))
print("=" * 60)

try:
    import basic_pitch
    print("basic_pitch imported OK")
    print("Version:", getattr(basic_pitch, "__version__", "Unknown"))
except Exception:
    print("Failed to import basic_pitch")
    traceback.print_exc()
    sys.exit(1)

try:
    from basic_pitch.inference import predict
    print("predict imported OK")
except Exception:
    print("Failed to import predict")
    traceback.print_exc()
    sys.exit(1)

try:
    from basic_pitch.note_creation import model_output_to_notes
    print("note_creation imported OK")
except Exception:
    print("Failed to import note_creation")
    traceback.print_exc()
    sys.exit(1)

print("=" * 60)

if len(sys.argv) < 3:
    print("Usage:")
    print("python basicpitch_convert.py input.wav output.mid")
    sys.exit(1)

input_audio = sys.argv[1]
output_midi = sys.argv[2]

print("Input :", input_audio)
print("Output:", output_midi)

os.makedirs(os.path.dirname(output_midi), exist_ok=True)

try:
    model_output, midi_data, note_events = predict(input_audio)

    midi_data.write(output_midi)

    print("======================================")
    print("MIDI created successfully")
    print(output_midi)
    print("======================================")

except Exception:
    print("Prediction failed")
    traceback.print_exc()
    sys.exit(1)