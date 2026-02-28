class EditorTools:
    def __init__(self):
        self.text_ctrl = None

    def bind_editor(self, text_ctrl):
        self.text_ctrl = text_ctrl

    def insert_text(self, content: str):
        """Insert text into editor"""
        self.text_ctrl.WriteText(content)
        return {"status": "ok"}

    def clear_text(self):
        """Clear entire editor content"""
        self.text_ctrl.SetValue("")
        return {"status": "ok"}

    def to_upper(self):
        """Convert entire text to uppercase"""
        text = self.text_ctrl.GetValue()
        self.text_ctrl.SetValue(text.upper())
        return {"status": "ok"}

    def to_lower(self):
        """Convert entire text to lowercase"""
        text = self.text_ctrl.GetValue()
        self.text_ctrl.SetValue(text.lower())
        return {"status": "ok"}