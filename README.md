# Typst Blog - Static Site Generator

A custom static site generator for academic blogging, built with Typst and Python.

## Features

- ✍️ Write content in **Typst** with full package support
- 📚 Automatic **Table of Contents** generation
- 🔍 Client-side **search and tag filtering**
- 🎨 **Typewriter aesthetic** design
- 🎯 **Interactive visualizations** (p5.js, Three.js, etc.)
- 🧮 **Math rendering** with Typst's native engine
- 🎨 **Syntax highlighting** for code blocks

## Prerequisites

- Python 3.x
- [Typst CLI](https://github.com/typst/typst) (`brew install typst` on macOS)

## Quick Start

1. **Clone the repository:**
   ```bash
   git clone <your-repo-url>
   cd Blog
   ```

2. **Build the site:**
   ```bash
   python3 build.py
   ```

3. **Preview locally:**
   ```bash
   python3 -m http.server --directory output 8080
   ```
   Open http://localhost:8080

## Project Structure

```
.
├── build.py              # Main build script
├── build_config.py       # Build configuration
├── content/
│   ├── blog/            # Blog posts (.typ files)
│   └── pages/           # Static pages
├── templates/           # HTML templates
├── static/              # CSS, JS, assets
├── scripts/             # Build scripts
├── interactive/         # Interactive components
└── output/              # Generated site (gitignored)
```

## Creating Content

### New Blog Post

Create a `.typ` file in `content/blog/`:

```typst
#set document(title: "My Post", date: datetime(year: 2025, month: 12, day: 1))
// tags: math, topology
// abstract: A brief summary of the post.

= My Post Title

Your content here...
```

### Interactive Components

Create HTML files in `interactive/` and embed with:

```typst
[INTERACTIVE:component-name]
```

Subdirectories are supported: `[INTERACTIVE:folder/component-name]`

## Deployment

The site is automatically deployed to GitHub Pages via GitHub Actions on every push to `main`.

### Manual Deployment

The `output/` directory contains the complete static site ready for deployment to:
- GitHub Pages
- Netlify
- Vercel
- Any static host

## Configuration

Edit `build_config.py` to change rendering modes:
- `USE_TYPST_HTML_FOR_BLOG`: Enable Typst HTML for blog posts
- `USE_TYPST_HTML_FOR_PAGES`: Enable Typst HTML for pages

## License

MIT
