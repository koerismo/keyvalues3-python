# Python KeyValues3 Parser
A simple parser for Valve's KeyValues3 data format.

### Progress tracker
- [x] Base parser
- [x] Shebang statements
- [x] Tagged values
- [ ] Allow objects within lists
- [ ] Analyze performance, optimize code
- [ ] Code cleanup
- [ ] Binary format?

### Usage
```py
from src import parse

tree = parse('''
<!-- Shebangs are ignored -->
{
	"key1" = "value"
	key2 = value
	key3 = 123

	key4 = [
		a, b, c,
		1, 2, 3,
	] // Comments are ignored

	key5 = """
		multiline
		  strings
		    work!
	""" /*
		Multiline
		  Comments
		    Too */
}
''')
```