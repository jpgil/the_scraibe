  
  
  
def to_html(content):  
    from markdown_it import MarkdownIt
    md = MarkdownIt("gfm-like").enable('table')
    rendered = md.render(content)
    return rendered
