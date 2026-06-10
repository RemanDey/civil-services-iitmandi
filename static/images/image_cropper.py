import numpy as np
from PIL import Image
def crop_image(image_path, crop_box):
    """
    Crops an image based on the provided crop box.

    Parameters:
    - image_path: str, path to the input image.
    - crop_box: tuple, a tuple of (left, upper, right, lower) pixel coordinates.

    Returns:
    - cropped_image: PIL Image object of the cropped area.
    """
    # Open the image using PIL
    image = Image.open(image_path)

    # Crop the image using the provided crop box
    cropped_image = image.crop(crop_box)

    return cropped_image
crop_box = (10, 10, 10, 10)  # Example crop box (left, upper, right, lower)
cropped_image = crop_image('logo.png', crop_box)
cropped_image.save('cropped_image.png')  # Save the cropped image to a file