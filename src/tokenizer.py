from enum import Enum
from typing import Callable
import re

class RawToken(Enum):
	OPEN_OBJECT = 0
	CLOSE_OBJECT = 1
	OPEN_ARRAY = 2
	CLOSE_ARRAY = 3
	UNQUOTED = 4
	QUOTED = 5
	COMMA = 6
	EQUALS = 7
	SHEBANG = 8

RE_WHITESPACE = re.compile('[\\s\\t\\n\\r]')
RE_QUOTE = re.compile('(?<!\\\\)"')
RE_QUOTE_TRIPLE = re.compile('(?<!\\\\)"""')
RE_PLAIN = re.compile('[\\da-z]', re.IGNORECASE)
RE_TERMINATE = re.compile('[\\s\\t\\n\\r\\{\\}\\[\\],]')
RE_SHEBANG_END = re.compile('(?<!\\\\)\\-\\-\\>')
RE_COMMENT_END = re.compile('(?<!\\\\)\\*/')

def tokenize(text: str, on_token: Callable):
	# These four lines are the equivalent of any other language's
	# for ( let i=0; i<text.length; i++ ) { ...
	i = -1
	while i+1 < len(text):
		i += 1
		char = text[i]

		escaped = (i != 0 and text[i-1] == '\\')
		if RE_WHITESPACE.match(char): continue

		# Your average control characters
		if not escaped:
			match char:
				case '=':
					on_token(RawToken.EQUALS, None, i)
					continue
				case '{':
					on_token(RawToken.OPEN_OBJECT, None, i)
					continue
				case '}':
					on_token(RawToken.CLOSE_OBJECT, None, i)
					continue
				case '[':
					on_token(RawToken.OPEN_ARRAY, None, i)
					continue
				case ']':
					on_token(RawToken.CLOSE_ARRAY, None, i)
					continue
				case ',':
					on_token(RawToken.COMMA, None, i)
					continue

		# Handle single-line comments
		if text.startswith('//', i):
			next_newline = text.find('\n', i+2)
			if next_newline == -1: break
			i = next_newline+1
			continue

		# Handle multi-line comments
		if text.startswith('/*', i):
			end: re.Match = RE_COMMENT_END.search(text, i+2)
			if end == None: break
			i = end.end()
			continue

		# Handle triple-quoted strings.
		if text.startswith('\"\"\"', i):
			start = i
			end = RE_QUOTE_TRIPLE.search(text, i+3)
			if end == None: raise ValueError(f'Could not resolve multiline quote starting at {start}!')
			i = end.end()-1
			on_token(RawToken.QUOTED, text[start+3:i-2], i)
			continue

		# Handle single-quoted strings.
		if char == '"':
			start = i
			end = RE_QUOTE.search(text, i+1)
			if end == None: raise ValueError(f'Could not resolve quote starting at {start}!')
			i = end.start()

			next_newline = text.find('\n', start)
			if next_newline != -1 and next_newline < i: raise ValueError(f'Unexpected newline at {next_newline}! Unclosed string starts at {start}.')
			on_token(RawToken.QUOTED, text[start+1:i], i)
			continue

		# Handle shebang statement.
		if text.startswith('<!--', i):
			start = i
			end = RE_SHEBANG_END.search(text, i+3)
			if end == None: raise ValueError(f'Could not resolve shebang starting at {start}!')
			i = end.end()-1
			on_token(RawToken.SHEBANG, text[start+3:i-2], i)
			continue

		# Handle non-quoted strings.
		if RE_PLAIN.match(char):
			start = i
			while True:
				i += 1
				if i >= len(text) or (RE_TERMINATE.match(text, i) and text[i-1] != '\\'): break
			on_token(RawToken.UNQUOTED, text[start:i], i)
			i -= 1
			continue

		# If we reach this, something has gone very wrong.
		raise ValueError(f'Unexpected character {char} at position {i}!')
