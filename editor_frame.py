import wx
import threading
from tool_registry import ToolRegistry
from llm_client import LLMClient


class EditorFrame(wx.Frame):
    def __init__(self):
        super().__init__(None, title="MCP Groq Editor", size=(900, 550))

        panel = wx.Panel(self)

        # 📄 메인 에디터
        self.text_ctrl = wx.TextCtrl(
            panel,
            style=wx.TE_MULTILINE | wx.TE_RICH2
        )

        # 💬 콘솔형 대화창
        self.console = wx.TextCtrl(
            panel,
            style=wx.TE_MULTILINE | wx.TE_PROCESS_ENTER
        )

        self.console.Bind(wx.EVT_KEY_DOWN, self.on_console_key)

        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self.text_ctrl, 3, wx.EXPAND | wx.ALL, 5)
        sizer.Add(self.console, 1, wx.EXPAND | wx.ALL, 5)
        panel.SetSizer(sizer)

        # Tool registry
        self.registry = ToolRegistry()
        self.registry.editor_tools.bind_editor(self.text_ctrl)

        # LLM
        self.llm = LLMClient()

        # 콘솔 초기화
        self.reset_console()

    # -----------------------------
    # 콘솔 초기화
    # -----------------------------
    def reset_console(self):
        self.console.SetValue(">>> ")
        self.console.SetInsertionPointEnd()

    # -----------------------------
    # 키 이벤트 처리
    # -----------------------------
    def on_console_key(self, event):
        key = event.GetKeyCode()

        if key == wx.WXK_RETURN:
            if event.ShiftDown():
                # Shift+Enter → 줄바꿈
                self.console.WriteText("\n")
            else:
                # Enter → 실행
                text = self.console.GetValue()

                if text.startswith(">>> "):
                    user_input = text[4:].strip()
                else:
                    user_input = text.strip()

                if user_input:
                    self.run_llm(user_input)

                self.reset_console()

        else:
            event.Skip()
    # -----------------------------
    # LLM 호출 (비동기)
    # -----------------------------
    def run_llm(self, user_input):
        def worker():
            try:
                document_context = self.text_ctrl.GetValue()
                result = self.llm.process(user_input, document_context)

                action = result.get("action")

                if action and action != "none":
                    wx.CallAfter(
                        self.registry.call_tool,
                        action,
                        result.get("parameters", {})
                    )

            except Exception as e:
                wx.CallAfter(
                    self.console.AppendText,
                    f"\n[ERROR] {str(e)}\n"
                )

        threading.Thread(target=worker, daemon=True).start()