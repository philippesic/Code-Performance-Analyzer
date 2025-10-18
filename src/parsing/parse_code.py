from tree_sitter import Language, Parser
import json

def parse_code(code, lang="python"):
    parser = Parser()
    parser.set_language(Language('build/my-languages.so', lang))
    tree = parser.parse(bytes(code, "utf8"))
    return tree.root_node.sexp()  # or a summarized form

def process_file(input_path, output_path):
    with open(input_path) as f:
        code = f.read()
    ast_summary = parse_code(code)
    json.dump({"code": code, "ast": ast_summary}, open(output_path, "w"))
