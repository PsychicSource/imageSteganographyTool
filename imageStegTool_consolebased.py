# steganography tool to decode/encode images from other images
# python 3.13.2
# jonah colon, finished mar 11th 2025
#
# ill explain how everything is done later
#
# TODO make it so you can payload images that are the same size or smaller than the carrier image

from PIL import Image, ImagePalette

# initialize variables
x = 0
y = 0
mode = ""
saveName = ""
COLOR_CODES = (0x00, 0x55, 0xAA, 0xFF)

# prompt user for mode, encoding or decoding
while mode != "d" and mode != "e": mode = input("Type \"d\" to decode an image or \"e\" to encode >>> ")

# open an image file, then take the width and height of the image
print("Type the path of the carrier image here >>> ", end="")
while True:
    try:
        inpCarrierFilename = input()
        carrier = Image.open(inpCarrierFilename)
    except:
        print("\nFile not found, make sure to include the directory and file extension!")
    else:
        carrier = carrier.convert("RGB")
        break



####################################################################################################################################################################################################################################################################################################################################################################################################################################
if mode == "e":
    # prompt user for payload image
    print("Type the path of the payload image here >>> ", end="")
    while True:
        try:
            inpPayloadFilename = input()
            payload = Image.open(inpPayloadFilename)
        except:
            print("\nFile not found, make sure to include the directory and file extension!")
        else:
            payload = payload.convert("RGB")
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
print("Type the path and filename of where you want the image to be saved (include file extension!) >>> ", end="")
while True:
    try:
        saveName = input()
        carrier.save(saveName)
    except:
        print("\nFile not found, make sure to include the directory and file extension!")
    else:
        break

carrier.close()
input("Done! Press enter to quit. ")