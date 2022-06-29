#!/usr/bin/bash

ffmpeg -r 60 -f image2 -i "frames1/frame%04d.png" -vcodec libx264 -crf 30 -pix_fmt yuv420p animation.mkv

