"""
Given a directory of images, return a random one
"""

import os
import random


class ImagePicker:

    def choose_random_image(self, images_path):

        imgExtension = ["png", "jpeg", "jpg"]
        images = list()

        for img in os.listdir(images_path):
            ext = img.split(".")[len(img.split(".")) - 1]
            if (ext in imgExtension):
                images.append(img)
        choice = random.randint(0, len(images) - 1)
        chosen_image = images[choice]
        return f"{images_path}{chosen_image}"
