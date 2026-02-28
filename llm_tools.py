# llm_tools.py

TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "insert_text",
            "description": "Insert text into the editor",
            "parameters": {
                "type": "object",
                "properties": {
                    "content": {
                        "type": "string",
                        "description": "Text to insert"
                    }
                },
                "required": ["content"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "clear_text",
            "description": "Clear entire editor content",
            "parameters": {
                "type": "object",
                "properties": {}
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "to_upper",
            "description": "Convert entire text to uppercase",
            "parameters": {
                "type": "object",
                "properties": {}
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "to_lower",
            "description": "Convert entire text to lowercase",
            "parameters": {
                "type": "object",
                "properties": {}
            }
        }
    }
]