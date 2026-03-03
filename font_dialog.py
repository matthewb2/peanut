import wx


class FontDialog(wx.Dialog):
    def __init__(self, parent, current_font):
        super().__init__(parent, title="글꼴", size=(450, 420))

        self.selected_font = current_font

        panel = wx.Panel(self)
        main_vbox = wx.BoxSizer(wx.VERTICAL)

        # =============================
        # 상단: 3개 콤보박스 가로 배치
        # =============================
        top_hbox = wx.BoxSizer(wx.HORIZONTAL)

        # 1️⃣ 글꼴 목록
        font_label = wx.StaticText(panel, label="글꼴")
        enum = wx.FontEnumerator()
        enum.EnumerateFacenames()
        font_list = sorted(enum.GetFacenames())

        self.font_combo = wx.ComboBox(
			panel,
			choices=font_list,
			style=wx.CB_READONLY
		)

        # 2️⃣ 글꼴 스타일
        style_label = wx.StaticText(panel, label="글꼴 스타일")
        self.style_combo = wx.ComboBox(
            panel,
            choices=["보통", "기울임", "굵게", "굵게 기울임"],
            style=wx.CB_READONLY
        )

        # 3️⃣ 크기
        size_label = wx.StaticText(panel, label="크기")
        self.size_combo = wx.ComboBox(
            panel,
            choices=[str(i) for i in range(8, 49)],
            style=wx.CB_READONLY
        )

        # 각 그룹 세로 배치
        def make_column(label, combo):
            v = wx.BoxSizer(wx.VERTICAL)
            v.Add(label, 0, wx.BOTTOM, 5)
            v.Add(combo, 0, wx.EXPAND)
            return v

        top_hbox.Add(make_column(font_label, self.font_combo), 1, wx.ALL | wx.EXPAND, 10)
        top_hbox.Add(make_column(style_label, self.style_combo), 1, wx.ALL | wx.EXPAND, 10)
        top_hbox.Add(make_column(size_label, self.size_combo), 0, wx.ALL | wx.EXPAND, 10)

        main_vbox.Add(top_hbox, 0, wx.EXPAND)

        # =============================
        # 체크 옵션
        # =============================
        option_box = wx.BoxSizer(wx.HORIZONTAL)
        self.underline_chk = wx.CheckBox(panel, label="밑줄")
        self.strike_chk = wx.CheckBox(panel, label="취소선")

        option_box.Add(self.underline_chk, 0, wx.ALL, 10)
        option_box.Add(self.strike_chk, 0, wx.ALL, 10)

        main_vbox.Add(option_box, 0)

        # =============================
        # 미리보기 영역
        # =============================
        preview_box = wx.StaticBox(panel, label="미리보기")
        preview_sizer = wx.StaticBoxSizer(preview_box, wx.VERTICAL)

        self.preview = wx.StaticText(panel, label="가나다 ABC abc 123")
        preview_sizer.Add(self.preview, 1, wx.ALL | wx.ALIGN_CENTER, 20)

        main_vbox.Add(preview_sizer, 1, wx.ALL | wx.EXPAND, 10)

        # =============================
        # 버튼
        # =============================
        btn_sizer = wx.StdDialogButtonSizer()
        ok_btn = wx.Button(panel, wx.ID_OK)
        cancel_btn = wx.Button(panel, wx.ID_CANCEL)

        btn_sizer.AddButton(ok_btn)
        btn_sizer.AddButton(cancel_btn)
        btn_sizer.Realize()

        main_vbox.Add(btn_sizer, 0, wx.ALL | wx.ALIGN_RIGHT, 10)

        panel.SetSizer(main_vbox)

        # =============================
        # 초기값 설정
        # =============================
        self._load_current_font(current_font)

        # 이벤트 연결
        self.font_combo.Bind(wx.EVT_COMBOBOX, self.update_preview)
        self.style_combo.Bind(wx.EVT_COMBOBOX, self.update_preview)
        self.size_combo.Bind(wx.EVT_COMBOBOX, self.update_preview)
        self.underline_chk.Bind(wx.EVT_CHECKBOX, self.update_preview)
        self.strike_chk.Bind(wx.EVT_CHECKBOX, self.update_preview)

        ok_btn.Bind(wx.EVT_BUTTON, self.on_ok)

    # --------------------------------
    # 현재 폰트값 로딩
    # --------------------------------
    def _load_current_font(self, font):
        self.font_combo.SetValue(font.GetFaceName())
        self.size_combo.SetValue(str(font.GetPointSize()))

        if font.GetWeight() == wx.FONTWEIGHT_BOLD and font.GetStyle() == wx.FONTSTYLE_ITALIC:
            self.style_combo.SetValue("굵게 기울임")
        elif font.GetWeight() == wx.FONTWEIGHT_BOLD:
            self.style_combo.SetValue("굵게")
        elif font.GetStyle() == wx.FONTSTYLE_ITALIC:
            self.style_combo.SetValue("기울임")
        else:
            self.style_combo.SetValue("보통")

        self.underline_chk.SetValue(font.GetUnderlined())
        self.update_preview(None)

    # --------------------------------
    # 미리보기 업데이트
    # --------------------------------
    def update_preview(self, event):
        face = self.font_combo.GetValue()
        size = int(self.size_combo.GetValue())

        weight = wx.FONTWEIGHT_NORMAL
        style = wx.FONTSTYLE_NORMAL

        style_text = self.style_combo.GetValue()

        if style_text == "굵게":
            weight = wx.FONTWEIGHT_BOLD
        elif style_text == "기울임":
            style = wx.FONTSTYLE_ITALIC
        elif style_text == "굵게 기울임":
            weight = wx.FONTWEIGHT_BOLD
            style = wx.FONTSTYLE_ITALIC

        font = wx.Font(
            size,
            wx.FONTFAMILY_DEFAULT,
            style,
            weight,
            underline=self.underline_chk.GetValue(),
            faceName=face
        )

        self.preview.SetFont(font)
        self.preview.Refresh()

        self.selected_font = font

    # --------------------------------
    def on_ok(self, event):
        self.EndModal(wx.ID_OK)

    def get_font(self):
        return self.selected_font