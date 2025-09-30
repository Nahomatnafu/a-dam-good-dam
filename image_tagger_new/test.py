import os
# Import the ImageTagger class from the ctagger module
from ctagger import ImageTagger

# Set the Google API key as an environment variable
# https://aistudio.google.com/app/api-keys
os.environ["GOOGLE_API_KEY"] = "AIzaSyBcEffoHhNRLKmurbqJZY0_tFiVtjc__Bg"

# Define the path to the target image to be tagged
target_img_path = r"images\trumpandelon.jpg"

# Define the path to an example image
example_img_path = r"images\elon.jpg"

# Create an instance of the ImageTagger
image_tagger = ImageTagger()

# Generate tags for the target image, using an example image for few-shot learning
# Note the example image is optional(The second argument). You can call tag() with just the target image path if you want.
tags = image_tagger.tag(target_img_path, [{"image_path": example_img_path, "label": "elon musk"}]) 


# print out the generated tags
print(tags)