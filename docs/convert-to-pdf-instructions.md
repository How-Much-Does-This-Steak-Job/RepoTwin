# Converting RepoTwin Presentation to PDF

The presentation file `RepoTwin-Presentation.md` has been created in Markdown format. Here are several ways to convert it to PDF:

## Method 1: Using Marp (Recommended for Presentations)

Marp is designed specifically for creating presentation slides from Markdown.

### Installation:
```bash
# Install Marp CLI
npm install -g @marp-team/marp-cli

# Or use npx (no installation needed)
npx @marp-team/marp-cli
```

### Convert to PDF:
```bash
# Basic conversion
marp docs/RepoTwin-Presentation.md --pdf

# With custom theme
marp docs/RepoTwin-Presentation.md --pdf --theme dark

# Output to specific location
marp docs/RepoTwin-Presentation.md --pdf -o RepoTwin-Presentation.pdf
```

### Marp Features:
- ✅ Slide-based layout (each `---` creates a new slide)
- ✅ Dark theme support
- ✅ Professional presentation format
- ✅ Easy to customize

## Method 2: Using Pandoc (Recommended for Documents)

Pandoc is a universal document converter.

### Installation:
```bash
# Windows (using Chocolatey)
choco install pandoc

# macOS (using Homebrew)
brew install pandoc

# Or download from: https://pandoc.org/installing.html
```

### Convert to PDF:
```bash
# Basic conversion
pandoc docs/RepoTwin-Presentation.md -o RepoTwin-Presentation.pdf

# With custom styling
pandoc docs/RepoTwin-Presentation.md -o RepoTwin-Presentation.pdf \
  --pdf-engine=xelatex \
  -V geometry:margin=1in \
  -V fontsize=12pt

# With table of contents
pandoc docs/RepoTwin-Presentation.md -o RepoTwin-Presentation.pdf \
  --toc \
  --toc-depth=2
```

### Requirements:
- Requires LaTeX installation (MiKTeX on Windows, MacTeX on macOS)

## Method 3: Using reveal.js (Web-Based Presentation)

Create an interactive HTML presentation that can be printed to PDF.

### Installation:
```bash
# Install reveal-md
npm install -g reveal-md
```

### Convert:
```bash
# Start presentation server
reveal-md docs/RepoTwin-Presentation.md

# Export to PDF
reveal-md docs/RepoTwin-Presentation.md --print RepoTwin-Presentation.pdf
```

### Features:
- ✅ Interactive slides
- ✅ Animations and transitions
- ✅ Speaker notes support
- ✅ Can be hosted online

## Method 4: Using VS Code Extensions

If you're using VS Code:

### Markdown PDF Extension:
1. Install "Markdown PDF" extension
2. Open `RepoTwin-Presentation.md`
3. Press `Ctrl+Shift+P` (or `Cmd+Shift+P` on Mac)
4. Type "Markdown PDF: Export (pdf)"
5. Select output location

### Marp for VS Code:
1. Install "Marp for VS Code" extension
2. Open `RepoTwin-Presentation.md`
3. Click "Export Slide Deck" button
4. Choose PDF format

## Method 5: Using Online Tools

### Markdown to PDF Online Converters:
- **Dillinger.io**: https://dillinger.io/
  - Import markdown
  - Export as PDF
  
- **Markdown to PDF**: https://www.markdowntopdf.com/
  - Upload file
  - Download PDF

- **CloudConvert**: https://cloudconvert.com/md-to-pdf
  - Upload markdown
  - Convert to PDF

## Method 6: Using Google Slides

1. Copy content from `RepoTwin-Presentation.md`
2. Use a Markdown to Google Slides converter:
   - **md2googleslides**: https://github.com/googleworkspace/md2googleslides
3. Or manually create slides in Google Slides
4. Export as PDF from Google Slides

## Method 7: Using PowerPoint

1. Import markdown to PowerPoint using:
   - **Pandoc**: `pandoc docs/RepoTwin-Presentation.md -o presentation.pptx`
2. Or use PowerPoint's markdown import feature (if available)
3. Export as PDF from PowerPoint

## Recommended Workflow

For the **best presentation quality**, I recommend:

### Option A: Marp (For Slide Deck)
```bash
# Install Marp
npm install -g @marp-team/marp-cli

# Convert with dark theme
marp docs/RepoTwin-Presentation.md \
  --pdf \
  --theme dark \
  --allow-local-files \
  -o RepoTwin-Presentation.pdf
```

### Option B: Pandoc + Beamer (For Professional Slides)
```bash
# Convert to Beamer presentation
pandoc docs/RepoTwin-Presentation.md \
  -t beamer \
  -o RepoTwin-Presentation.pdf \
  --slide-level=2 \
  -V theme:metropolis \
  -V colortheme:default
```

## Customization Tips

### For Marp:
Add this to the top of the markdown file:
```yaml
---
marp: true
theme: default
class: invert
paginate: true
backgroundColor: #1a1a1a
color: #ffffff
---
```

### For Pandoc:
Add this to the top of the markdown file:
```yaml
---
title: RepoTwin by Bob
author: Team RepoTwin
date: IBM Bob Hackathon 2026
theme: metropolis
colortheme: default
---
```

## Troubleshooting

### Issue: "pandoc: command not found"
**Solution:** Install Pandoc from https://pandoc.org/installing.html

### Issue: "pdflatex not found"
**Solution:** Install LaTeX:
- Windows: MiKTeX (https://miktex.org/)
- macOS: MacTeX (https://www.tug.org/mactex/)
- Linux: `sudo apt-get install texlive-full`

### Issue: Images not showing
**Solution:** Use `--allow-local-files` flag with Marp or ensure images are in the same directory

### Issue: Tables not formatting correctly
**Solution:** Use Pandoc with `--pdf-engine=xelatex` for better table support

## Quick Start (Easiest Method)

If you want the fastest result:

1. **Install Marp CLI:**
   ```bash
   npm install -g @marp-team/marp-cli
   ```

2. **Convert:**
   ```bash
   marp docs/RepoTwin-Presentation.md --pdf
   ```

3. **Done!** Your PDF will be in the same directory.

## Need Help?

If you encounter issues:
1. Check that Node.js is installed: `node --version`
2. Check that npm is installed: `npm --version`
3. Try using npx instead: `npx @marp-team/marp-cli docs/RepoTwin-Presentation.md --pdf`
4. Use an online converter as a fallback

---

**Note:** The presentation markdown file is already formatted with slide breaks (`---`) and is ready to convert to PDF using any of these methods.