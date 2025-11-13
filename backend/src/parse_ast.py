from tree_sitter import Language, Parser

Language.build_library(
  'build/my-languages.so',
  ['tree-sitter-python']
)

PY_LANGUAGE = Language('build/my-languages.so', 'python')

parser = Parser()
parser.set_language(PY_LANGUAGE)

def extract_ast(code):
    tree = parser.parse(bytes(code, "utf8"))
    return tree.root_node.sexp()
