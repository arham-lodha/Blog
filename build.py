import os
import shutil
import subprocess
import re
from datetime import datetime
from pathlib import Path

# Import configuration
try:
    from build_config import USE_SVG_FOR_BLOG, USE_SVG_FOR_PAGES, USE_TYPST_HTML_FOR_BLOG, USE_TYPST_HTML_FOR_PAGES
except ImportError:
    # Defaults if config file doesn't exist
    USE_SVG_FOR_BLOG = False
    USE_SVG_FOR_PAGES = False
    USE_TYPST_HTML_FOR_BLOG = False
    USE_TYPST_HTML_FOR_PAGES = False

# Configuration
CONTENT_DIR = Path("content")
BLOG_DIR = CONTENT_DIR / "blog"
PAGES_DIR = CONTENT_DIR / "pages"
TEMPLATES_DIR = Path("templates")
STATIC_DIR = Path("static")
OUTPUT_DIR = Path("output")

def clean_output():
    if OUTPUT_DIR.exists():
        shutil.rmtree(OUTPUT_DIR)
    OUTPUT_DIR.mkdir()

def copy_static():
    if STATIC_DIR.exists():
        shutil.copytree(STATIC_DIR, OUTPUT_DIR / "static")

def compile_typst(typ_file, use_svg=False, use_typst_html=False, skip_toc=False):
    """Compiles a Typst file to HTML (via Pandoc, Typst HTML, or SVG)."""
    
    if use_typst_html:
        # Use Typst's native HTML export (experimental)
        html_file = typ_file.with_suffix(".html")
        try:
            subprocess.run(
                ["typst", "compile", "--features", "html", "--format", "html", str(typ_file), str(html_file)],
                check=True,
                capture_output=True
            )
            
            with open(html_file, "r", encoding="utf-8") as f:
                html_content = f.read()
            
            # Clean up
            html_file.unlink()
            
            # Extract body content only
            body_match = re.search(r'<body.*?>(.*?)</body>', html_content, re.DOTALL)
            if body_match:
                html = body_match.group(1)
            else:
                html = html_content
            
            # Add IDs to headers for TOC
            html = add_header_ids(html)
            
            # Generate and prepend TOC (unless skipped)
            if not skip_toc:
                toc_html = generate_toc(html, max_depth=3)
                if toc_html:
                    html = toc_html + html
            
            return html
            
        except subprocess.CalledProcessError as e:
            print(f"Error compiling {typ_file} to HTML: {e.stderr.decode()}")
            return None
    
    elif use_svg:
        # Compile to SVG using typst
        svg_file = typ_file.with_suffix(".svg")
        try:
            subprocess.run(
                ["typst", "compile", "--format", "svg", str(typ_file), str(svg_file)],
                check=True,
                capture_output=True
            )
            
            with open(svg_file, "r", encoding="utf-8") as f:
                svg_content = f.read()
            
            # Clean up
            svg_file.unlink()
            
            # Wrap SVG in a container div
            return f'<div class="typst-svg-container">{svg_content}</div>'
            
        except subprocess.CalledProcessError as e:
            print(f"Error compiling {typ_file} to SVG: {e.stderr.decode()}")
            return None
    else:
        # Use Pandoc for HTML conversion
        try:
            cmd = [
                "pandoc", 
                "-f", "typst", 
                "-t", "html", 
                "--mathjax", 
                "--toc", 
                "--toc-depth=3", 
                "--standalone", 
                "--template=templates/pandoc_content.html",
                "--lua-filter=scripts/add_ids.lua",
                str(typ_file)
            ]
            result = subprocess.run(
                cmd,
                check=True,
                capture_output=True
            )
            html = result.stdout.decode("utf-8")
            
            # Post-process: wrap "Last updated" text in a styled span
            html = re.sub(
                r'\\(Last updated: ([^)]+)\\)',
                r'<span class="cv-updated">Last updated: \\1</span>',
                html
            )
            
            # Protect [INTERACTIVE:...] inside code blocks from replacement
            def protect_interactive_in_code(match):
                opening = match.group(1)
                content = match.group(2)
                closing = match.group(3)
                # Replace [INTERACTIVE:...] with HTML entities
                protected = re.sub(r'\[INTERACTIVE:([a-zA-Z0-9_-]+)\]', r'&#91;INTERACTIVE:\1&#93;', content)
                return opening + protected + closing
            
            html = re.sub(r'(<code>)(.*?)(</code>)', protect_interactive_in_code, html, flags=re.DOTALL)
            html = re.sub(r'(<pre[^>]*>)(.*?)(</pre>)', protect_interactive_in_code, html, flags=re.DOTALL)
            
            # Post-process: inject interactive content from files
            # Pattern: [INTERACTIVE:path/to/filename] where path is relative to interactive/
            def load_interactive(match):
                filepath = match.group(1)
                # Support subdirectories: interactive/folder/component
                interactive_file = Path("interactive") / f"{filepath}.html"
                
                if interactive_file.exists():
                    with open(interactive_file, "r", encoding="utf-8") as f:
                        content = f.read()
                    return f'<div class="interactive-center">{content}</div>'
                else:
                    print(f"Warning: Interactive file not found: {interactive_file}")
                    return f"<!-- Interactive component '{filepath}' not found -->"
            
            html = re.sub(
                r'\[INTERACTIVE:([a-zA-Z0-9_/-]+)\]',
                load_interactive,
                html
            )
            
            # Legacy support for old marker
            html = re.sub(
                r'\[INTERACTIVE_P5_SKETCH\]',
                lambda m: load_interactive(re.match(r'.*', 'p5-sketch')),
                html
            )
            
            return html
        except subprocess.CalledProcessError as e:
            print(f"Error compiling {typ_file}: {e.stderr.decode()}")
            return None


