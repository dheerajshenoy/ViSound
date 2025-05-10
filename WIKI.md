# WIKI for ViSound

Welcome to the wiki for visound

# Options/Flags

* `--output` accepts a path to an audio file (requires the extension also) where the generated audio will be saved.
If you want to output to stdout specify with `-`.
* `--play` plays the audio generated from the image
* `--verbose` shows detailed information about the audio generated
* `--mode` image traversal mode. Defaults to **left to right**. It can be one of:

    + left_to_right
    + right_to_left
    + top_to_bottom
    + bottom_to_top

* `--width` resize the input image to this width (default 256)
* `--height` resize the input image to this height (default 256)
* `--dpc` the duration per column in seconds. Higher the value longer the generated audio.
* `--sample_rate` sampling rate of the audio

## Example

1. stdout the audio to play using something like `mpv` media player

```
visound
```
