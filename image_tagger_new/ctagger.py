import base64
import mimetypes
import warnings
from pathlib import Path
from typing import List, Dict, Optional

from langchain_core.messages import HumanMessage
from pydantic import BaseModel
from langchain_core.output_parsers import JsonOutputParser
from langchain.chat_models import init_chat_model

# Define a Pydantic schema for the expected JSON output.
class TaggingOutput(BaseModel):
    """Represents a list of tags for an image."""
    tags: List[str]

class ImageTagger:
    """A class to generate descriptive tags for an image using a multimodal LLM."""

    PROMPT_TEMPLATE = """
    <system_role>
    You are an Elite Image Tagging Specialist. Your primary task is to perform an exhaustive, detail-oriented analysis of an image and generate a list of highly accurate, descriptive tag keywords. You may be given examples to help you identify specific subjects.
    </system_role>

    <task_description>
    You will be provided with a target image to tag.
    Optionally, you may first be given one or more example images, each with a specific text label (e.g., a person's name).
    Your goal is to analyze the final target image and generate tags. If you recognize a subject from an example image in the target image, you **MUST** use the label provided in the example as one of the tags.
    </task_description>

    <instructions>
    1.  **Analyze and Tag:** Scrutinize the final target image and identify all visible elements.
    2.  **Few-Shot Recognition:** If example images are provided, first study them and their associated labels. Then, determine if the subject(s) from the examples appear in the target image. If a match is found, use the provided label (e.g., 'dave') as a tag.
    3.  **Strict Constraint (MANDATORY):** **ALL** other generated keywords *must* represent elements, text, actions, or emotions **directly and unequivocally visible** within the image.
    4.  **Forbidden Tags (with exceptions):**
        * **Do NOT** include generic colors (e.g., 'red', 'blue'). *Specific color descriptors are allowed (e.g., 'golden retriever').*
        * **Do NOT** infer, guess, or tag concepts that are not explicitly visible (e.g., if a dog is running, tag 'dog' and 'running', but not 'park' unless a park is visible).
        * **Do NOT** invent personal identifiers (names). Only use names if they are provided in the few-shot examples.
    5.  **Priority Tags (Detail Focus):** Prioritize descriptive tags covering:
        * **Actions:** Verbs describing what is happening (e.g., 'running', 'holding').
        * **Emotions:** Clearly visible facial expressions (e.g., 'smiling', 'laughing').
        * **Objects/Scenes:** Specific nouns for visible items and locations (e.g., 'smartphone', 'city skyline').
        * **Text:** If readable text appears, extract it and include it as a tag.
    6.  **Format Rules:**
        * Use **lowercase** for all tags.
        * Use singular nouns where appropriate, but allow multi-word descriptive phrases.
        * Remove duplicates and trim whitespace.
    </instructions>

    <output_format>
    Return strictly valid JSON and nothing else, in this exact shape. Do not include comments, explanations, or extra fields.

    {
    "tags": [
    "tag1",
    "tag2",
    "tag3"
    ]
    }
    </output_format>
    """

    def __init__(self, model_name: str = "gemini-2.5-flash", temperature: float = 0):
        """
        Initializes the ImageTagger.
        
        Args:
            model_name (str): The name of the model to use (e.g., "gemini-2.5-flash").
            temperature (float): The sampling temperature for the model.
        """
        self.llm = init_chat_model(model_name, model_provider="google_genai", temperature=temperature)
        self.parser = JsonOutputParser(pydantic_object=TaggingOutput)

    def tag(self, target_image_path: str, examples: Optional[List[Dict[str, str]]] = None) -> TaggingOutput:
        """
        Generates tags for a target image, optionally using example images for few-shot learning.

        Args:
            target_image_path (str): The file path to the target image to be tagged.
            examples (Optional[List[Dict[str, str]]]): A list of dictionaries,
                where each dictionary contains 'image_path' and a 'label' for that image.
                Example: [{'image_path': 'dave_1.jpg', 'label': 'dave'}]

        Returns:
            TaggingOutput: A Pydantic object containing a list of tags.
        """
        # Helper: encode image to base64 and detect its MIME type
        def encode_image(filepath):
            mime_type, _ = mimetypes.guess_type(filepath)
            if mime_type not in ("image/jpeg", "image/png", "image/gif", "image/webp"):
                # Fall back to jpeg for unknown types; Gemini accepts these four
                mime_type = "image/jpeg"
            with open(filepath, "rb") as image_file:
                data = base64.b64encode(image_file.read()).decode("utf-8")
            return data, mime_type

        # Start building the multimodal message content
        content = [{"type": "text", "text": ImageTagger.PROMPT_TEMPLATE}]

        # Add examples to the content if they are provided
        if examples:
            for example in examples:
                image_path = example.get('image_path')
                label = example.get('label')
                if not image_path or not label:
                    warnings.warn(
                        "Skipping example with missing 'image_path' or 'label'.",
                        UserWarning,
                    )
                    continue

                if not Path(image_path).exists():
                    warnings.warn(
                        f"Example image not found, skipping: {image_path}",
                        UserWarning,
                    )
                    continue

                # Add text introducing the example
                content.append({
                    "type": "text",
                    "text": f"--- EXAMPLE --- \nThis is an example image. The subject shown here should be identified and tagged with the label: '{label}'"
                })

                # Add the example image with the correct MIME type
                image_base64, mime_type = encode_image(image_path)
                content.append({
                    "type": "image_url",
                    "image_url": {"url": f"data:{mime_type};base64,{image_base64}"}
                })

        # Add text introducing the final target image
        content.append({
            "type": "text",
            "text": "--- TARGET IMAGE --- \nNow, analyze this target image. Generate tags for it based on all the instructions and any examples provided."
        })

        # Add the target image with the correct MIME type
        target_image_base64, target_mime = encode_image(target_image_path)
        content.append({
            "type": "image_url",
            "image_url": {"url": f"data:{target_mime};base64,{target_image_base64}"}
        })

        # Create the final multimodal message
        message = HumanMessage(content=content)
        
        # Invoke the chain and return the parsed Pydantic object
        response = self.llm.invoke([message])
        parsed_output = self.parser.parse(response.content)

        return parsed_output