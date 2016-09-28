gtk-recordmydesktop &

ffmpeg -i ~/out.ogv -sws_flags lanczos+accurate_rnd -vf "scale=1024:576" -c:v libx264 -crf 20 -preset veryslow -profile:v main -c:a copy sppas-about.mp4

rm ~/out.ogv


