echo Drag and Drop several files to automatically interpolate them with the given parameters

REM Read movie mode value from filename (2nd value that's between the _ signs)
FOR /f "tokens=3 delims=_ " %%d in ("%~n0") DO (
    set mode=%%d
    )
REM Read interpolation value from filename (4th value that's between the _ signs)
FOR /f "tokens=5 delims=_ " %%d in ("%~n0") DO (
    set interp=%%d
    )
REM Read movie mode value from filename (6th value that's between the _ signs)
FOR /f "tokens=7 delims=_ " %%d in ("%~n0") DO (
    set sectionsize=%%d
    )
REM Read movie mode value from filename (8th value that's between the _ signs)
FOR /f "tokens=9 delims=_ " %%d in ("%~n0") DO (
    set sectionpadding=%%d
    )
    
CD "%~dp0"
FOR %%A IN (%*) DO (

echo ---- Calling DAIN on %%A ----
"%~dp0..\DAINAPP.exe" --cli True -i %%A -o "%%~dpnA\\" --output_name "%%~nA.gif" --loop 1 --pallete 1 --interpolations %interp% --downsample_fps 50 --frame_handling %mode% --split_size %sectionsize% --split_pad %sectionpadding% --alpha 2 --check_scene_change -1 --interpolation_algo 0 --audio_version 0 --clear_original_folder 1 --clear_interpolated_folder 0 --step_extract 1 --step_interpolate 1 --step_render 1 --clean_cache 1
echo ---- DAIN done ----
)

cmd \K