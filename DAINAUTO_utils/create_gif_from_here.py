import os
from PIL import Image

def create_gif_from_folder(allow_dropped_frames=0):
    #Default duration for when there is not actually a duration name in the file
    #Allow_dropped_frames=1/True for when frames are 10ms (remove one out of two 10ms frames)
    #Allow_dropped_frames=2 to sacrifice as many frames as there is missing time (when interpolated too much)
    images = list()
    durations = list()
    previous_time = 0
    borrowed_time = 0
    total=0
    dropped = 0
    added = 0
    duration = 0
    transparencies = []
    for file in os.listdir(os.getcwd()):
        if file[0]=="0" and file.endswith(".gif") or file.endswith(".png"):
            total+=1
            im = Image.open(file)
            if(im.mode!="P"):
                print(im.mode)
                im=im.quantize(colors=255, method=2, kmeans=0, dither=0)
            #print(im.getpalette()[0:20])
            transparencies.append(im.info.get("transparency",None))
            
            try: #Load durations from timestamps
                time = int(file.split(".")[-2])
                if(time!=0):    #Not the first frame 
                    duration = time-previous_time
                    previous_time = time
                    if(duration==1):
                        #Mode 1 or 2, not an actual duration
                        duration = default_duration
                    elif(allow_dropped_frames):
                        #Try to deal with framerate>50 by dropping frames
                        duration-=borrowed_time
                        if(duration<=0): #As of now, don't sacrifice more than one frame (I suppose no input over 100fps)
                            if(allow_dropped_frames>1):
                                borrowed_time=-duration #Still longing
                                print(borrowed_time)
                            else:
                                borrowed_time=0 #Sacrifice accepted
                            dropped+=1
                            continue        #A real gestion of that would evenly space out the kept frames
                        elif(duration<20):
                            #I suppose borrow at most 10
                            borrowed_time = 20-duration
                            duration=20
                        else:
                            borrowed_time=0 #No issue
                    else:
                        #Force to 50fps
                        duration=max(20,duration)
            except Exception as e:
                duration = 20
            if(duration):
                durations.append(duration)
            images.append(im)
            added+=1
            # images[-1].show()
            #Puts the transparent color at index 255 so that I can simply pass 255 as transparency
            #It seems PIL reserves 255 for transparency anyway
            #Edit: but then optimize=True will make it so that there are less than 128 colors sometimes... so 0 is a safer bet
    print("Drop",dropped,"Add",added,"Total",total)
    durations+=[20]*(len(images)-len(durations)) #Fill the missing durations. Might get fixed if not using timestamps but actual values...
    #durations[-1]=1600
    # for im in images:
        # try:
            # del im.info['transparency']
        # except: pass
    print(len(images),len(durations))
    print(durations)
    print(transparencies)
    #optimize=True will only try to reduce the size of the palette
    images[0].save("output.gif", "GIF", save_all=True,append_images=images[1:], optimize=False,disposal=2, duration=durations, loop=0) 

create_gif_from_folder()