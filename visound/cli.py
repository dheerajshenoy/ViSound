import argparse
from visound.core.TraversalMode import TraversalMode
from visound.core.Sonify import Sonify
import sounddevice as sd

def main():
    parser = argparse.ArgumentParser(description="Sonify an image into audio")
    parser.add_argument("image_path", help="Path to the input image")
    parser.add_argument("--width", type=int, default=256, help="Image width")
    parser.add_argument("--height", type=int, default=256, help="Image height")
    parser.add_argument("--dpc", type=float, default=0.01,
                        help="Duration per column (seconds)")
    parser.add_argument("--sample_rate", type=int, default=44100,
                        help="Sample rate of the audio")
    parser.add_argument("--play", action="store_true", help="Play the audio after generation")
    parser.add_argument("--mode",
                        choices=[
                        "left_to_right",
                        "right_to_left",
                        "top_to_bottom",
                        "bottom_to_top",
                        ],
                        default="left_to_right",
                        help="Traversal Mode\n"
                        "Modes are as follows:\n"
                        "left_to_right - Left to right\n"
                        "right_to_left - Right to left\n"
                        "top_to_bottom - Top to bottom\n"
                        "bottom_to_top - Bottom to top\n")
    parser.add_argument("--verbose", action="store_true", help="Detailed output")

    parser.add_argument("--output", type=str,
                        help="Path to the output file where the audio file should be saved")

    args = parser.parse_args()

    sonify = Sonify(
        file_path=args.image_path,
        dimension=(args.height, args.width),
        duration_per_column=args.dpc,
        sample_rate=args.sample_rate,
    )

    audio = None

    match args.mode:
        case "left_to_right":
            audio = sonify.LeftToRight()

        case "right_to_left":
            audio = sonify.RightToLeft()

        case "top_to_bottom":
            audio = sonify.TopToBottom()

        case "bottom_to_top":
            audio = sonify.BottomToTop()

    if args.verbose:
        print(f"Duration of audio: {sonify.duration()} seconds")

    if args.output:
        sonify.save(args.output)

    if args.play and audio is not None:
        print("Audio playback started: ")
        sd.play(audio, args.sample_rate)
        try:
            sd.wait()
        except KeyboardInterrupt:
            print("Playback cancelled")
