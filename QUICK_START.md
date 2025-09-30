# Quick Start Guide - Integrated Media Catalog

## 🚀 Launch the Application

```bash
python run_media_catalog.py
```

---

## 📺 Main Interface Overview

```
┌─────────────────────────────────────────────────────────────────┐
│ File  Tools                                                      │
├─────────────────────────────────────────────────────────────────┤
│ [New Catalog] [Open Catalog] [Add Folder] [🔄 Refresh] │ [🎬 AI Stills Exporter] │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌──────────┬────────────────────────┬──────────────────────┐  │
│  │ Library  │   Files                │   File Info          │  │
│  │          │                         │                      │  │
│  │ 📁 My    │  video1.mp4  125MB     │  Preview:            │  │
│  │ Catalogs │  video2.mp4  98MB      │  [Thumbnail]         │  │
│  │          │  video3.mp4  156MB     │                      │  │
│  │ 📊 Test  │                         │  [▶ Play] [📁 Show] │  │
│  │  📁 Vids │                         │                      │  │
│  │          │                         │  File Details:       │  │
│  │          │                         │  Name: video1.mp4    │  │
│  │          │                         │  Size: 125 MB        │  │
│  │          │                         │                      │  │
│  │          │                         │  AI Generated Tags:  │  │
│  │          │                         │  president inch,     │  │
│  │          │                         │  smiling, office...  │  │
│  └──────────┴────────────────────────┴──────────────────────┘  │
│                                                                  │
│ Ready | Catalog: Test                                           │
└─────────────────────────────────────────────────────────────────┘
```

---

## 🎬 Complete Workflow

### 1️⃣ Process Videos with AI

**Click**: "🎬 AI Stills Exporter" button

A new window opens:

```
┌─────────────────────────────────────────────┐
│ AI Stills Exporter                          │
├─────────────────────────────────────────────┤
│                                             │
│ Source Folder:  [Browse...]                │
│ Output Folder:  [Browse...]                │
│                                             │
│ ☑ Enable AI Tagging with Few-Shot Learning │
│                                             │
│ Training examples: 3 (3 per category)      │
│ Categories: president_inch, buildings      │
│                                             │
│ [Start Export]                             │
│                                             │
│ Log:                                        │
│ ┌─────────────────────────────────────────┐│
│ │ Processing video1.mp4...                ││
│ │ Using 3 training examples               ││
│ │ ✓ Using LangChain + Gemini              ││
│ │ Analyzing 10 frames...                  ││
│ │ ✅ Saved AI analysis to video1_tags.xml ││
│ └─────────────────────────────────────────┘│
└─────────────────────────────────────────────┘
```

### 2️⃣ Create/Open Catalog

**Back in Media Catalog:**

- Click "New Catalog" → Enter name → "President Inch Videos"
- OR Click "Open Catalog" → Select existing .db file

### 3️⃣ Add Videos to Catalog

- Click "Add Folder"
- Select the output folder from Step 1
- Wait for scanning to complete

### 4️⃣ Browse and View Tags

- Click on any video in the file list
- See AI tags in the Info Panel on the right!

---

## 🔍 What You'll See

### When You Select a Video:

```
File Info
─────────────────────────

Preview:
┌─────────────────┐
│                 │
│  [Thumbnail]    │
│                 │
└─────────────────┘

[▶ Play]  [📁 Show in Explorer]

File Details:
Name: president_inch_speech.mp4
Size: 125.3 MB
Type: video

Embedded Keywords:
No embedded keywords

AI Generated Tags:
president inch, man, smiling, dark suit, 
eyeglasses, standing, office, desk, 
american flag, indoor, professional, 
formal, speaking, podium, microphone, 
audience, daytime, windows (18 total)
```

---

## 🎯 Key Features

### In Media Catalog:

✅ **Organize** - Create multiple catalogs for different projects  
✅ **Search** - Find videos by filename or keywords  
✅ **Preview** - See thumbnails and play videos  
✅ **Browse** - Navigate by folders  
✅ **Refresh** - Update metadata for all videos  

### In AI Stills Exporter:

✅ **Extract Frames** - Automatically extract key frames  
✅ **AI Analysis** - Recognize people, objects, actions  
✅ **Few-Shot Learning** - Recognize President Inch  
✅ **Fast Processing** - Optimized to 3 examples (5-7x faster)  
✅ **XML Storage** - Tags saved for catalog integration  

---

## 💡 Pro Tips

### For Best Results:

1. **Process first, catalog second**
   - Always run AI Stills Exporter before adding to catalog
   - This ensures AI tags are available

2. **Organize by project**
   - Create separate catalogs for different events/projects
   - Example: "President Inch 2024", "Campus Buildings", etc.

3. **Use descriptive folder names**
   - Folder names become searchable keywords
   - Example: "2024_Graduation_Ceremony"

4. **Enable metadata embedding** (optional)
   - Makes AI tags searchable in catalog
   - Requires ExifTool installed

### For Fast Processing:

1. **Default settings are optimized**
   - 3 training examples per category
   - Balanced speed and accuracy

2. **Process in batches**
   - Select folder with multiple videos
   - All processed automatically

3. **Close other apps**
   - Free up RAM and CPU for AI processing

---

## 🔧 Common Tasks

### Add More Training Images

```bash
# 1. Add images to folder
mkdir training_images/new_category
# Copy images to folder

# 2. Register images
python add_training_images.py
```

### Test President Inch Recognition

```bash
python test_president_inch_tagger.py
```

### View XML Tags Directly

```bash
python view_xml_results.py
```

### Refresh Catalog After Changes

1. Open catalog
2. Click "🔄 Refresh" button
3. Wait for re-scanning

---

## 📊 Performance

### AI Processing Speed:

- **Per frame**: ~2-3 seconds
- **10 frames**: ~30 seconds
- **30-second video**: ~30-40 seconds total

### Optimization:

- Uses only 3 training images (not all 43)
- 5-7x faster than before
- No loss in accuracy

---

## 🆘 Troubleshooting

### "No AI tags found"

**Cause**: Video not processed with AI tagging  
**Fix**: Run AI Stills Exporter on the video

### "AI Stills Exporter won't open"

**Cause**: Missing dependencies or API key  
**Fix**: 
```bash
pip install -r requirements.txt
python add_training_images.py
```

### "Video won't play"

**Cause**: No default video player  
**Fix**: Install VLC or Windows Media Player

### "Catalog is empty"

**Cause**: No folder added  
**Fix**: Click "Add Folder" and select video folder

---

## 📚 Documentation

- **INTEGRATION_GUIDE.md** - Detailed integration documentation
- **AI_TAGGING_GUIDE.md** - AI tagging features and setup
- **PERFORMANCE_OPTIMIZATION.md** - Speed optimization details
- **TESTING_INSTRUCTIONS.md** - Testing the AI tagger

---

## 🎉 You're Ready!

**Launch the app and start cataloging your videos with AI-powered tagging!**

```bash
python run_media_catalog.py
```

**Questions?** Check the documentation files or the log output for details.

**Enjoy your intelligent media catalog!** 🚀

