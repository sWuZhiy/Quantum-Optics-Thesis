from pathlib import Path

from faster_whisper import WhisperModel


AUDIO = Path(r"D:\下载\2026年09月23日 15点35分.m4a")
OUTPUT = Path(r"D:\codex\Quantum Optics Thesis\results\runs\audio_20260923\key_segment_1060_1410.txt")
CLIPS = "1060,1410"


def main() -> None:
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    model = WhisperModel("small", device="cpu", compute_type="int8")
    segments, info = model.transcribe(
        str(AUDIO),
        language="zh",
        beam_size=1,
        best_of=1,
        vad_filter=True,
        condition_on_previous_text=True,
        clip_timestamps=CLIPS,
    )
    with OUTPUT.open("w", encoding="utf-8") as stream:
        for segment in segments:
            line = f"[{segment.start:8.2f} --> {segment.end:8.2f}] {segment.text.strip()}"
            stream.write(line + "\n")
            stream.flush()


if __name__ == "__main__":
    main()
