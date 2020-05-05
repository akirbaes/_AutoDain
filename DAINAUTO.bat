CD "%~dp0"
FOR %%A IN (%*) DO (
REM For every file in the argument (drag&drop)
echo ---- Calling DAIN on %%A ----
"%~dp0\DAINAPP.exe" --cli True -i %%A -o "%%~dpnA\\" --output_name "%%~nA.gif" --loop 1
echo ---- DAIN done ----
)

cmd \K