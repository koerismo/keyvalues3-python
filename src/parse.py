from enum import Enum
from .node import Node, ValueNode, ArrayNode, ObjectNode, NodeType
from .tokenizer import RawToken, tokenize
import re

# This is a bit of a hack, since the tokenizer doesn't actually keep track of the line count.
def get_pos(text: str, ind: int):
	current_line = text.count('\n', 0, ind)
	current_char = text.rfind('\n', 0, ind)
	current_char = ind if current_char == -1 else ind - current_char
	return current_line, current_char

class State(Enum):
	NONE = 0 # Expect a key or closing bracket
	KEY = 1 # Expect a separator (=)
	SEP = 2 # Expect a value

	ARR_NONE = 3 # Expect an item or a closing bracket
	ARR_ITEM = 5 # Expect a comma or closing bracket

	ROOT = 6 # Unique state for the file start. Forces the first token to be an opening bracket.

RE_INT = re.compile('^-?\\d+$')
RE_FLOAT = re.compile('^-?\\d*\\.\\d+$')
RE_BOOLEAN = re.compile('^(true|false)$', re.IGNORECASE)
RE_TAGGED = re.compile('^\w+\\:\\".+\\"$')

def parse_value(value: str):
	if RE_BOOLEAN.match(value): return NodeType.BOOL,  bool(value.lower() == 'true')
	if RE_INT.match(value):     return NodeType.INT,   int(value)
	if RE_FLOAT.match(value):   return NodeType.FLOAT, float(value)
	return NodeType.STRING, value

def parse_to_node(parent: Node, value: str, quoted: bool=False):
	if quoted: return ValueNode(parent, NodeType.STRING, value)

	tag = None
	if RE_TAGGED.match(value):
		tag, _, value = value.partition(':')
		value = value[1:-1]
	type, value = parse_value(value)

	return ValueNode(parent, type, value, tag)

def parse(text: str):
	root = ObjectNode(None)
	node = root
	key = None
	state = State.ROOT


	def on_token(type: RawToken, value: str, ind: int):
		nonlocal node, key, state

		match state:

			# Root state. This only exists to give more insightful errors when the root brackets are not present.
			case State.ROOT:
				if type == RawToken.SHEBANG:
					return

				if type != RawToken.OPEN_OBJECT:
					raise ValueError('Expected opening bracket at start of file!')

				state = State.NONE
				return

			# Default state. Expects a key or a closing bracket.
			case State.NONE:
				if type == RawToken.QUOTED or type == RawToken.UNQUOTED:
					state = State.KEY
					key = value
					return

				if type == RawToken.CLOSE_OBJECT:
					state = State.NONE
					node = node.parent
					return

				current_line, current_char = get_pos(text, ind)
				raise ValueError(f'Expected key or closing bracket, but found {RawToken(type).name} at L{current_line}:{current_char}!')


			# Key received state. Expects an equals sign.
			case State.KEY:
				if type == RawToken.EQUALS:
					state = State.SEP
					return

				current_line, current_char = get_pos(text, ind)
				raise ValueError(f'Expected equals, but found {RawToken(type).name} at L{current_line}:{current_char}!')


			# Equals received state. Expects a value or opening bracket.
			case State.SEP:
				if type == RawToken.QUOTED:
					state = State.NONE
					node.children[key] = parse_to_node(node, value, True)
					return

				if type == RawToken.UNQUOTED:
					state = State.NONE
					node.children[key] = parse_to_node(node, value)
					return

				if type == RawToken.OPEN_OBJECT:
					state = State.NONE
					new_node = ObjectNode(node)
					node.children[key] = new_node
					node = new_node
					return

				if type == RawToken.OPEN_ARRAY:
					state = State.ARR_NONE
					new_node = new_node = ArrayNode(node)
					node.children[key] = new_node
					node = new_node
					return

				current_line, current_char = get_pos(text, ind)
				raise ValueError(f'Expected value or opening bracket, but found {RawToken(type).name} at L{current_line}:{current_char}!')


			# Array state. Expects an item or a closing bracket.
			case State.ARR_NONE:
				if type == RawToken.QUOTED:
					node.children.append(parse_to_node(node, value, True))
					state = State.ARR_ITEM
					return

				if type == RawToken.UNQUOTED:
					node.children.append(parse_to_node(node, value))
					state = State.ARR_ITEM
					return

				if type == RawToken.CLOSE_ARRAY:
					state = State.NONE
					node = node.parent
					return

				current_line, current_char = get_pos(text, ind)
				raise ValueError(f'Expected array item or closing bracket, but found {RawToken(type).name} at L{current_line}:{current_char}!')


			# Array post-item state. Expects a comma or a closing bracket.
			case State.ARR_ITEM:
				if type == RawToken.COMMA:
					state = State.ARR_NONE
					return

				if type == RawToken.CLOSE_ARRAY:
					state = State.NONE
					node = node.parent
					return

				current_line, current_char = get_pos(text, ind)
				raise ValueError(f'Expected comma or closing bracket, but found {RawToken(type).name} at L{current_line}:{current_char}!')


		current_line, current_char = get_pos(text, ind)
		raise ValueError(f'Encountered unexpected {RawToken(type).name} (state={State(state).name}) at L{current_line}:{current_char}. REPORT THIS ERROR!')


	tokenize(text, on_token)

	# This can be changed to node != root if the outer brackets are not desired.
	if node != None: raise ValueError('Encountered unexpected EOF inside non-root node!')
	return root

