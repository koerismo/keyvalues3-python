from src import parse


tree = parse('''
<!-- kv3 encoding:text:version{e21c7f3c-8a33-41c5-9977-a76d3a32aa0d} format:generic:version{7412167c-06e9-4698-aff2-e63eb59037e7} -->
{
	boolValue = false
	intValue = 128
	doubleValue = 64.000000
	stringValue = "hello world"
	stringThatIsAResourceReference = resource:"particles/items3_fx/star_emblem.vpcf"
	multiLineStringValue = """
First line of a multi-line string literal.
Second line of a multi-line string literal.
"""
	arrayValue =
	[
		1,
		2,
	]
	objectValue =
	{
		n = 5
		s = "foo"
	}
	// single line comment
	/* multi
	line
	comment */
}
''')

print(tree)
