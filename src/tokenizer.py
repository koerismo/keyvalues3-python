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
RE_PLAIN = re.compile('[\\da-z\\-\\\\]', re.IGNORECASE)
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

		if RE_WHITESPACE.match(char): continue

		# Your average control characters
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
		if text.startswith('"""', i):
			i += 3
			start = i

			while True:
				if i+3 >= len(text): raise ValueError(f'Encountered unexpected EOF while waiting for end of multiline string starting at {start}!')
				if text.startswith('"""', i): break
				if text[i] == '\\': i += 1
				i += 1

			i += 3
			on_token(RawToken.QUOTED, text[start:i-3], start)
			continue

		# Handle single-quoted strings.
		if char == '"':
			i += 1
			start = i

			while True:
				if i >= len(text): raise ValueError(f'Encountered unexpected EOF while waiting for end of string starting at {start}!')
				if text[i] == '\n': raise ValueError(f'Encountered unexpected newline while waiting for end of string starting at {start}!')
				if text[i] == '"': break
				if text[i] == '\\': i += 1
				i += 1

			on_token(RawToken.QUOTED, text[start:i], i)
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
				if i >= len(text) or RE_TERMINATE.match(text, i): break
				if text[i] == '\\': i += 1
				i += 1

			on_token(RawToken.UNQUOTED, text[start:i], i)
			i -= 1
			continue

		# If we reach this, something has gone very wrong.
		raise ValueError(f'Unexpected character {char} at position {i}!')
