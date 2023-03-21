from enum import Enum
from typing import Union

class NodeType(Enum):
	OBJECT = 0
	ARRAY = 1
	BOOL = 2
	STRING = 3
	INT = 4
	FLOAT = 5

NodeValue = str|int|bool|float|list['Node']|dict['Node']
NodeParent = Union['Node', None]

class Node():
	def __init__(self, parent: NodeParent, type: NodeType):
		self.type: NodeType = type
		self.parent: Node|None = parent

	def __indent__(self, s: str):
		return '\t' + '\n\t'.join(s.splitlines())

	def __indent_il__(self, s: str):
		return '\n\t'.join(s.splitlines())

class ValueNode(Node):
	def __init__(self, parent: NodeParent, type: NodeType, value: NodeValue, tag: str|None=None):
		super().__init__(parent, type)
		self.value = value
		self.tag = tag

	def __repr__(self):
		out = '<' + (self.tag+':' if self.tag else '') + NodeType(self.type).name + '> '
		if self.type == NodeType.STRING: return out+'"'+self.__indent_il__(self.value)+'"'
		return out+str(self.value)

class ObjectNode(Node):
	def __init__(self, parent: NodeParent, children: dict[Node]=None):
		super().__init__(parent, NodeType.OBJECT)
		self.children: dict[Node] = children or {}

	def __repr__(self):
		return '{\n' + ',\n'.join([ self.__indent__(f'{k} = {str(v)}') for k,v in self.children.items() ]) + '\n}\n'

class ArrayNode(Node):
	def __init__(self, parent: NodeParent, children: list[Node]=None):
		super().__init__(parent, NodeType.ARRAY)
		self.children: list[Node] = children or []

	def __repr__(self):
		return '[\n' + ',\n'.join([ self.__indent__(str(x)) for x in self.children ]) + '\n]\n'