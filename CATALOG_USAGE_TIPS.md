# Media Catalog Usage Tips

## ⚠️ Important: What to Add to the Catalog

### The Problem You're Seeing

If you see only **images** (PNG files) in your catalog and no **videos** (MP4 files), it's because you added the **wrong folder** to the catalog.

### Understanding the Folder Structure

When you use the AI Stills Exporter, it creates this structure:

```
Your Videos Folder/
├── video1.mp4                    ← ORIGINAL VIDEO (add this folder!)
├── video2.mp4                    ← ORIGINAL VIDEO
├── video3.mp4                    ← ORIGINAL VIDEO
│
Output Folder/                    ← DON'T add this folder!
├── video1_stills/                ← Contains only PNG images
│   ├── video1_0001.png
│   ├── video1_0002.png
│   └── video1_tags.xml
├── video2_stills/
│   ├── video2_0001.png
│   └── video2_tags.xml
└── video3_stills/
    ├── video3_0001.png
    └── video3_tags.xml
```

### ✅ Correct: Add the Original Videos Folder

**Add the folder that contains the .mp4 files**, not the output folder with stills!

```
✅ CORRECT: Add "Your Videos Folder" (contains .mp4 files)
❌ WRONG: Add "Output Folder" (contains only _stills subfolders with .png files)
```

---

## 📋 Step-by-Step: Correct Workflow

### Option 1: Videos and Stills in Same Folder

If you want everything in one place:

1. **Process videos** with AI Stills Exporter
   - Source: `C:\Videos\MyVideos`
   - Output: `C:\Videos\MyVideos` (same folder!)
   - This creates `_stills` subfolders next to the videos

