import os
# Import the ImageTagger class from the ctagger module
from ctagger import ImageTagger

# Load the Google API key from the environment — never hardcode secrets in source files.
# Set it before running:  $env:GOOGLE_API_KEY = "your_key_here"
# Or use a .env file with python-dotenv: pip install python-dotenv
# Get your key at: https://aistudio.google.com/app/api-keys
api_key = os.environ.get("GOOGLE_API_KEY")
if not api_key:
    raise EnvironmentError(
        "GOOGLE_API_KEY environment variable is not set. "
        "Please set it before running this script."
    )
os.environ["GOOGLE_API_KEY"] = api_key  # ensure it is set for downstream libraries

# Define the path to the target image to be tagged
target_img_path = r"images\target.jpg"

# Define the path to an example image
example_img_path = r"images\example.jpg"

# Create an instance of the ImageTagger
image_tagger = ImageTagger()

# Generate tags for the target image, using an example image for few-shot learning
# Note the example image is optional (the second argument).
# You can call tag() with just the target image path if you want.
tags = image_tagger.tag(target_img_path, [{"image_path": example_img_path, "label": "example label"}])

# print out the generated tags
print(tags)