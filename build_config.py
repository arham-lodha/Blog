# Build Configuration

# Compilation modes (choose one per content type):
# - False, False: Use Pandoc (fast, loses Typst styling and packages)
# - True, False: Use SVG (preserves styling, but page-like layout)
# - False, True: Use Typst native HTML (preserves styling, responsive, experimental)

USE_SVG_FOR_BLOG = False
USE_TYPST_HTML_FOR_BLOG = True  # Typst HTML for blog posts (package support + math)

USE_SVG_FOR_PAGES = False
USE_TYPST_HTML_FOR_PAGES = True  # Typst HTML for pages

# Base URL for deployment (e.g., "/Blog" for GitHub Pages, "" for local/root)
BASE_URL = "/Blog"
