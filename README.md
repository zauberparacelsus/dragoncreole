
## DragonCreole

DragonCreole began life as a custom spinoff of the Creole markup, optimized for speed and HTML5 compliance.  It has some additional features that make it different from the official Creole 1.0 specification:

* Uses the sub-script, super-script, underlined text, and definition list additions
* Lettered lists and Roman Numeral lists are supported, as an alternative to numbered lists.
* Bullet, Numbered, Lettered, and Roman Numeral lists can all be embedded within one another.
* Cells in tables can span across multiple columns
* Automatic paragraphs can optionally be disabled
* Macros are explicitly supported, using the recommended markup

Currently, documentation is not yet ready, but getting started with DragonCreole is simple enough:

```
from dragoncreole import DragonCreole

parser = DragonCreole()
print( parser.render("**Hello World!**") )
```