def add_header_ids(html):
    """Add IDs to headers that don't have them (for TOC linking)."""
    def add_id(match):
        tag = match.group(1)
        attrs = match.group(2)
        content = match.group(3)
        close_tag = match.group(4)
        
        # Check if already has an id
        if 'id=' in attrs:
            return match.group(0)
        
        # Generate slugified ID from content
        # Remove HTML tags from content for slug
        text_content = re.sub(r'<[^>]+>', '', content)
        slug = text_content.lower().strip()
        slug = re.sub(r'\s+', '-', slug)
        slug = re.sub(r'[^a-z0-9-]', '', slug)
        
        # Add id attribute with proper spacing
        if attrs.strip():
            new_attrs = f'{attrs} id="{slug}"'
        else:
            new_attrs = f' id="{slug}"'
        return f'<{tag}{new_attrs}>{content}</{close_tag}>'
    
    # Match h1-h6 tags
    html = re.sub(r'<(h[1-6])([^>]*)>(.*?)</(\1)>', add_id, html, flags=re.DOTALL)
    return html

def generate_toc(html, max_depth=3):
    """Generate table of contents from headers in HTML."""
    # Find all headers with IDs
    header_pattern = r'<(h[1-6])[^>]*id=["\']([^"\']+)["\'][^>]*>(.*?)</\1>'
    headers = re.findall(header_pattern, html, re.DOTALL)
    
    if not headers:
        return ""
    
    toc_items = []
    for tag, id_attr, content in headers:
        level = int(tag[1])  # Extract number from h1, h2, etc.
        if level > max_depth:
            continue
        
        # Clean HTML from content
        text = re.sub(r'<[^>]+>', '', content)
        toc_items.append((level, id_attr, text))
    
    if not toc_items:
        return ""
    
    # Build nested HTML structure
    toc_html = '<nav id="TOC" role="doc-toc">\n<ul>\n'
    current_level = toc_items[0][0]
    
    for level, id_attr, text in toc_items:
        # Handle level changes
        while level > current_level:
            toc_html += '<ul>\n'
            current_level += 1
        while level < current_level:
            toc_html += '</ul>\n</li>\n'
            current_level -= 1
        
        # Close previous item if at same level
        if level == current_level and toc_items.index((level, id_attr, text)) > 0:
            toc_html += '</li>\n'
        
        toc_html += f'<li><a href="#{id_attr}" id="toc-{id_attr}">{text}</a>'
    
    # Close remaining tags
    while current_level > toc_items[0][0]:
        toc_html += '</ul>\n</li>\n'
        current_level -= 1
    
    toc_html += '</li>\n</ul>\n</nav>\n'
    return toc_html

def fix_paths(html):
    """
    Prepend BASE_URL to all absolute paths starting with /.
    Ignores paths that already start with http, https, or relative paths.
    """
    if not BASE_URL:
        return html
        
    # Regex to match href="/...", src="/...", action="/..."
    # We only match paths starting with / that are NOT // (protocol relative)
    pattern = r'(href|src|action)=["\']/(?!/)([^"\']*)["\']'
    
    def replace_path(match):
        attr = match.group(1)
        path = match.group(2)
        return f'{attr}="{BASE_URL}/{path}"'
    
    return re.sub(pattern, replace_path, html)

