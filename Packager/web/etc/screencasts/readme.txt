LINUX:


gtk-recordmydesktop &

ffmpeg -i ~/out.ogv -sws_flags lanczos+accurate_rnd -vf "scale=1024:576" -c:v libx264 -crf 20 -preset veryslow -profile:v main -c:a copy sppas-about.mp4

rm ~/out.ogv


===================================


WINDOWS:

ScreenPresso


Must trim the video 4 sec. before its end and re-encode to divide size by 2 without loosing quality:
(-to HH:MM:SS)

ffmpeg.exe -i original.mp4 -to 1:11 -c:v libx264 destination.mp4


Sous-titres : Subtitle Edit - à sauver en .vtt
Ne fonctionne pas encore sous Firefox...

