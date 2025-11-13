from tree_sitter import Parser, Language
import tree_sitter_python

# Initialize parser once at module level
_parser = None

def _get_parser():
    global _parser
    if _parser is None:
        _parser = Parser(Language(tree_sitter_python.language()))
    return _parser

def extract_ast(code: str):
    try:
        parser = _get_parser()
        tree = parser.parse(bytes(code, "utf8"))
        root = tree.root_node

        def walk(node):
            return {
                "type": node.type,
                "start": node.start_point,
                "end": node.end_point,
                "children": [walk(child) for child in node.children]
            }

        return walk(root)

    except Exception as e:
        return {"error": f"AST parse failed: {e}"}