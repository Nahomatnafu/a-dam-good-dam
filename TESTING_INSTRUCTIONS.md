# Testing the President Inch AI Tagging

## The GUI is Now Open! 🎉

Follow these steps to test the AI tagging with your President Inch video:

## Step-by-Step Instructions

### 1. Configure Source and Output

In the GUI window:

- **Source Folder**: Click "Browse" and select the folder containing your President Inch video
- **Output Folder**: Click "Browse" and select where you want the frames and tags saved

### 2. Enable AI Tagging

- ✅ **Check the box**: "Enable AI Tagging with Few-Shot Learning"
- You should see status text showing:
  - "✓ LangChain + Gemini ready | 43 training examples"
  - "Training examples loaded: 43"
  - "Categories: president_inch, buildings"

### 3. Optional Settings

- **Image Format**: PNG (recommended) or JPG
- **Parallel workers**: Leave at default (4)
- **Embed metadata**: Optional - check if you want tags embedded in video files

### 4. Start Processing

- Click **"Start Export"** button
- Watch the log output in the bottom panel

### 5. What to Expect in the Log

You should see messages like:

```
Processing video: your_video.mp4
Extracting frames...
✓ Extracted 10 frames

AI Tagging enabled for your_video.mp4
Using 43 training examples for few-shot learning
  - President Inch: President-Edward-Inch-0001.jpg
  - President Inch: President-Edward-Inch-0002.jpg
  ...
✓ Using LangChain + Gemini for AI tagging

Found 10 images to analyze
  Analyzing your_video_0001.png...
  Analyzing your_video_0002.png...
  ...

✅ Saved AI analysis to your_video_tags.xml
```

### 6. Check the Results

After processing completes, navigate to your output folder:

```
output_folder/
  your_video_stills/
    your_video_0001.png  ← Extracted frames
    your_video_0002.png
    ...
    your_video_tags.xml  ← AI analysis with tags!
```

### 7. View the Tags

Open `your_video_tags.xml` to see the AI-generated tags:

```xml
<VideoTags>
  <Frame path="your_video_0001.png">
    <Labels>
      <Label confidence="0.950">president inch</Label>  ← Look for this!
      <Label confidence="0.950">man</Label>
      <Label confidence="0.950">smiling</Label>
      <Label confidence="0.950">dark suit</Label>
      ...
    </Labels>
  </Frame>
</VideoTags>
```

## Success Criteria

✅ **President Inch Detected**: Look for "president inch" in the tags  
✅ **Detailed Tags**: Should see 15-20 tags per frame  
✅ **Accurate Descriptions**: Tags should match what's in the frames  

## If President Inch is NOT Detected

This could mean:
1. President Inch is not visible in those particular frames
2. The video quality is very different from training images
3. President Inch is too small or obscured in the frame

**Try**:
- Check which frames were extracted (they might not include President Inch)
- Adjust frame extraction settings to get more frames
- Ensure President Inch is clearly visible in the video

## Troubleshooting

### Error: "No API key configured"
- Check `config/ai_config.json` has the API key

### Error: "No training examples"
- Run: `python add_training_images.py`

### GUI doesn't open
- Check terminal output for errors
- Ensure tkinter is installed: `python -m tkinter`

### Frames extracted but no tags
- Check "Enable AI Tagging" is checked
- Look for error messages in the log
- Verify API key is valid

## Next Steps After Testing

If President Inch detection works:

1. **Add Building Training Images**:
   - Create `training_images/buildings/` folder
   - Add campus building images
   - Run `python add_training_images.py`

2. **Process More Videos**:
   - Select folder with multiple videos
   - Batch process them all

3. **Use Tags for Search**:
   - Import tagged videos into Media Catalog
   - Search by "President Inch" keyword
   - Find all videos featuring him

## Current Status

✅ GUI is running  
✅ 43 President Inch training images loaded  
✅ LangChain + Gemini AI ready  
✅ Few-shot learning enabled  

**You're all set! Process your video and check the results!** 🚀