def parse_metadata(typ_content):
    """Extracts title, date, tags, and abstract from Typst content."""
    title_match = re.search(r'#set document\(.*?title:\s*"(.*?)".*?\)', typ_content, re.DOTALL)
    date_match = re.search(r'date:\s*datetime\(.*?year:\s*(\d+).*?month:\s*(\d+).*?day:\s*(\d+).*?\)', typ_content, re.DOTALL)
    
    # Extract tags from a comment like: // tags: topology, homotopy, math
    tags_match = re.search(r'//\s*tags:\s*(.+)', typ_content)
    
    # Extract abstract from a comment like: // abstract: This post explores...
    abstract_match = re.search(r'//\s*abstract:\s*(.+)', typ_content)
    
    title = title_match.group(1) if title_match else "Untitled"
    
    # Parse date properly and format nicely
    if date_match:
        year, month, day = date_match.groups()
        # Create a nice date format: "Nov 28, 2025"
        from datetime import datetime
        date_obj = datetime(int(year), int(month), int(day))
        date = date_obj.strftime("%b %d, %Y")
        date_iso = f"{year}-{month.zfill(2)}-{day.zfill(2)}"  # For sorting
    else:
        date = "Jan 01, 2025"
        date_iso = "2025-01-01"
    
    # Parse tags
    tags = []
    if tags_match:
        tags = [tag.strip() for tag in tags_match.group(1).split(',')]
    
    # Parse abstract
    abstract = abstract_match.group(1).strip() if abstract_match else None
    
    return {"title": title, "date": date, "date_iso": date_iso, "tags": tags, "abstract": abstract}

def render_template(template_name, context):
    """Simple template rendering (replacing {{ key }})."""
    template_path = TEMPLATES_DIR / template_name
    with open(template_path, "r", encoding="utf-8") as f:
        template = f.read()
    
    # Handle inheritance (very basic)
    if "{% extends" in template:
        base_match = re.search(r'{% extends "(.*?)" %}', template)
        if base_match:
            base_name = base_match.group(1)
            with open(TEMPLATES_DIR / base_name, "r", encoding="utf-8") as f:
                base = f.read()
            
            # Extract blocks
            blocks = {}
            for match in re.finditer(r'{% block (.*?) %}(.*?){% endblock %}', template, re.DOTALL):
                blocks[match.group(1)] = match.group(2)
            
            # Replace blocks in base
            for block_name, block_content in blocks.items():
                base = re.sub(r'{% block ' + block_name + r' %}.*?{% endblock %}', block_content, base, flags=re.DOTALL)
            
            template = base

    # Handle basic if blocks: {% if key %}...{% endif %}
    # We support simple boolean checks on context keys
    while True:
        if_match = re.search(r'{% if (.*?) %}(.*?){% endif %}', template, re.DOTALL)
        if not if_match:
            break
            
        condition_key = if_match.group(1).strip()
        block_content = if_match.group(2)
        
        # Check if key exists and is truthy in context
        if context.get(condition_key):
            template = template.replace(if_match.group(0), block_content)
        else:
            template = template.replace(if_match.group(0), "")

    # Replace variables
    for key, value in context.items():
        template = template.replace(f"{{{{ {key} }}}}", str(value))
        
    return template

def build_blog():
    posts = []
    blog_output_dir = OUTPUT_DIR / "blog"
    blog_output_dir.mkdir(exist_ok=True)

    for typ_file in BLOG_DIR.glob("*.typ"):
        print(f"Processing {typ_file}...")
        
        # Read raw content for metadata extraction
        with open(typ_file, "r", encoding="utf-8") as f:
            raw_content = f.read()
            
        metadata = parse_metadata(raw_content)
        
        # Compile to HTML or SVG
        html_content = compile_typst(typ_file, use_svg=USE_SVG_FOR_BLOG, use_typst_html=USE_TYPST_HTML_FOR_BLOG)
        if not html_content:
            continue
            
        # Extract body from full HTML if Typst outputs full page
        # Typst HTML export is experimental, it might output a full <html> document.
        # We might need to extract just the body content.
        # For now, let's assume we dump it as is or extract <body> content.
        
        body_match = re.search(r'<body.*?>(.*?)</body>', html_content, re.DOTALL)
        if body_match:
            html_content = body_match.group(1)
            
        slug = typ_file.stem
        post_dir = blog_output_dir / slug
        post_dir.mkdir(exist_ok=True)
        
        context = {
            "title": metadata["title"],
            "date": metadata["date"],
            "content": html_content,
            "show_title": True
        }
        
        final_html = render_template("post.html", context)
        
        # Apply path fix for GitHub Pages
        final_html = fix_paths(final_html)
        
        with open(post_dir / "index.html", "w", encoding="utf-8") as f:
            f.write(final_html)
            
        posts.append({
            "title": metadata["title"], 
            "url": f"/blog/{slug}/", 
            "date": metadata["date"],
            "date_iso": metadata.get("date_iso", metadata["date"]),
            "tags": metadata.get("tags", []),
            "abstract": metadata.get("abstract"),
            "slug": slug
        })
        
    return posts

