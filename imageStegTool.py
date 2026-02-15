# steganography tool to decode/encode images from other images
# python 3.13.2
# jonah colon, finished mar 11th 2025
#
# ill explain how everything is done later
#
# TODO make it so you can payload images that are the same size or smaller than the carrier image

from PIL import Image, ImagePalette
from tkinter import Tk
from tkinter.filedialog import askopenfilename, asksaveasfilename

# create a root tkinter window
root = Tk()
root.attributes('-topmost', True)
root.withdraw()

# initialize variables
x = 0
y = 0
mode = ""
saveName = ""
COLOR_CODES = (0x00, 0x55, 0xAA, 0xFF)

# prompt user for mode, encoding or decoding
while mode != "d" and mode != "e": mode = input("Type \"d\" to decode an image or \"e\" to encode >>> ")

# open an image file, then take the width and height of the image
print("Carrier image >>> ", end="")
while True:
    try:
        inpCarrierFilename = askopenfilename(initialdir="\\", title="Select carrier image", filetypes=[("PNG", "*.png"), ("JPG", "*.jpg")])
        carrier = Image.open(inpCarrierFilename)
    except:
        print("\nDon't close out of the window please!")
    else:
        carrier = carrier.convert("RGB")
        print(inpCarrierFilename)
        break



####################################################################################################################################################################################################################################################################################################################################################################################################################################
if mode == "e":
    
    # prompt user for payload image
    print("Payload image >>> ", end="")
    while True:
        try:
            inpPayloadFilename = askopenfilename(initialdir="\\", title="Select payload image", filetypes=[("PNG", "*.png")])
            payload = Image.open(inpPayloadFilename)
        except:
            print("\nDon't close out of the window please!")
        else:
            payload = payload.convert("RGB")
            print(inpPayloadFilename)
            break

    if (payload.width * payload.height) != (carrier.width * carrier.height):
        raise Exception("payload image is different size than carrier image")
    


    # quantize payload image so it has a 6bpp color depth 
    sixb_pal = ImagePalette.ImagePalette("RGB", [0, 0, 0, 0, 0, 85, 0, 0, 170, 0, 0, 255, 85, 0, 0, 85, 0, 85, 85, 0, 170, 85, 0, 255, 170, 0, 0, 170, 0, 85, 170, 0, 170, 170, 0, 255, 255, 0, 0, 255, 0, 85, 255, 0, 170, 255, 0, 255, 0, 85, 0, 0, 85, 85, 0, 85, 170, 0, 85, 255, 85, 85, 0, 85, 85, 85, 85, 85, 170, 85, 85, 255, 170, 85, 0, 170, 85, 85, 170, 85, 170, 170, 85, 255, 255, 85, 0, 255, 85, 85, 255, 85, 170, 255, 85, 255, 0, 170, 0, 0, 170, 85, 0, 170, 170, 0, 170, 255, 85, 170, 0, 85, 170, 85, 85, 170, 170, 85, 170, 255, 170, 170, 0, 170, 170, 85, 170, 170, 170, 170, 170, 255, 255, 170, 0, 255, 170, 85, 255, 170, 170, 255, 170, 255, 0, 255, 0, 0, 255, 85, 0, 255, 170, 0, 255, 255, 85, 255, 0, 85, 255, 85, 85, 255, 170, 85, 255, 255, 170, 255, 0, 170, 255, 85, 170, 255, 170, 170, 255, 255, 255, 255, 0, 255, 255, 85, 255, 255, 170, 255, 255, 255])
    paletteReference = Image.new("P", (1, 1))
    paletteReference.putpalette(sixb_pal, "RGB")

    payload = payload.quantize(colors=64, method=Image.Quantize.MEDIANCUT, kmeans=0, palette=paletteReference, dither=Image.Dither.FLOYDSTEINBERG)
    payload = payload.convert("RGB")



    # useful method
    def encodeColorChannelVal(channelNum, encodedVal, cImage, xCoord, yCoord):
        val = format(int(cImage.getpixel((xCoord, yCoord))[channelNum]), "b")
        val = val[:-2] + encodedVal
        return int(val, 2)

    # loop through every pixel in the payload image
    print("Please wait...")
    for i in range((payload.width * payload.height)):
        # get color channel values of the current payload pixel, and convert them into a binary number, which will be between 0-3 inclusive
        writeToR = format(int(payload.getpixel((x, y))[0] / 85), "b")
        if len(writeToR) < 2: writeToR = "0" + writeToR

        writeToG = format(int(payload.getpixel((x, y))[1] / 85), "b")
        if len(writeToG) < 2: writeToG = "0" + writeToG

        writeToB = format(int(payload.getpixel((x, y))[2] / 85), "b")
        if len(writeToB) < 2: writeToB = "0" + writeToB


        # use the method defined earlier to combine the color channel values of the carrier image pixel and the payload pixel together, so the payload value is encoded into the carrier image value
        r = encodeColorChannelVal(0, writeToR, carrier, x, y)
        g = encodeColorChannelVal(1, writeToG, carrier, x, y)
        b = encodeColorChannelVal(2, writeToB, carrier, x, y)


        # put the encoded pixel back into the carrier image
        carrier.putpixel((x, y), (r, g, b))
        x += 1
        if x >= carrier.width:
            x = 0
            y += 1

    payload.close()

############################################################################################################################################

else:
    # useful method 2
    def getDecodedColor(channel, cImage, xCoord, yCoord): 
        componentVal = int(hex(cImage.getpixel((xCoord, yCoord))[channel])[-1], 16)
        return int(divmod(componentVal / 4, 1)[1] * 4)
    
    # loop through every pixel in the carrier image
    print("Please wait...")
    for i in range((carrier.width * carrier.height)):
        r = COLOR_CODES[getDecodedColor(0, carrier, x, y)]
        g = COLOR_CODES[getDecodedColor(1, carrier, x, y)]
        b = COLOR_CODES[getDecodedColor(2, carrier, x, y)]
        carrier.putpixel((x, y), (r, g, b))

        x += 1
        if x >= carrier.width:
            x = 0
            y += 1

####################################################################################################################################################################################################################################################################################################################################################################################################################################



# open a file dialog to choose the folder the encoded image will be saved in
root.iconify()
while True:
    try:
        saveName = asksaveasfilename(initialdir="\\", title="Save encoded/decoded image", filetypes=[("PNG", "*.png")])
        if saveName[-4:] != ".png": saveName += ".png"
        carrier.save(saveName)
    except:
        print("Image didn't save properly, don't close out of the window please!")
    else: break

root.destroy()
carrier.close()

input("Done! Press enter to quit. ")