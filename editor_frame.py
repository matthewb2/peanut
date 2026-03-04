import wx
import wx.stc as stc
import threading
from tool_registry import ToolRegistry
from llm_client import LLMClient
from about_dialog import AboutDialog
from font_dialog import FontDialog


class EditorFrame(wx.Frame):
    def __init__(self):
        super().__init__(None, title="Editor", size=(650, 600))

        # -----------------------------
        # 상태 표시줄
        # -----------------------------
        self.status_bar = self.CreateStatusBar(4)
        self.status_bar.SetStatusWidths([-2, -1, -1, -1])
        self.status_bar.SetStatusText("Ready", 0)
        self.status_bar.SetStatusText("UTF-8", 1)
        self.status_bar.SetStatusText("Ln 1, Col 1", 2)
        self.status_bar.SetStatusText("100%", 3)

        self.current_encoding = "utf-8"

        self._create_menu()

        panel = wx.Panel(self)

        # -----------------------------
        # Splitter
        # -----------------------------
        self.splitter = wx.SplitterWindow(panel)
        self.splitter.SetMinimumPaneSize(30)

        self.editor_panel = wx.Panel(self.splitter)
        self.editor = stc.StyledTextCtrl(self.editor_panel)
        self.editor.SetMarginWidth(0, 0)
        self.editor.SetText("This is example text\n 이것은 예제 문장입니다");

        editor_sizer = wx.BoxSizer(wx.VERTICAL)
        editor_sizer.Add(self.editor, 1, wx.EXPAND)
        self.editor_panel.SetSizer(editor_sizer)

        self.console_panel = wx.Panel(self.splitter)
        self.console = wx.TextCtrl(
            self.console_panel,
            style=wx.TE_MULTILINE | wx.TE_PROCESS_ENTER
        )

        console_sizer = wx.BoxSizer(wx.VERTICAL)
        console_sizer.Add(self.console, 1, wx.EXPAND)
        self.console_panel.SetSizer(console_sizer)

        self.splitter.SplitHorizontally(
            self.editor_panel,
            self.console_panel,
            -50
        )
        self.splitter.SetSashGravity(1.0)

        main_sizer = wx.BoxSizer(wx.VERTICAL)
        main_sizer.Add(self.splitter, 1, wx.EXPAND)
        panel.SetSizer(main_sizer)

        # -----------------------------
        # 기본 폰트
        # -----------------------------
        font = wx.Font(
            14,
            wx.FONTFAMILY_MODERN,
            wx.FONTSTYLE_NORMAL,
            wx.FONTWEIGHT_NORMAL,
            faceName="Consolas"
        )

        self.editor.StyleSetFont(stc.STC_STYLE_DEFAULT, font)
        self.editor.StyleClearAll()

        # 줄번호 기본 숨김
        self.editor.SetMarginType(0, stc.STC_MARGIN_NUMBER)
        self.editor.SetMarginWidth(0, 0)

        self.editor.SetTabWidth(4)
        self.editor.SetUseTabs(False)

        # 자동 줄바꿈 끄기 (가로 스크롤 사용)
        self.editor.SetWrapMode(stc.STC_WRAP_NONE)
        self.editor.SetEndAtLastLine(False)

        #커서 줄 표시
        self.editor.SetCaretLineVisible(False)
        self.editor.SetCaretLineBackground(wx.Colour(240, 240, 240))

        self.editor.SetSelBackground(True, wx.Colour(0, 120, 215))
        self.editor.SetSelForeground(True, wx.WHITE)

        self.editor.SetCodePage(stc.STC_CP_UTF8)

        # Zoom 초기화
        self.editor.SetZoom(0)
        self.update_zoom_status()

        # 이벤트
        #self.Bind(wx.EVT_MENU, self.on_about, about_item)
        self.editor.Bind(wx.EVT_RIGHT_DOWN, self.on_editor_context_menu)
        self.editor.Bind(stc.EVT_STC_UPDATEUI, self.update_status_bar)
        self.editor.Bind(wx.EVT_MOUSEWHEEL, self.on_mouse_wheel_zoom)

        self.console.Bind(wx.EVT_KEY_DOWN, self.on_console_key)

        self.registry = ToolRegistry()
        self.registry.editor_tools.bind_editor(self.editor)

        self.llm = LLMClient()

        self.reset_console()

    # =============================
    # 줄번호 표시 토글
    # =============================
    def on_toggle_line_number(self, event):
        margin_width = self.editor.GetMarginWidth(0)

        if margin_width == 0:
            # 표시
            self.editor.SetMarginWidth(0, 50)
        else:
            # 숨김
            self.editor.SetMarginWidth(0, 0)
    # =============================
    # Zoom 기능
    # =============================
    def on_zoom_in(self, event):
        zoom = self.editor.GetZoom()
        if zoom < 20:
            self.editor.SetZoom(zoom + 1)
        self.update_zoom_status()

    def on_zoom_out(self, event):
        zoom = self.editor.GetZoom()
        if zoom > -10:
            self.editor.SetZoom(zoom - 1)
        self.update_zoom_status()

    def on_zoom_reset(self, event):
        self.editor.SetZoom(0)
        self.update_zoom_status()

    def update_zoom_status(self):
        zoom = self.editor.GetZoom()
        percent = 100 + (zoom * 10)
        self.status_bar.SetStatusText(f"{percent}%", 3)

    def on_mouse_wheel_zoom(self, event):
        if event.ControlDown():
            rotation = event.GetWheelRotation()
            zoom = self.editor.GetZoom()

            if rotation > 0 and zoom < 20:
                self.editor.SetZoom(zoom + 1)
            elif rotation < 0 and zoom > -10:
                self.editor.SetZoom(zoom - 1)

            self.update_zoom_status()
        else:
            event.Skip()

    # =============================
    # 상태표시줄
    # =============================
    def update_status_bar(self, event):
        line = self.editor.GetCurrentLine() + 1
        col = self.editor.GetColumn(self.editor.GetCurrentPos()) + 1
        self.status_bar.SetStatusText(f"Ln {line}, Col {col}", 2)

    # =============================
    # 메뉴
    # =============================
    def _create_menu(self):
        menu_bar = wx.MenuBar()

        file_menu = wx.Menu()
        open_item = file_menu.Append(wx.ID_OPEN, "열기(&O)\tCtrl+O")
        save_item = file_menu.Append(wx.ID_SAVE, "저장(&S)\tCtrl+S")
        file_menu.AppendSeparator()
        exit_item = file_menu.Append(wx.ID_EXIT, "종료(&X)\tCtrl+Q")
        menu_bar.Append(file_menu, "파일(&F)")

        format_menu = wx.Menu()
        font_item = format_menu.Append(
            wx.ID_ANY,
            "글꼴(&F)...\tCtrl+Shift+F"
        )
        menu_bar.Append(format_menu, "서식(&O)")

        view_menu = wx.Menu()

        zoom_menu = wx.Menu()
        zoom_in_item = zoom_menu.Append(wx.ID_ANY, "확대\tCtrl++")
        zoom_out_item = zoom_menu.Append(wx.ID_ANY, "축소\tCtrl+-")
        zoom_reset_item = zoom_menu.Append(wx.ID_ANY, "기본크기\tCtrl+0")

        view_menu.AppendSubMenu(zoom_menu, "확대하기/축소하기")
        view_menu.AppendSeparator()

        # 🔥 어시스턴트 대화창 체크 아이템
        self.assistant_toggle_item = view_menu.AppendCheckItem(
            wx.ID_ANY,
            "어시스턴트 대화창"
        )
        self.assistant_toggle_item.Check(True)  # 기본 표시
        menu_bar.Append(view_menu, "보기(&V)")

        # -----------------------------
        # 인코딩 메뉴 (라디오 버튼)
        # -----------------------------
        encode_menu = wx.Menu()

        self.ansi_item = encode_menu.Append(
            wx.ID_ANY,
            "ANSI",
            kind=wx.ITEM_RADIO
        )

        self.cp949_item = encode_menu.Append(
            wx.ID_ANY,
            "cp949 (euc-kr)",
            kind=wx.ITEM_RADIO
        )

        self.utf8_item = encode_menu.Append(
            wx.ID_ANY,
            "UTF-8",
            kind=wx.ITEM_RADIO
        )

        # 기본 선택
        self.utf8_item.Check(True)

        menu_bar.Append(encode_menu, "인코딩(&A)")
        
        help_menu = wx.Menu()
        about_item = help_menu.Append(wx.ID_ABOUT, "About MCP Editor\tF1")
        menu_bar.Append(help_menu, "도움말(&H)")

        self.SetMenuBar(menu_bar)
        
        
        self.Bind(wx.EVT_MENU, self.on_open, open_item)
        self.Bind(wx.EVT_MENU, self.on_save, save_item)
        self.Bind(wx.EVT_MENU, self.on_exit, exit_item)
        self.Bind(wx.EVT_MENU, self.on_zoom_in, zoom_in_item)
        self.Bind(wx.EVT_MENU, self.on_zoom_out, zoom_out_item)
        self.Bind(wx.EVT_MENU, self.on_zoom_reset, zoom_reset_item)
        self.Bind(wx.EVT_MENU, self.on_choose_font, font_item)
        self.Bind(wx.EVT_MENU, self.on_about, about_item)
        self.Bind(wx.EVT_MENU, self.on_exit, exit_item)
        self.Bind(wx.EVT_MENU, self.on_encoding_change, self.ansi_item)
        self.Bind(wx.EVT_MENU, self.on_encoding_change, self.cp949_item)
        self.Bind(wx.EVT_MENU, self.on_encoding_change, self.utf8_item)
        
        # 🔥 이 줄이 빠져 있었음
        self.Bind(wx.EVT_MENU, self.on_toggle_assistant, self.assistant_toggle_item)

    # =============================
    # 인코딩 변경
    # =============================
    def on_encoding_change(self, event):
        item = event.GetEventObject().FindItemById(event.GetId())
        encoding = item.GetItemLabel()

        # 상태바 표시 변경
        self.status_bar.SetStatusText(encoding, 1)

        # 내부 변수로 저장
        if encoding.startswith("ANSI"):
            self.current_encoding = "latin-1"
        elif encoding.startswith("cp949"):
            self.current_encoding = "cp949"
        else:
            self.current_encoding = "utf-8"
    # =============================
    # 어시스턴트 대화창 토글
    # =============================
    def on_toggle_assistant(self, event):
        if self.assistant_toggle_item.IsChecked():
            # 다시 표시
            if not self.splitter.IsSplit():
                self.splitter.SplitHorizontally(
                    self.editor_panel,
                    self.console_panel,
                    -50
                )
                self.splitter.SetSashGravity(1.0)
        else:
            # 숨기기
            if self.splitter.IsSplit():
                self.splitter.Unsplit(self.console_panel)
    # =============================
    # 기타 기능
    # =============================
    def on_choose_font(self, event):
        current_font = self.editor.StyleGetFont(stc.STC_STYLE_DEFAULT)
        dialog = FontDialog(self, current_font)

        if dialog.ShowModal() == wx.ID_OK:
            chosen_font = dialog.get_font()
            self.editor.StyleSetFont(stc.STC_STYLE_DEFAULT, chosen_font)
            self.editor.StyleClearAll()

        dialog.Destroy()

    def on_about(self, event):
        dlg = AboutDialog(self)
        dlg.ShowModal()
        dlg.Destroy()

    def on_exit(self, event):
        self.Close()

    # =============================
    # Console
    # =============================
    def reset_console(self):
        self.console.SetValue(">>> ")
        self.console.SetInsertionPointEnd()

    def on_console_key(self, event):
        if event.GetKeyCode() == wx.WXK_RETURN:
            if event.ShiftDown():
                self.console.WriteText("\n")
            else:
                self.reset_console()
        else:
            event.Skip()
    # =============================
    # 파일 저장
    # =============================
    def on_save(self, event):
        with wx.FileDialog(
            self,
            "파일 저장",
            wildcard="모든 파일 (*.*)|*.*",
            style=wx.FD_SAVE | wx.FD_OVERWRITE_PROMPT
        ) as file_dialog:

            if file_dialog.ShowModal() == wx.ID_CANCEL:
                return

            path = file_dialog.GetPath()

            try:
                with open(path, "w", encoding=self.current_encoding) as f:
                    f.write(self.editor.GetText())
            except Exception as e:
                wx.MessageBox(str(e), "파일 저장 오류", wx.ICON_ERROR)
    # =============================
    # 파일 열기
    # =============================
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

            encodings = ["utf-8", "cp949", "euc-kr", "latin-1"]

            for enc in encodings:
                try:
                    with open(path, "r", encoding=enc) as f:
                        content = f.read()
                        self.editor.SetText(content)
                        self.editor.EmptyUndoBuffer()
                        self.editor.SetSavePoint()
                        self.editor.GotoPos(0)
                        self.editor.SetFocus()
                    return
                except UnicodeDecodeError:
                    continue
                except Exception as e:
                    wx.MessageBox(str(e), "파일 열기 오류", wx.ICON_ERROR)
                    return

            wx.MessageBox("지원되지 않는 인코딩입니다.", "파일 열기 오류", wx.ICON_ERROR)
    # =============================
    # 에디터 컨텍스트 메뉴
    # =============================
    def on_editor_context_menu(self, event):
        menu = wx.Menu()

        undo_item = menu.Append(wx.ID_UNDO, "실행취소")
        cut_item = menu.Append(wx.ID_CUT, "잘라내기")
        copy_item = menu.Append(wx.ID_COPY, "복사")
        paste_item = menu.Append(wx.ID_PASTE, "붙여넣기")

        menu.AppendSeparator()

        # 줄번호 체크 아이템
        line_number_item = menu.AppendCheckItem(
            wx.ID_ANY,
            "줄번호 표시"
        )
        caret_line_item = menu.AppendCheckItem(
            wx.ID_ANY,
            "커서 라인 표시"
        )

        # 현재 상태 반영
        margin_width = self.editor.GetMarginWidth(0)
        line_number_item.Check(margin_width > 0)

        # 이벤트 연결
        self.Bind(wx.EVT_MENU, self.on_toggle_line_number, line_number_item)
        self.Bind(wx.EVT_MENU, lambda e: self.editor.Undo(), undo_item)
        self.Bind(wx.EVT_MENU, lambda e: self.editor.Cut(), cut_item)
        self.Bind(wx.EVT_MENU, lambda e: self.editor.Copy(), copy_item)
        self.Bind(wx.EVT_MENU, lambda e: self.editor.Paste(), paste_item)

        self.PopupMenu(menu)
        menu.Destroy()

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
                document_context = self.editor.GetValue()
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