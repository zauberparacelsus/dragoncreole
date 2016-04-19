
## DragonCreole

DragonCreole began life as a custom spinoff of the Creole markup, optimized for speed and HTML5 compliance.  Written in Python, it was originally designed as a component for the bliki engine I use for running the site of my web comic, [Lord of Maelstrom](https://lordofmaelstrom.com).  It has some additional features that make it different from the official Creole 1.0 specification:

* Uses the sub-script, super-script, underlined text, and definition list additions
* Lettered lists and Roman Numeral lists are supported, as an alternative to numbered lists.
* Bullet, Numbered, Lettered, and Roman Numeral lists can all be embedded within one another.
* Cells in tables can span across multiple columns
* Automatic paragraphs can optionally be disabled
* Macros are explicitly supported, using the recommended markup

Currently, documentation is not yet ready and it is not yet available on PyPI, but getting started with DragonCreole is simple enough:

```python
from dragoncreole import DragonCreole

parser = DragonCreole()
print( parser.render("**Hello World!**") )
```

Alternatively, you can run dragoncreole.py directly and then open http://localhost:5000 in your browser to see a basic demo page.

You can find examples of the markup in the file test.txt, and test.html contains the rendered output.
