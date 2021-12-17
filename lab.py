#!/usr/bin/env python3

import math

from PIL import Image as Image

# NO ADDITIONAL IMPORTS ALLOWED!


def get_pixel(image, x, y):
  
    # if x and y are not in bounds, we want to reassign the values
    if x not in range(image['width']):
        if x < 0: # everything to the left of the box will have x = 0
            x = 0
        else: # everything to the right of the box will have x equal to width-1
            x = image['width']-1
    
    if y not in range(image['height']): 
        if y < 0: # everything to the top of the box will have y equal to 0
            y = 0
        else: # everything below the box will have y equal to height-1
            y = image['height']-1
      
    # fixed error: turning (x,y) coordinates into an index      
    return image['pixels'][y* image['width'] + x]
    

def set_pixel(image, x, y, c):
    image['pixels'][y* image['width'] + x] = c


def apply_per_pixel(image, func):
    
    # create a dictionary to return 
    result = {
        'height': image['height'],
        'width': image['width'],
        'pixels': [0 for i in range(image['width']*image['height'])],
    }
    
    # iterate through each row and column and get the pixel value 
    for x in range(image['width']):
        for y in range(image['height']):
            color = get_pixel(image, x, y)
            newcolor = func(color) # new pixel value

            set_pixel(result, x, y, newcolor)
    return result


def inverted(image):
    
    # fixed error: pixel value is subtracted from 255 
    return apply_per_pixel(image, lambda c: 255-c)


# HELPER FUNCTIONS

def correlate(image, kernel):
    """
    Compute the result of correlating the given image with the given kernel.

    The output of this function should have the same form as a 6.009 image (a
    dictionary with 'height', 'width', and 'pixels' keys), but its pixel values
    do not necessarily need to be in the range [0,255], nor do they need to be
    integers (they should not be clipped or rounded at all).

    This process should not mutate the input image; rather, it should create a
    separate structure to represent the output.

    Kernel is a 1D array, similar to the 'pixels' value in the dictionary. 

    """
    
    # create a new image object that is the manipulated image 
    new_image = {
        'height': image['height'],
        'width': image['width'],
        'pixels': [0]*(image['width']*image['height']),
    }
      
    # create a list to store the new pixels 
    new_pixels = []
    
    for j in range(image['height']): # every row
        for i in range(image['width']): #every column

            # get kernel length so we know how to select the square from the image
            box = int((len(kernel))**0.5)//2

            # get the square of pixels from the image given the center pixel (x, y)
            image_box= [get_pixel(image, x_value, y_value) for y_value in range(j-box,j+box+1)\
                        for x_value in range(i-box,i+box+1)]
                                     
            # apply kernel
            kernel_on_im = [image_box[i]*kernel[i] for i in range(len(kernel))]
            
            # sum the values to get the new pixel value and update the list 
            new_pixel = sum(kernel_on_im)
            new_pixels.append(new_pixel)
       
    # update dictionary 
    new_image['pixels'] = new_pixels 
    
    return new_image
            
def box_blur(n):
    '''
    Given an odd integer n, returns a kernel as a list with n x n items, all identical.
    '''
    
    return [(1/n**2) for i in range(n**2)] 

def round_and_clip_image(image):
    """
    Given a dictionary, ensure that the values in the 'pixels' list are all
    integers in the range [0, 255].

    All values should be converted to integers using Python's `round` function.

    Any locations with values higher than 255 in the input should have value
    255 in the output; and any locations with values lower than 0 in the input
    should have value 0 in the output.
    """
    
    # create a new list with the same pixel values from the image 
    new_pixels = [pixel for pixel in image['pixels']]
    
    for i, pixel in enumerate(new_pixels): # iterate through the list 
        
        # change value if pixel is too hgh or too low, and update list value      
        if pixel < 0:
            pixel = 0 
            new_pixels[i] = pixel 
        elif pixel > 255:
            pixel = 255
            new_pixels[i] = pixel
    
    # update dictionary and round            
    image['pixels'] = [int(round(i)) for i in new_pixels]


# FILTERS

def blurred(image, n):
    """
    Return a new image representing the result of applying a box blur (with
    kernel size n) to the given input image.

    This process should not mutate the input image; rather, it should create a
    separate structure to represent the output.
    """
    
    # call box_blur to create the kernel
    kernel = box_blur(n)
    
    # correlation of the input image with that kernel
    new_image = correlate(image, kernel)
    
    # check that the output is valid 
    round_and_clip_image(new_image)
    
    return new_image

def sharpened(image,n):
    '''
    Returns a new image representing the result of subtracting the blurred pixel
    value from twice the original pixel of the given input image. 
    
    The output image is rounded and clipped. 
    '''
    
    # create a new dictionary for the new image with same dimensions
    new_image = {
        'height': image['height'],
        'width': image['width'],
        'pixels': [0]*(image['width']*image['height']),
    }
    
    # find intermediate blurred picture
    im_blurred = correlate(image, box_blur(n))
    
    # iterate through each row and column to get pixel values 
    for j in range(image['height']): 
        for i in range(image['width']): 
            
            # evaluate input image value and blurred value 
            image_val = get_pixel(image, i, j)
            val_blurred = get_pixel(im_blurred, i, j)
            
            # compute the new value and set the pixel value for the new image
            new_val = 2*image_val-val_blurred
            set_pixel(new_image, i, j, new_val)
    
    # make sure image is valid        
    round_and_clip_image(new_image)
    return new_image


