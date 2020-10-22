from PIL import Image


try:
    im = Image.open("./pictmp/pic0.jpg")

    width  = im.size[0]
    height = im.size[1]
    aspect = width / float(height)

    if width < height:
        #Portrait 4:5 1080 x 1350px

        ideal_width = 1080
        ideal_height = 1350


    elif width > height:
        #Landscape 1.91:1 1080 x 608px
        ideal_width = 1080
        ideal_height = 608
    else:
        #1:1 1080 x 1080:
        ideal_width = 1080
        ideal_height = 1080
    
    ideal_aspect = ideal_width / float(ideal_height)


    if aspect > ideal_aspect:
        # Then crop the left and right edges:
        new_width = int(ideal_aspect * height)
        offset = (width - new_width) / 2
        resize = (offset, 0, width - offset, height)
    else:
        # ... crop the top and bottom:
        new_height = int(width / ideal_aspect)
        offset = (height - new_height) / 2
        resize = (0, offset, width, height - offset)

    thumb = im.crop(resize).resize((ideal_width, ideal_height), Image.ANTIALIAS)
    thumb.save('image_thumbnail.jpg')

except IOError:
    print("cannot create thumbnail for '%s'" % infile)

