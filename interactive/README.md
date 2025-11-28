# Interactive Components

This folder contains reusable interactive HTML/JavaScript components that can be embedded in blog posts.

## Usage

In your Typst blog post, use:

```typst
[INTERACTIVE:filename]
```

Where `filename` is the name of the `.html` file in this directory (without the extension).

## Examples

- `[INTERACTIVE:p5-sketch]` - Embeds `interactive/p5-sketch.html`
- `[INTERACTIVE:three-cube]` - Embeds `interactive/three-cube.html`

## Creating New Components

1. Create a new `.html` file in this directory (e.g., `my-viz.html`)
2. Write your HTML/JavaScript code
3. Reference it in your Typst file: `[INTERACTIVE:my-viz]`

## Tips

- Use unique IDs for your DOM elements to avoid conflicts
- Include CDN links for libraries (p5.js, Three.js, D3.js, etc.)
- Keep components self-contained
- Test locally before deploying
