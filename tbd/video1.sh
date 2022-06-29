#!/usr/bin/bash

ffmpeg -r 30 -f image2 -i "frames1/frame%04d.png" -vcodec libx264 -crf 25 -pix_fmt yuv420p animation.mkv

