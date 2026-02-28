# command_dispatcher.py

class CommandDispatcher:
    def __init__(self, text_ctrl):
        self.text_ctrl = text_ctrl

    def execute(self, command: dict):
        action = command.get("action")

        if action == "clear_text":
            self.text_ctrl.SetValue("")

        elif action == "to_upper":
            text = self.text_ctrl.GetValue()
            self.text_ctrl.SetValue(text.upper())

        elif action == "to_lower":
            text = self.text_ctrl.GetValue()
            self.text_ctrl.SetValue(text.lower())

        elif action == "insert_text":
            content = command.get("content", "")
            self.text_ctrl.WriteText(content)

        else:
            print("Unknown command:", action)