def edges(image):
    ''' 

     Returns an image where the edges of the input image are emphasized.
     This process uses two kernels, Kx and Ky, which will be mathematically used.
    
    '''
    
    # new image representation
    new_image = {
        'height': image['height'],
        'width': image['width'],
        'pixels': [0]*(image['width']*image['height']),
    }  
    
    # set kernel values 
    kernel_x = [-1,0,1,-2,0,2,-1,0,1]
    kernel_y = [-1,-2,-1,0,0,0,1,2,1]
    
    # create two new images with the two given kernels 
    image_x = correlate(image, kernel_x)
    image_y = correlate(image, kernel_y)
    
    # create a new list for the new pixels 
    new_pixels = []
    
    # iterate through each row and column 
    for j in range(new_image['height']): 
        for i in range(new_image['width']): 
            
            # get the squared value of each image pixel 
            squared_val_x = get_pixel(image_x, i, j)**2
            squared_val_y = get_pixel(image_y, i, j)**2
            
            # sum the values, then take the square root and round 
            sqrt_val = round(math.sqrt(squared_val_x + squared_val_y))  
            
            # add the new values 
            new_pixels.append(sqrt_val)
      
    # update the new image dictionary 
    new_image['pixels'] = new_pixels

    # check to ensure that image is valid 
    round_and_clip_image(new_image)
    
    return new_image


# HELPER FUNCTIONS FOR LOADING AND S(tAVING IMAGES      

def load_image(filename):
    """
    Loads an image from the given file and returns a dictionary
    representing that image.  This also performs conversion to greyscale.

    Invoked as, for example:
       i = load_image('test_images/cat.png')
    """
    with open(filename, 'rb') as img_handle:
        img = Image.open(img_handle)
        img_data = img.getdata()
        if img.mode.startswith('RGB'):
            pixels = [round(.299 * p[0] + .587 * p[1] + .114 * p[2])
                      for p in img_data]
        elif img.mode == 'LA':
            pixels = [p[0] for p in img_data]
        elif img.mode == 'L':
            pixels = list(img_data)
        else:
            raise ValueError('Unsupported image mode: %r' % img.mode)
        w, h = img.size
        return {'height': h, 'width': w, 'pixels': pixels}


def save_image(image, filename, mode='PNG'):
    """
    Saves the given image to disk or to a file-like object.  If filename is
    given as a string, the file type will be inferred from the given name.  If
    filename is given as a file-like object, the file type will be determined
    by the 'mode' parameter.
    """
    out = Image.new(mode='L', size=(image['width'], image['height']))
    out.putdata(image['pixels'])
    if isinstance(filename, str):
        out.save(filename)
    else:
        out.save(filename, mode)
    out.close()


if __name__ == '__main__':
    # code in this block will only be run when you explicitly run your script,
    # and not when the tests are being run.  this is a good place for
    # generating images, etc.
    
    # image = load_image('test_images/bluegill.png')
    # print(get_pixel(image,1,2))
    # image_inverted = inverted(image)
    # save_image(image_inverted, 'bluegill_inverted.png', mode='PNG')
    
    # correlate({'height': 4, 'width': 3, 'pixels': [250, 250, 100, 50, 50, 100, 100, 255, 200, 200, 255, 255]}, 
    #           [0, 0, 0, 0, 1, 0, 0, 0, 0])
    
    # correlate({'height': 4, 'width': 3, 'pixels': [250, 250, 100, 50, 50, 100, 100, 255, 200, 200, 255, 255]}, 
    #           [0.0, 0.2, 0.0, 0.0, 0.2, 0.2, 0.0, 0.2, 0.0])
    

    # image = load_image('test_images/pigbird.png')
    # kernel_test = [0]*81
    # kernel_test[18] = 1
    # image_kernel = correlate(image, kernel_test)
    # save_image(image_kernel, 'pigbird_kernel.png', mode='PNG')
    
    # blurred({'height': 4, 'width': 3, 'pixels': [250, 250, 100, 50, 50, 100, 100, 255, 200, 200, 255, 255]}, 4)    
    # image = load_image('test_images/centered_pixel.png')
    # print(image['pixels'])
    
    # im = load_image('test_images/cat.png')
    # blurred_im = blurred(im, 5)
    # save_image(blurred_im, 'cat_blurred.png', mode='PNG')
    
    # im = load_image('test_images/python.png')
    # sharp_im = sharpened(im, 11)
    # save_image(sharp_im, 'python_sharpened.png', mode='PNG')
    
    image = load_image('test_images/centered_pixel.png')
    edge_image = edges(image)
    # save_image(edge_image, 'centered_pixel_edge.png', mode='PNG')
    
    # final_image = load_image('lab01/centered_pixel_edge.png')
    # final_image['pixels']
    
    # image = load_image('test_images/construct.png')
    # edge_image = edges(image)
    # save_image(edge_image, 'construct_edge.png', mode='PNG')
    
    