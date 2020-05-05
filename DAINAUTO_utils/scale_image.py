from PIL import Image
import os.path
import sys
import statistics
from gif_manips import swap_palette_colors

    
def get_background_color(image):
    return statistics.mode((image.getpixel((0,0)),image.getpixel((-1,0)),image.getpixel((0,-1)),image.getpixel((-1,-1))))

def majority_resample(image,zoom):
    bgc=get_background_color(image)
    #image.show()
    #pal = image.getpalette()
    #image = image.convert("RGB")
    #image.show()
    w,h = image.size
    w,h=int(round(w*zoom)),int(round(h*zoom))
    out = image.copy().crop((0,0,w,h))#Image.new(mode="RGB", size=(w,h))
    orig_pixels=[[list() for y in range(h)] for x in range(w)]
    
    #print(image.width,image.height,w,h)
    for x in range(image.width):
        for y in range(image.height):
            X=min(int(x*zoom),w-1)
            Y=min(int(y*zoom),h-1)
            orig_pixels[X][Y].append(image.getpixel((x,y)))
            #print(X,Y,x,y,image.getpixel((x,y)))
    #print(zoom)
    #print(orig_pixels)
    for x in range(out.width):
        for y in range(out.height):
            try:
                #print(x,y,len(orig_pixels[x][y]))
                if(bgc in orig_pixels[x][y]):
                    orig_pixels[x][y].remove(bgc) #remove one
                out.putpixel((x,y),statistics.mode(orig_pixels[x][y]))
            except Exception as e:
                print(e)
                pass
    #out = out.quantize(palette=pal,dither=0)
    return out
        

def scale_file(filename,zoom,mode="mode"):
    im = Image.open(filename)
    transparency = im.info.get("transparency",None)
    if(zoom<0):
        zoom=-1/zoom
    name,extension = os.path.splitext(filename)
    output = list()
    
    durations = list()
    disposals = list()
    #print(im.tell())
    try:
        while 1:
            w,h = im.size
            w,h=int(round(w*zoom)),int(round(h*zoom))
            
            duration = im.info.get('duration', None)
            if(duration is not None):
                durations.append(duration)
            disposal = im.disposal_method
            if(disposal is not None):
                disposals.append(disposal)
            #print(w,h)
            #print(mode)
            if(zoom>=1 or mode=="nearest"):
                output.append(im.resize((w,h),resample=Image.NEAREST))
            else:
                output.append(majority_resample(im,zoom))
            
            
            
            im.seek(im.tell()+1)
            #print(im.tell())
            # do something to im
    except EOFError:
        pass # end of sequence
        
        
    if(zoom<1 and 1/zoom==int(1/zoom)):
        zoomtext = "_D"+str(int(1/zoom))
        if(mode=="nearest"):
            zoomtext = "_N"+str(int(1/zoom))
            
    else:
        if(zoom==int(zoom)):
            zoom = int(zoom)
        zoomtext = "_X"+str(zoom)
    outname = name+zoomtext+extension
    #print(outname, file=sys.stdout)
    #Default: disposal=2
    #print(len(output),len(durations),len(disposals))
    #print(durations)
    #print(disposals) 
    for i in range(len(output)):
        out = output[i]
        tr = out.info.get('transparency', None)
        if(transparency!=None):
            #There exist at least one transparency
            if(tr!=None):
                out=swap_palette_colors(out,0,tr)
            else:
                out=swap_palette_colors(out,0,unused_color(out))
            out.info["transparency"]=0
        output[i]=out
    if(len(output)>1):
        if(transparency!=None):
            output[0].save(outname, save_all=True,append_images=output[1:], disposal=2, transparency=0, duration=durations, loop=0)
        else:
            output[0].save(outname, save_all=True,append_images=output[1:], disposal=2, duration=durations, loop=0)
    
    else:
        if(transparency!=None):
            output[0].save(outname)
        else:
            output[0].save(outname)
        
def is_float(value):
    try:
        float(value)
        return True
    except:
        return False

if __name__ == "__main__":
    import sys
    #print(sys.argv)
    if(len(sys.argv)>1):
        file = None
        zoom = None
        mode="mode"
        
        for arg in sys.argv[1:]:
            if(is_float(arg)):
                zoom = float(arg)
                
        for arg in sys.argv[1:]:
            if(arg[0]=="+"):
                mode=arg[1:]
                
        if not zoom:
            exit("Please provide a zoom value!")
        for arg in sys.argv[1:]:
            if(is_float(arg)):
                zoom = float(arg)
            elif(arg[0]=="+"):
                mode=arg[1:]
            else:
                file=arg
                scale_file(file,zoom,mode)
                #Multiple files: multiple calls
                #Multiple zooms: applied in-order
        if not file:
            exit("Please provide a file!")
    else:
        input("Usage: python scalevalueFLOAT Negative filetoscalePNG/GIF \nvalues will scale to 1/value rather than flipping\nmultiple values and files accepted in-order")
        