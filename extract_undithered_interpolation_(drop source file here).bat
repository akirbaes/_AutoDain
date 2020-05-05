Echo Pass the source file next to its interpolated folder to create an interpolated gif without dithering.

FOR %%A IN (%*) DO (
"%~dp0..\ffmpeg" -i "%%~dpnxA" -vf palettegen=max_colors=256:stats_mode=full:reserve_transparent=1:transparency_color=0000FF "%%~dpnA\palette.png" -y

cd "%%~dpnA"

mkdir interpolated_gifs

cd interpolated_frames

FOR %%B IN (0*.png) DO (
"%~dp0..\ffmpeg" -i %%B -i "%%~dpnA\palette.png" -lavfi paletteuse=dither=0 "..\interpolated_gifs\%%~nB.gif" -y
) 

cd ..\interpolated_gifs

python "%~dp0\DAINAUTO_utils\create_gif_from_here.py"

cd ..

COPY "interpolated_gifs\output.gif" "%%~dpnA interp.gif" /Y
)

if "%main%"=="" (
pause
)
