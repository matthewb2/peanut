import wx
import os

class AboutDialog(wx.Dialog):
    def __init__(self, parent):
        super().__init__(parent, title="About MCP Editor", size=(420, 360))

        panel = wx.Panel(self)
        vbox = wx.BoxSizer(wx.VERTICAL)

        # ===== 로고 로드 =====
        base_path = os.path.dirname(os.path.abspath(__file__))
        logo_path = os.path.join(base_path, "assets", "logo.png")

        if os.path.exists(logo_path):
            image = wx.Image(logo_path, wx.BITMAP_TYPE_ANY)
            image = image.Scale(140, 140, wx.IMAGE_QUALITY_HIGH)
            bitmap = wx.Bitmap(image)
            logo = wx.StaticBitmap(panel, bitmap=bitmap)
            vbox.Add(logo, 0, wx.ALIGN_CENTER | wx.TOP, 15)

        # ===== 타이틀 =====
        title = wx.StaticText(panel, label="MCP Editor")
        font = title.GetFont()
        font.PointSize = 17
        font = font.Bold()
        title.SetFont(font)
        vbox.Add(title, 0, wx.ALIGN_CENTER | wx.TOP, 10)

        # ===== 설명 =====
        desc = wx.StaticText(
            panel,
            label="Context-Aware Coding Editor\nBuilt with wxPython\nVersion 1.0"
        )
        vbox.Add(desc, 0, wx.ALIGN_CENTER | wx.ALL, 10)

        copyright_text = wx.StaticText(
            panel,
            label="© 2026 MCP Project"
        )
        vbox.Add(copyright_text, 0, wx.ALIGN_CENTER | wx.BOTTOM, 20)

        # ===== 닫기 버튼 =====
        btn = wx.Button(panel, wx.ID_OK, "Close")
        vbox.Add(btn, 0, wx.ALIGN_CENTER | wx.BOTTOM, 15)

        panel.SetSizer(vbox)
        self.Centre()