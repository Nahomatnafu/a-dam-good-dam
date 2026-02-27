# Configuration Files

## Setup Instructions

### First Time Setup

1. **Copy the example file**:
   ```bash
   cp ai_config.json.example ai_config.json
   ```

2. **Get a Google API Key**:
   - Go to: https://aistudio.google.com/app/api-keys
   - Create a new API key
   - Copy the key

3. **Edit the config file**:
   ```bash
   # Windows
   notepad ai_config.json
   
   # Mac/Linux
   nano ai_config.json
   ```

4. **Add your API key**:
   ```json
   {
     "google_api_key": "YOUR_ACTUAL_API_KEY_HERE",
     "training_examples": {
       ...
     }
   }
   ```

5. **Add training images** (optional):
   ```bash
   python add_training_images.py
   ```

## Files

- **`ai_config.json.example`** - Template file (safe to commit to git)
- **`ai_config.json`** - Your actual config with API key (NOT in git, ignored)

## Security

⚠️ **NEVER commit `ai_config.json` to git!**

The file is already in `.gitignore` to prevent accidental commits.

If you accidentally commit it:
1. See `../SECURITY_FIX.md` for instructions
2. Revoke the exposed API key immediately
3. Create a new API key

## Configuration Options

### google_api_key
Your Google Gemini API key for AI image tagging.

### training_examples
Categories of training images for few-shot learning.

Example:
```json
{
  "google_api_key": "AIza...",
  "training_examples": {
    "president_inch": {
      "label": "President Inch",
      "images": [
        "training_images/president_inch/image1.jpg",
        "training_images/president_inch/image2.jpg"
      ]
    },
    "buildings": {
      "label": "campus building",
      "images": []
    }
  }
}
```

## Troubleshooting

### "No API key configured"
- Make sure `ai_config.json` exists (not just the .example file)
- Check that the API key is correctly formatted
- Verify the key is valid at https://aistudio.google.com/app/api-keys

### "Training examples not found"
- Run `python add_training_images.py` to scan and register images
- Check that training images exist in `training_images/` folder

### File not found error
- Make sure you copied `ai_config.json.example` to `ai_config.json`
- Check you're in the correct directory

