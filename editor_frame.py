import wx
import wx.stc as stc
import threading
from tool_registry import ToolRegistry
from llm_client import LLMClient


class EditorFrame(wx.Frame):
    def __init__(self):
        super().__init__(None, title="MCP Groq Editor", size=(900, 550))

        # 메뉴바 생성
        menu_bar = wx.MenuBar()

        # 파일 메뉴 생성
        file_menu = wx.Menu()

        # 열기 메뉴 항목 생성
        open_item = file_menu.Append(wx.ID_OPEN, "열기\tCtrl+O", "파일 열기")

        # 종료 메뉴 항목 추가
        exit_item = file_menu.Append(wx.ID_EXIT, "종료\tCtrl+Q", "프로그램 종료")

        # 메뉴바에 파일 메뉴 추가
        menu_bar.Append(file_menu, "파일")

        # 프레임에 메뉴바 설정
        self.SetMenuBar(menu_bar)

        # 이벤트 바인딩
        self.Bind(wx.EVT_MENU, self.on_open, open_item)
        self.Bind(wx.EVT_MENU, self.on_exit, exit_item)

        panel = wx.Panel(self)

        # 📄 메인 에디터 (Scintilla 기반)
        self.text_ctrl = stc.StyledTextCtrl(panel)


        # -----------------------------
        # 기본 설정
        # -----------------------------

        font = wx.Font(
            15,
            wx.FONTFAMILY_MODERN,
            wx.FONTSTYLE_NORMAL,
            wx.FONTWEIGHT_NORMAL,
            faceName="Consolas"   # Windows 기본 고정폭
        )

        self.text_ctrl.StyleSetFont(stc.STC_STYLE_DEFAULT, font)
        self.text_ctrl.StyleClearAll()

        # 줄 번호 마진
        self.text_ctrl.SetMarginType(0, stc.STC_MARGIN_NUMBER)
        self.text_ctrl.SetMarginWidth(0, 30)

        # 탭 설정
        self.text_ctrl.SetTabWidth(4)
        self.text_ctrl.SetUseTabs(False)

        # 자동 줄바꿈
        self.text_ctrl.SetWrapMode(stc.STC_WRAP_WORD)

        # 현재 라인 하이라이트
        self.text_ctrl.SetCaretLineVisible(True)
        self.text_ctrl.SetCaretLineBackground(wx.Colour(240, 240, 240))

        # 선택 색상
        self.text_ctrl.SetSelBackground(True, wx.Colour(0, 120, 215))
        self.text_ctrl.SetSelForeground(True, wx.WHITE)

        # UTF-8 모드
        self.text_ctrl.SetCodePage(stc.STC_CP_UTF8)

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
    # 파일 열기
    # -----------------------------
    def on_open(self, event):
        with wx.FileDialog(
            self,
            "파일 선택",
            wildcard="모든 파일 (*.*)|*.*",
            style=wx.FD_OPEN | wx.FD_FILE_MUST_EXIST
        ) as file_dialog:

            if file_dialog.ShowModal() == wx.ID_CANCEL:
                return

            path = file_dialog.GetPath()

            # 🔥 인코딩 자동 시도
            encodings = ["utf-8", "cp949", "euc-kr", "latin-1"]

            for enc in encodings:
                try:
                    with open(path, "r", encoding=enc) as f:
                        content = f.read()
                        self.text_ctrl.SetText(content)
                        self.text_ctrl.EmptyUndoBuffer()
                        self.text_ctrl.SetSavePoint()
                        self.text_ctrl.SetFocus()
                        self.text_ctrl.GotoPos(0)
                        print(f"[INFO] 열린 인코딩: {enc}")
                        self.text_ctrl.SetFocus()
                    return
                except UnicodeDecodeError:
                    continue
                except Exception as e:
                    wx.MessageBox(str(e), "파일 열기 오류", wx.ICON_ERROR)
                    return

            wx.MessageBox("지원되지 않는 인코딩입니다.", "파일 열기 오류", wx.ICON_ERROR)
    # -----------------------------
    # 종료
    # -----------------------------
    def on_exit(self, event):
        self.Close()

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
                self.console.WriteText("\n")
            else:
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