2. **Add to catalog**
   - Add folder: `C:\Videos\MyVideos`
   - Catalog will find: ✅ Videos (.mp4) + ✅ AI tags (from _stills/*.xml)

**Result**: Videos show in catalog with AI tags!

### Option 2: Videos and Stills in Separate Folders

If you already processed to a separate output folder:

1. **Your current situation**:
   - Original videos: `C:\Videos\Source`
   - Stills output: `C:\Videos\Analyzed`

2. **Add the SOURCE folder to catalog**:
   - Add folder: `C:\Videos\Source` (where the .mp4 files are!)
   - NOT: `C:\Videos\Analyzed`

3. **Move XML files to video location** (optional):
   - Copy `video1_tags.xml` from `Analyzed/video1_stills/` 
   - To: `Source/video1_stills/`
   - This allows catalog to find AI tags

**Result**: Videos show in catalog, AI tags show if XML files are accessible

---

## 🔍 Using the File Type Filter

The catalog now has a **file type filter** at the top of the Files panel:

```
Show: ⚪ All  ⚪ Videos  ⚪ Images
```

### How to Use:

1. **All** - Shows both videos and images (default)
2. **Videos** - Shows only .mp4, .mov, .avi, etc.
3. **Images** - Shows only .png, .jpg, etc.

### Why This Helps:

- If you accidentally added a stills folder, select "Videos" to see if any videos were found
- If you see 0 videos, you added the wrong folder!
- Use "Images" to see extracted frames if you want to catalog those separately

---

## 🎯 Recommended Workflow

### Best Practice: Keep Videos and Analysis Together

1. **Organize your source videos**:
   ```
   C:\Videos\
   ├── Project1\
   │   ├── video1.mp4
   │   └── video2.mp4
   └── Project2\
       ├── video3.mp4
       └── video4.mp4
   ```

2. **Process with AI Stills Exporter**:
   - Source: `C:\Videos\Project1`
   - Output: `C:\Videos\Project1` (same folder!)
   - Result:
     ```
     C:\Videos\Project1\
     ├── video1.mp4
     ├── video1_stills\
     │   ├── video1_0001.png
     │   └── video1_tags.xml  ← AI tags here!
     ├── video2.mp4
     └── video2_stills\
         └── video2_tags.xml
     ```

3. **Add to catalog**:
   - Add folder: `C:\Videos\Project1`
   - Catalog finds: Videos + AI tags automatically!

4. **Browse in catalog**:
   - Select video1.mp4
   - See AI tags in Info Panel
   - Search by tags

---

## 🔧 Fixing Your Current Situation

### If You Already Added the Wrong Folder:

**Option A: Start Fresh**

1. Create a new catalog
2. Add the correct folder (with .mp4 files)

**Option B: Add the Correct Folder**

1. Keep current catalog
2. Click "Add Folder" again
3. Select the folder with .mp4 files
4. Use filter to show "Videos" only

**Option C: Move Files**

1. Copy/move .mp4 files to the output folder
2. Refresh catalog (🔄 button)

---

## 📊 Checking What's in Your Catalog

### Status Bar Information

Look at the bottom of the window:

```
Loaded 27 files
```

This tells you how many files are in the catalog.

### With File Type Filter:

```
Showing 0 video files (of 27 total)
```

This means:
- ❌ 0 videos found
- ✅ 27 images found
- **You added the stills folder, not the videos folder!**

```
Showing 5 video files (of 32 total)
```

This means:
- ✅ 5 videos found
- ✅ 27 images found (probably the stills)
- **Correct! Videos are in the catalog**

---

## 🎬 Complete Example

### Scenario: You have videos of President Inch

1. **Your videos are here**:
   ```
   C:\Videos\PresidentInch\
   ├── speech1.mp4
   ├── speech2.mp4
   └── ceremony.mp4
   ```

2. **Process with AI Stills Exporter**:
   - Click "🎬 AI Stills Exporter"
   - Source: `C:\Videos\PresidentInch`
   - Output: `C:\Videos\PresidentInch` (same!)
   - Enable AI Tagging ✅
   - Start Export

3. **Result**:
   ```
   C:\Videos\PresidentInch\
   ├── speech1.mp4                    ← Video
   ├── speech1_stills\
   │   ├── speech1_0001.png
   │   └── speech1_tags.xml           ← AI tags
   ├── speech2.mp4                    ← Video
   ├── speech2_stills\
   │   └── speech2_tags.xml           ← AI tags
   ├── ceremony.mp4                   ← Video
   └── ceremony_stills\
       └── ceremony_tags.xml          ← AI tags
   ```

4. **Add to catalog**:
   - Back in Media Catalog
   - Click "New Catalog" → "President Inch Videos"
   - Click "Add Folder"
   - Select: `C:\Videos\PresidentInch`
   - Wait for scanning

5. **Browse**:
   - See 3 videos in file list
   - Select "speech1.mp4"
   - Info Panel shows:
     - File details
     - AI Generated Tags: "president inch, smiling, podium..."

6. **Filter** (optional):
   - Click "Videos" radio button
   - See only the 3 videos (hides the PNG stills)

---

## 💡 Pro Tips

### Tip 1: Use Separate Output for Testing

When testing, use a separate output folder:
- Source: `C:\Videos\Test`
- Output: `C:\Videos\Test_Analyzed`

Then you can compare before/after without mixing files.

### Tip 2: Catalog the Source Videos

Always catalog the **source videos**, not the analysis output:
- Add to catalog: `C:\Videos\Test` (source)
- AI tags will be found if XML files are in `Test/video_stills/` folders

### Tip 3: Use the Filter

After adding a folder, use the filter to check:
- Click "Videos" → See how many videos were found
- Click "Images" → See how many images were found

### Tip 4: Check the Status Bar

Always check the status bar after adding a folder:
- "Added 5 files" → Check if this is the right number
- Use filter to see breakdown

---

## ✅ Quick Checklist

Before adding a folder to the catalog, verify:

- [ ] Folder contains .mp4, .mov, or other video files
- [ ] Not just PNG images or _stills subfolders
- [ ] If AI tags are needed, XML files are accessible
- [ ] Folder path is correct

After adding a folder:

- [ ] Check status bar for file count
- [ ] Use "Videos" filter to verify videos were added
- [ ] Select a video to test if AI tags appear
- [ ] If no videos, remove catalog and add correct folder

---

## 🆘 Still Having Issues?

### No videos showing up?

1. Click "Videos" filter
2. Check status bar
3. If "0 video files", you added the wrong folder
4. Add the folder with .mp4 files instead

### AI tags not showing?

1. Verify XML file exists: `video_name_stills/video_name_tags.xml`
2. Check XML file is in correct location
3. Re-process video with AI tagging if needed

---

**Remember**: Add the folder with **.mp4 files**, not the folder with **.png stills**! 🎬

