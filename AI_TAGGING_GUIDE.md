# AI Tagging with Few-Shot Learning Guide

## Overview

The Stills Exporter now includes advanced AI tagging powered by **LangChain + Google Gemini 2.5 Flash** with **few-shot learning** capabilities. This means the AI can learn to recognize specific people (like President Inch) or objects (like campus buildings) from example images you provide.

## Features

✅ **Automatic frame extraction** from videos  
✅ **AI-powered tagging** using Google Gemini  
✅ **Few-shot learning** - teach the AI to recognize specific subjects  
✅ **Detailed tag generation** - actions, objects, clothing, emotions, text  
✅ **Metadata embedding** into video files  
✅ **43 President Inch training images** already configured  

## Quick Start

### 1. Run the Stills Exporter GUI

```bash
python run_stills_exporter.py
```

### 2. Configure Settings

- **Source Folder**: Select folder containing your videos
- **Output Folder**: Where extracted frames and tags will be saved
- **Enable AI Tagging**: Check this box
- **Image Format**: PNG or JPG (PNG recommended for quality)

### 3. Process Videos

Click **Start Export** and the system will:
1. Extract frames from each video
2. Analyze each frame with AI
3. Generate tags (including "President Inch" if detected)
4. Save tags to XML files
5. Optionally embed metadata into videos

## Training Examples

### Current Training Data

**President Inch**: 43 training images configured  
- Location: `training_images/president_inch/`
- Label: "President Inch"
- Status: ✅ Ready to use

**Campus Buildings**: Ready for training images  
- Location: `training_images/buildings/` (create this folder)
- Label: "campus building"
- Status: ⏳ Awaiting images

### Adding More Training Images

#### For President Inch (add more examples):

1. Add images to `training_images/president_inch/`
2. Run: `python add_training_images.py`

#### For Buildings:

1. Create folder: `training_images/buildings/`
2. Add building images
3. Run: `python add_training_images.py`

## Configuration

### API Key

The Google API key is stored in `config/ai_config.json`:

```json
{
  "google_api_key": "YOUR_API_KEY_HERE",
  "training_examples": {
    "president_inch": {
      "label": "President Inch",
      "images": [...]
    }
  }
}
```

### Training Manager

Manage training images programmatically:

```python
from src.training_manager import TrainingManager

manager = TrainingManager()

# Add training example
manager.add_training_example(
    category="president_inch",
    label="President Inch",
    image_path="path/to/image.jpg"
)

# Get all training examples
examples = manager.get_training_examples()
```

## Testing

### Test President Inch Recognition

```bash
python test_president_inch_tagger.py
```

This will:
1. Load all training examples
2. Ask for a test image path
3. Analyze the image
4. Show if President Inch was detected

### Example Output

```
Generated 18 tags:
  1. ⭐ president inch ⭐
  2. man
  3. smiling
  4. dark suit
  5. eyeglasses
  ...

✅ SUCCESS! President Inch was recognized in the image!
```

## Output Files

### Frame Images

Extracted frames are saved as:
```
output_folder/
  video_name_stills/
    video_name_0001.png
    video_name_0002.png
    ...
```

### Tag XML Files

AI analysis is saved as:
```
output_folder/
  video_name_stills/
    video_name_tags.xml
```

XML structure:
```xml
<VideoTags>
  <Frame path="video_name_0001.png">
    <Labels>
      <Label confidence="0.950">president inch</Label>
      <Label confidence="0.950">man</Label>
      <Label confidence="0.950">smiling</Label>
      ...
    </Labels>
  </Frame>
</VideoTags>
```

## How Few-Shot Learning Works

1. **Training Phase**: You provide example images with labels
   - Example: 43 images of President Inch labeled "President Inch"

2. **Recognition Phase**: When analyzing new images:
   - AI compares the new image to training examples
   - If it finds a match, it uses your label
   - Also generates other descriptive tags

3. **Benefits**:
   - Recognizes specific individuals
   - Works with limited training data (few-shot)
   - More accurate than generic object detection

## Troubleshooting

### AI Tagging Not Working

**Check API Key**:
```bash
# View current config
cat config/ai_config.json
```

**Check Training Examples**:
```bash
python add_training_images.py
```

### No Tags Generated

1. Ensure AI Tagging is enabled in GUI
2. Check that training images exist
3. Verify API key is valid
4. Check log output for errors

### President Inch Not Detected

- Ensure training images are loaded (check GUI status)
- Image quality should be similar to training images
- President Inch should be clearly visible in the frame
- Try adding more diverse training images

## Advanced Usage

### Custom Categories

Add your own recognition categories:

1. Create folder: `training_images/your_category/`
2. Add images
3. Edit `config/ai_config.json`:
```json
{
  "training_examples": {
    "your_category": {
      "label": "Your Label",
      "images": []
    }
  }
}
```
4. Run: `python add_training_images.py`

### Batch Processing

The GUI supports batch processing:
- Select a folder with multiple videos
- All videos will be processed sequentially
- Each gets its own output folder and tags

## Performance

- **Frame Extraction**: ~1-2 seconds per video
- **AI Analysis**: ~2-3 seconds per frame
- **Total Time**: Depends on video length and frame count
  - 30-second video → ~10 frames → ~30 seconds analysis

## Requirements

- Python 3.8+
- FFmpeg (for video processing)
- LangChain packages (installed)
- Google API key with Gemini access

## Support

For issues or questions:
1. Check the log output in the GUI
2. Verify all dependencies are installed
3. Test with `test_president_inch_tagger.py`
4. Check training images are properly configured

---

**Ready to use!** Run `python run_stills_exporter.py` and process your first video with President Inch! 🎉

