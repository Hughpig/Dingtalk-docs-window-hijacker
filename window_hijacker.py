import win32gui
import win32process
import uiautomation as auto
import time
import pyperclip
import webbrowser
import psutil

# ================= 配置区 =================
KEYWORDS = ["表单", "钉钉文档", "智能填表", "预约"]
EDGE_PATH = r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"
# =========================================

class Win32Hijacker:
    def __init__(self):
        self.processed_handles = set()

    def get_process_name(self, hwnd):
        try:
            _, pid = win32process.GetWindowThreadProcessId(hwnd)
            return psutil.Process(pid).name().lower()
        except:
            return ""

    def solve_via_handle(self, hwnd):
        try:
            win = auto.ControlFromHandle(hwnd)
            if not win.Exists(0): return False
            
            print(f"🚨 [捕获] 句柄:{hwnd} 标题:{win.Name}")
            win.SetActive()
            rect = win.BoundingRectangle
            share_btn = win.ButtonControl(searchDepth=15, Name="分享")
            if share_btn.Exists(0.5):
                share_btn.Click()
                print("   - UI点击【分享】")
            else:
                cx, cy = rect.right - 80, rect.top + 70
                auto.Click(cx, cy)
                print(f"   - 坐标点击【分享】: ({cx}, {cy})")

            time.sleep(0.8) # 等待菜单弹出

            found_copy = False
            for _ in range(5):
                copy_btn = auto.ButtonControl(searchDepth=10, Name="复制链接")
                if not copy_btn.Exists(0):
                    copy_btn = auto.MenuItemControl(searchDepth=10, Name="复制链接")
                
                if copy_btn.Exists(0):
                    copy_btn.Click()
                    print("   - 成功点击【复制链接】")
                    found_copy = True
                    break
                # time.sleep(0.2)

            if found_copy:
                # time.sleep(0.3)
                url = pyperclip.paste().strip()
                if url.startswith("http"):
                    print(f"   - 🚀 弹射成功: {url[:50]}")
                    # 调用 Edge
                    import os
                    os.startfile(EDGE_PATH, "open", url)
                    # 关闭钉钉旧窗口
                    win.GetWindowPattern().Close()
                    return True
            else:
                print("   - ❌ 没找到复制链接按钮")
                
        except Exception as e:
            print(f"   - ⚠️ 出错: {e}")
        return False

    def scan(self):
        def callback(hwnd, extra):
            if not win32gui.IsWindowVisible(hwnd): return
            if hwnd in self.processed_handles: return

            title = win32gui.GetWindowText(hwnd)
            class_name = win32gui.GetClassName(hwnd)
            process_name = self.get_process_name(hwnd)

            # 逻辑：只要是钉钉进程下的窗口，且标题匹配关键词
            if "dingtalk" in process_name:
                # 如果是 WebBrowserView 或者是命中了关键词的窗口
                if "WebBrowserView" in class_name or any(k in title for k in KEYWORDS):
                    if title != "钉钉" and title != "":
                        if self.solve_via_handle(hwnd):
                            self.processed_handles.add(hwnd)
                        else:
                            self.processed_handles.add(hwnd)

        win32gui.EnumWindows(callback, None)

    def run(self):
        print("=== 🛡️ 钉钉劫持器 ===")
        while True:
            self.scan()
            time.sleep(1)

if __name__ == "__main__":
    app = Win32Hijacker()
    app.run()
