from tree_sitter_languages import get_parser

parser = get_parser("python")

def extract_ast(code: str):
    try:
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
