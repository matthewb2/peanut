# main.py
import wx
from editor_frame import EditorFrame

class MCPTextEditorApp(wx.App):
    def OnInit(self):
        frame = EditorFrame()
        frame.Show()
        return True

if __name__ == "__main__":
    app = MCPTextEditorApp()
    app.MainLoop()