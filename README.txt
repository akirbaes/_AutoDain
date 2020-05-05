INSTALL:

Put this folder into DAIN_APP 
It should look like DAIN_APP ALpha\__AUTODAIN_TEMPLATES

Install Python
Install pillow and numpy
(You can click on install_python_dependencies.bat for that part)

USE:

Drag-and-drop gif files on DAINAUTO scripts to interpolate them using pretty good settings for transparent gifs.


DAINAUTOTEMPLATE_mode_1_interp_4_split_500_pad_200.bat
and
DAINAUTOTEMPLATE_mode_4_interp_4_split_500_pad_200.bat
You can edit the filename to edit these four parameters.
You can crack it open to save your own set of favorite parameters

You can then drag your gif file on 
extract_undithered_interpolation_(drop source file here).bat
if your version of DAIN-App still has dithering in the output (0.36 and lower)



If you have particularly sensitive pixel-art, you can drag it on 
DAINAUTO_pixelsafe_interpolation.bat
This will
1) Add a 1px border to your gif (DAIN-app tends to mush borders)
2) Upscale 4X the animation (bigger pixel=less loss of detail using DAIN)
3) Send it to DAIN-app with good params
4) Retrieve the undithered interpolation
5) Downscale back the image
6) Remove the 1px border
7) Cleanup :) 

If DAIN_app gives you a Memory Error, edit the file to have a lower section size and padding


Details:
Uses DAIN_APP's own ffmpeg.exe to create a palette from gif
Uses PIL and NUMPY to manipulate the images and create gifs
Uses gifsicle to Unoptimise gifs because PIL has trouble with reading transparency