def build_index(posts):
    # Build Home Page from home.typ
    home_typ = PAGES_DIR / "home.typ"
    if home_typ.exists():
        html_content = compile_typst(home_typ, use_svg=USE_SVG_FOR_PAGES, use_typst_html=USE_TYPST_HTML_FOR_PAGES, skip_toc=True)
        
        # Promote headings for home page: h2 -> h1, h3 -> h2, etc.
        # Typst HTML export seems to demote the top-level heading to h2 by default
        def promote_heading(match):
            tag_open = match.group(1) # "" or "/"
            level = int(match.group(2))
            return f"<{tag_open}h{max(level - 1, 1)}"
            
        html_content = re.sub(r'<(/?)h([2-6])', promote_heading, html_content)
        
        context = {
            "title": "", # No title for home
            "date": "",
            "content": html_content,
            "show_title": False # Home page has its own heading in Typst
        }
        # Use post template for consistency or base? Post has the article wrapper.
        html = render_template("post.html", context)
        
        # Apply path fix for GitHub Pages
        html = fix_paths(html)
        
        with open(OUTPUT_DIR / "index.html", "w") as f:
            f.write(html)
    else:
        # Fallback
        context = {
            "title": "Home",
            "content": "<h1>Welcome</h1>"
        }
        html = render_template("base.html", context)
        with open(OUTPUT_DIR / "index.html", "w") as f:
            f.write(html)

    # Build Blog Index with search and tags
    post_list = "<ul class='post-list'>"
    all_tags = set()
    
    for post in posts:
        tags_html = ""
        if post.get("tags"):
            all_tags.update(post["tags"])
            tags_html = " ".join([f"<span class='tag'>{tag}</span>" for tag in post["tags"]])
        
        abstract_html = ""
        if post.get("abstract"):
            abstract_html = f"<p class='post-abstract'>{post['abstract']}</p>"
        
        post_list += f"<li class='post-item' data-tags='{','.join(post.get('tags', []))}'>"
        post_list += f"<div class='post-header'><a href='{post['url']}'>{post['title']}</a><span class='post-date'>{post['date']}</span></div>"
        post_list += abstract_html
        if tags_html:
            post_list += f"<div class='post-tags'>{tags_html}</div>"
        post_list += "</li>"
    post_list += "</ul>"
    
    # Create tag filter buttons
    tag_buttons = "<div class='tag-filter'><button class='tag-btn active' data-tag='all'>All</button>"
    for tag in sorted(all_tags):
        tag_buttons += f"<button class='tag-btn' data-tag='{tag}'>{tag}</button>"
    tag_buttons += "</div>"
    
    # Create search box
    search_box = """<div class='search-box'>
        <input type='text' id='search-input' placeholder='Search posts...' />
    </div>"""
    
    blog_content = f"""<h1>Blog</h1>
    {search_box}
    {tag_buttons}
    {post_list}
    <script src='/static/js/blog-search.js'></script>"""
    
    with open(TEMPLATES_DIR / "base.html", "r") as f:
        base = f.read()

    blog_index_html = base.replace("{% block content %}{% endblock %}", blog_content)
    blog_index_html = blog_index_html.replace("{% block title %}My Math Website{% endblock %}", "Blog")
    
    # Apply path fix for GitHub Pages
    blog_index_html = fix_paths(blog_index_html)
    
    with open(OUTPUT_DIR / "blog" / "index.html", "w") as f:
        f.write(blog_index_html)
    
    # Create search index JSON
    search_index = []
    for post in posts:
        search_index.append({
            "title": post["title"],
            "url": post["url"],
            "date": post["date"],
            "tags": post.get("tags", []),
            "slug": post["slug"]
        })
    
    import json
    with open(OUTPUT_DIR / "static" / "search-index.json", "w") as f:
        json.dump(search_index, f)

def build_pages():
    PAGES_DIR.mkdir(exist_ok=True)
    for typ_file in PAGES_DIR.glob("*.typ"):
        with open(typ_file, "r", encoding="utf-8") as f:
            raw_content = f.read()
            
        metadata = parse_metadata(raw_content)
        html_content = compile_typst(typ_file)
        
        if not html_content:
            continue
            
        body_match = re.search(r'<body.*?>(.*?)</body>', html_content, re.DOTALL)
        if body_match:
            html_content = body_match.group(1)
            
        slug = typ_file.stem
        # Pages go to root or their own folder? Let's do root/slug/index.html
        page_dir = OUTPUT_DIR / slug
        page_dir.mkdir(exist_ok=True)
        
        context = {
            "title": metadata["title"],
            "date": metadata["date"],
            "content": html_content
        }
        
        # Use a generic page template or post template? Let's use post.html for now as it's generic enough
        final_html = render_template("post.html", context)
        
        with open(page_dir / "index.html", "w", encoding="utf-8") as f:
            f.write(final_html)

def main():
    print("Building site...")
    clean_output()
    copy_static()
    posts = build_blog()
    # build_pages() # We are handling home manually and don't need other pages for now
    build_index(posts)
    print("Build complete.")

if __name__ == "__main__":
    main()
