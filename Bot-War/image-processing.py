

from skimage import data, color
from skimage import io
from skimage.transform import rescale, resize, downscale_local_mean
from matplotlib import pyplot as plt
from skimage import data
import os
import numpy
from PIL import Image
from numpy import asarray
img= Image.open('foo.png')
# img = data.astronaut()
data = asarray(img)
print(data)
top_left = img[:100, :100]
# image = color.rgb2gray(data.astronaut())
image_rescaled = rescale(img, 5, anti_aliasing=False)
# image_resized = resize(image, (image.shape[0] // 4, image.shape[1] // 4),
                    #    anti_aliasing=True)
# image_downscaled = downscale_local_mean(image, (4, 3))
plt.imshow(image_rescaled)
plt.show()