from enum import Enum
from typing import Union

class NodeType(Enum):
	OBJECT = 0
	ARRAY = 1
	BOOL = 2
	STRING = 3
	INT = 4
	FLOAT = 5
	TAGGED = 6

NodeValue = str|int|bool|float|list['Node']|dict['Node']

class Node():
	def __init__(self, nodeType: NodeType, nodeValue: NodeValue, parentNode: Union['Node', None], nodeTag: str=None) -> None:
		self.nodeType: NodeType = nodeType
		self.nodeValue: NodeValue = nodeValue
		self.nodeTag: str|None = None
		self.parentNode: Node|None = parentNode

	def __indent__(self, s: str):
		return '\t' + '\n\t'.join(s.splitlines())

	def __repr__(self) -> str:
		if self.nodeType == NodeType.ARRAY:
			return 'Node [\n' + ',\n'.join([ self.__indent__(str(x)) for x in self.nodeValue ]) + '\n]\n'

		if self.nodeType == NodeType.OBJECT:
			return 'Node {\n' + ',\n'.join([ self.__indent__(f'{k}: {str(v)}') for k,v in self.nodeValue.items() ]) + '\n}\n'

		if self.nodeType == NodeType.STRING:
			return 'Node<"'+self.nodeValue+'">'

		return 'Node<'+str(self.nodeValue)+'>'