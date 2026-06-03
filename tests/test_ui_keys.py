import ast
import unittest
from pathlib import Path


class StreamlitButtonKeyTest(unittest.TestCase):
    def test_all_streamlit_buttons_have_explicit_keys(self):
        tree = ast.parse(Path("app.py").read_text(encoding="utf-8"))
        missing = []
        static_keys = []

        for node in ast.walk(tree):
            if not isinstance(node, ast.Call):
                continue
            if not isinstance(node.func, ast.Attribute):
                continue
            if node.func.attr != "button":
                continue
            if not isinstance(node.func.value, ast.Name) or node.func.value.id != "st":
                continue

            has_key = any(keyword.arg == "key" for keyword in node.keywords)
            if not has_key:
                missing.append(node.lineno)
                continue

            key_node = next(keyword.value for keyword in node.keywords if keyword.arg == "key")
            if isinstance(key_node, ast.Constant) and isinstance(key_node.value, str):
                static_keys.append((key_node.value, node.lineno))

        duplicate_keys = {
            key: [line for value, line in static_keys if value == key]
            for key, _ in static_keys
            if sum(1 for value, _line in static_keys if value == key) > 1
        }

        self.assertEqual(missing, [], f"st.button without key at lines: {missing}")
        self.assertEqual(duplicate_keys, {}, f"Duplicate static button keys: {duplicate_keys}")


if __name__ == "__main__":
    unittest.main()
