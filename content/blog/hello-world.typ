#set document(title: "Hello World!", date: datetime(year: 2025, month: 11, day: 28))
// tags: meta, typst, web-dev
// abstract: My first blog post! I introduce this website and explain the technical details of how it's built using Typst, Pandoc, and a custom static site generator.

= Hello World!

This is my first blog post on my new website! I'm excited to share my thoughts, research, and projects here.

= Why This Site?

I wanted a clean, fast, and customizable platform to share my academic work, blog posts, and notes. I decided to build my own static site generator using Typst for content authoring and Python for the build system.

= How It Works

== Content Authoring

All content on this site is written in *Typst*, a modern markup language with excellent support for mathematics and typography. Typst makes it easy to write mathematical expressions like $e^(i pi) + 1 = 0$ and format academic content beautifully.

== Rendering Pipeline

The site uses **Typst's native HTML export** for all content:

```bash
typst compile --features html --format html
```

*Why Typst HTML?*
- Full support for Typst packages (like `@preview/commute` for diagrams)
- Responsive HTML output
- Preserves all Typst styling and features
- Native math rendering

However, Typst's HTML export sometimes demotes headings by one level (treating the document title as the main heading), so I wrote a post-processing step in Python to:
- Promote headers back to their original levels (for pages only)
- Generate table of contents from headers
- Add IDs to headers for navigation

== Interactive Content

I can embed interactive visualizations using a custom marker system. For example, `[INTERACTIVE:p5-sketch]` injects a p5.js sketch from the `interactive/` folder. [INTERACTIVE:p5-sketch] The build script performs regex replacement to inject the HTML/JavaScript code during the build process.

== Styling

The site uses a custom "typewriter" aesthetic with:
- Monospace fonts (Courier New)
- Cream/paper background
- Brown accents
- Markdown-style header prefixes (`#`, `##`, etc.)
- Dashed borders and vintage-style buttons

== Search and Tagging

The blog index includes:
- Real-time search (client-side JavaScript)
- Tag-based filtering
- Responsive tag buttons

All metadata (title, date, tags, abstract) is extracted from Typst comments using regex in the Python build script.

= What's Next?

I plan to write about:
- Representation Theory
- Typst tips and tricks
- Mathematical visualizations
- Research notes and preprints

Thanks for reading my first post! Feel free to explore the rest of the site.
