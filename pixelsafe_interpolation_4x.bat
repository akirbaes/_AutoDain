if "%main%"=="" (
set main=pixelsafe
)

set interp=4
set split=300
set padding=100
   
   

FOR %%A IN (%*) DO (

"%~dp0\gifsicle.exe" --colors=255 "%%~dpnxA" -o "%%~dpnA o.gif"
"%~dp0\gifsicle.exe" -U "%%~dpnA o.gif" -o "%%~dpnA o.gif"
@echo Cropping
python "%~dp0\DAINAUTO_utils\crop_image.py" "%%~dpnA o.gif" 1

"%~dp0\gifsicle.exe" --colors=255 "%%~dpnA o+1.gif" -o "%%~dpnA o+1.gif"
"%~dp0\gifsicle.exe" -U "%%~dpnA o+1.gif" -o "%%~dpnA o+1.gif"


python "%~dp0\DAINAUTO_utils\scale_image.py" "%%~dpnA o+1.gif" %interp%

echo "Calling DAIN"

"%~dp0..\DAINAPP.exe" --cli True -i "%%~dpnA o+1_X%interp%.gif" -o "%%~dpnA\\" --output_name "%%~nA.gif" --loop 1 --pallete 1 --interpolations %interp% --downsample_fps 50 --frame_handling 4 --split_size %split% --split_pad %padding% --alpha 2 --check_scene_change -1 --interpolation_algo 0 --audio_version 0 --clear_original_folder 1 --clear_interpolated_folder 0 --step_extract 1 --step_interpolate 1 --step_render 1 --clean_cache 1


call "%~dp0\extract_undithered_interpolation_(drop source file here).bat" "%%~dpnxA"

python "%~dp0\DAINAUTO_utils\scale_image.py" "%%~dpnA interp.gif" -%interp% +nearest

python "%~dp0\DAINAUTO_utils\crop_image.py" "%%~dpnA interp_N%interp%.gif" -1

"%~dp0\gifsicle.exe" --colors=255 "%%~dpnA interp_N%interp%+-1.gif" -o "%%~dpnA interp_N%interp%+-1.gif"
"%~dp0\gifsicle.exe" -U "%%~dpnA interp_N%interp%+-1.gif" -o "%%~dpnA interp_N%interp%.gif"

del "%%~dpnA interp_N%interp%+-1.gif"

cd "%~dp0"

del "%%~dpnA o%%~xA"
del "%%~dpnA o+1%%~xA"
del "%%~dpnA o+1_X%interp%%%~xA"
move /Y "%%~dpnA interp.gif" "%%~dpnA\\%%~nA interp.gif"
)

if "%main%"=="pixelsafe" (
pause
)

