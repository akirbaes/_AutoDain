import os
from PIL import Image
import numpy as np
alpha_limit = 130

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
                print("D:",dir(im))
                #input()
                
                im=im.convert(mode="P")#index_rgb_and_alpha(im,None,0)
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
    
def index_image(image,palette=None):
    #Does not care about alpha transparency: only use when transparency is not an issue
    if(palette!=None):
        #255: reserve one for transparency color (to rethink if there's already one)
        return image.quantize(colors=255, method=2, kmeans=0, palette=palette, dither=0)
    else:
        return image.quantize(colors=255, method=2, kmeans=0, dither=0)
        
def index_rgb_and_alpha(im,palette=None,transparency=0):      
    #Save the transparency areas beforehand because quantizing doesn't always respect it
    if(im.mode=="RGB" or im.mode=="RGBA"):
        im2, mask = reduce_and_get_rgba_transparency_area(im)
    elif(im.mode=="P"):
        mask = get_palette_transparency_area(im)
    else:
        print("Unhandled image mode:",im.mode)
    
    im2=im.convert("RGB") #"only RGB or L mode images can be quantized to a palette" says PIL
    #No RGBA, hence why the transparency has to be handled elsewheere
    im2 = index_image(im2,palette)
    if(palette==None):
        palette=im2
    im2.info["transparency"]=None
    del im2.info["transparency"]
    #im2.show()
    if not(mask is None):
        tr=unused_color(palette)
        #Either works, but 255 is more likely to be displaced later
        if(tr==None):
            print("Palette too full for transparency! Using 255")
            tr=255    #TODO: merge an existing color
        #Put the transparent areas back in
        im2=reset_transparency(im2,mask,tr)
        im2=swap_palette_colors(im2,tr,transparency) 
        im2.info["transparency"]=transparency
        # im2.show()
    return im2
def reduce_and_get_rgba_transparency_area(image,cutoff=alpha_limit):
    #Remove alpha transparency and makes a binary transparency mask
    if(image.mode=="RGB"):
        image=image.convert("RGBA")
    image=image.copy()
    data = np.array(image)
    alpha = data[:,:,3:]
    #Here: change data's rgb for alpha>alpha_limit
    alpha[alpha<=cutoff]=0
    alpha[alpha>cutoff]=255
    alphaonly = data[:,:,3].copy()//255
    #[TODO] try to fix the colors if they come from a black alpha overlay
    result = Image.fromarray(data)
    #print(np.unique(alphaonly))
    return result, alphaonly
def unused_color(image):
    #Returns unused palette index
    #PIL's ImagePalette doesn't actually work, so instead doing it by hand
    data = np.array(image)
    uniquecolors = set(np.unique(data))
    for i in range(256):
        if(i not in uniquecolors):
            return i
    return None

def get_palette_transparency_area(image):
    if(image.mode!="P"):
        input("Wrong input type")
    image=image.copy()
    tr = image.info.get("transparency",None)
    br = image.info.get("background",None)
    data = np.array(image)
    #print(br,tr,data) #Heavily optimised gifs will have issues here
    #Because some transparency areas are inherited from previous frames but with a different palette
    #Create a transparency mask where 1 is solid and 0 is transparent
    if(tr==0):
        data[data!=tr]=1
    else:
        data[data!=tr]=0
        data[data==tr]=2
        data[data==0]=1
        data[data==2]=0
    print("Transparency mask:",data)
    return data
    
def reset_transparency(pimage,mask,transparency=255):
    #Puts back the transparency areas on the image after quantization
    data = np.array(pimage)
    data = data*mask #Nullifies transparent areas
    mask = -(mask-1)*transparency
    maskimage = Image.fromarray(255+mask,"L")
    
    data = data+mask #Makes transparent area the transparency color
    result = Image.fromarray(data,"P")
    result.putpalette(pimage.getpalette())
    result.info["transparency"]=transparency
    
    # maskimage.show()
    # result.show()
    return result

def swap_palette_colors(image, source_id=None, target_id = 255):
    #Puts the source_id color at index target_id
    image=image.copy()
    palettedata = image.getpalette()
    if(source_id==None):
        source_id = get_background_color(image) #must be mode P to give an ID
    else:
        source_id = source_id
    if(source_id==target_id):
        return image
        
    source_index = source_id*3
    target_index = target_id*3
    #Swap the palette entries
    target_color = palettedata[target_index:target_index+3]
    source_color = palettedata[source_index:source_index+3]
    palettedata[target_index:target_index+3] = source_color
    palettedata[source_index:source_index+3] = target_color
    
    data = np.array(image)
    #Exchange the image areas
    source_mask = np.where(data==source_id,1,0)
    target_mask = np.where(data==target_id,1,0)
    data = np.where(source_mask==1,target_id,data)
    data = np.where(target_mask==1,source_id,data)
    
    result = Image.fromarray(data)
    result.putpalette(palettedata)
    return result
    
create_gif_from_folder()