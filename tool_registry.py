from tools.editor_tools import EditorTools

class ToolRegistry:
    def __init__(self):
        self.editor_tools = EditorTools()

        self.tools = {
            "insert_text": self.editor_tools.insert_text,
            "clear_text": self.editor_tools.clear_text,
            "to_upper": self.editor_tools.to_upper,
            "to_lower": self.editor_tools.to_lower,
        }

    def list_tools(self):
        return [
            {
                "name": name,
                "description": func.__doc__,
                "inputSchema": {
                    "type": "object",
                    "properties": {},
                }
            }
            for name, func in self.tools.items()
        ]

    def call_tool(self, name, arguments):
        if name not in self.tools:
            return {"error": "Tool not found"}
        return self.tools[name](**arguments)