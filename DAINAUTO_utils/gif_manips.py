from PIL import Image
import PIL
import os.path
import os
import numpy as np 
alpha_limit = 130
from statistics import mode

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
    
def remove_unused_color_from_palette(image):
    #The image will be turned into a palette square
    #[TODO] Gif:do it for every frame and group all the colors in one image
    palettedata = image.getpalette()
    data = np.array(image)
    
    uniquecolors = np.unique(data)
    if(image.info.get("transparency",None) != None):
        #Remove transparent, because we don't quantize with it
        tv = image.info.get("transparency")
        uniquecolors = uniquecolors[uniquecolors!=tv]
        #Optional: remove it from the frame too
        #Chose a color that is NOT tranparency, but exists otherwise
        fill = uniquecolors[0]
        data[data==tv]=fill
        
    uniquergb = [tuple(palettedata[x*3:x*3+3]) for x in uniquecolors]
    palettesize = len(uniquergb)
    newpalette = list()
    for rgb in uniquergb:
        newpalette.extend(rgb)
    while len(newpalette)<3*256:
        newpalette.extend(min(uniquergb)) #Fill with +/-darkest color
    
    # newpalette[0:palettesize] are the used colors
    # print("Unique colors:",len(uniquecolors))
    # print(uniquecolors)
    image=image.resize((16,16))
    data = np.array(image)
    for i in range(256):
        data[i//16][i%16]=min(i,len(uniquergb)-1)
    image=Image.fromarray(data)
    # image.info["transparency"]=255 #Rethink: Not sure for images that have 256 colors
    #Plus later quantization reserves one color anyway
    image.putpalette(newpalette)
    # image.show()
    return image
    
def get_outline_color(image):
    #For pixel-art that has outline
    #Looks at the first pixels on every side
    bgc = get_background_color(image)
    colors = list()
    for j in range(image.height):
        for i in range(image.width):
            col = image.getpixel((i,j))
            if(col)!=bgc:
                colors.append(col)
                break
    # print(colors)
    return mode(colors) #Majority wins

def get_background_color(image):
    #For pixel-art with solid background
    #Looks at all the 4 corners
    return mode((image.getpixel((0,0)),image.getpixel((-1,0)),image.getpixel((0,-1)),image.getpixel((-1,-1))))

def unused_color(image):
    #Returns unused palette index
    #PIL's ImagePalette doesn't actually work, so instead doing it by hand
    data = np.array(image)
    uniquecolors = set(np.unique(data))
    for i in range(256):
        if(i not in uniquecolors):
            return i
    return None

def index_image(image,palette=None):
    #Does not care about alpha transparency: only use when transparency is not an issue
    if(palette!=None):
        #255: reserve one for transparency color (to rethink if there's already one)
        return image.quantize(colors=255, method=2, kmeans=0, palette=palette, dither=0)
    else:
        return image.quantize(colors=255, method=2, kmeans=0, dither=0)

def reverse_black_blending(image):
    #Doesn't work.
    #https://stackoverflow.com/questions/2139350/what-is-the-formula-for-extracting-the-src-from-a-calculated-blendmode
    if(image.mode!=("RGBA")):
        print("Wrong image mode for this")
        return image
    data = np.array(image)
    
    width,height=image.size
    for x in range(width):
        for y in range(height):
            rn,gn,bn,alpha=data[y][x]
            if(alpha<255 and alpha>0):
                a=alpha/255
                data[y][x] = (min(int(round(rn/a)),255),min(int(round(gn/a)),255),min(int(round(bn/a)),255),255)
    result = Image.fromarray(data)
    result.show()
    return result

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
    