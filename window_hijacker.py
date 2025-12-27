import win32gui
import win32process
import uiautomation as auto
import time
import pyperclip
import os
import psutil
import ctypes

# ================= 1. 核心：DPI 感知 =================
try:
    ctypes.windll.shcore.SetProcessDpiAwareness(1)
except:
    ctypes.windll.user32.SetProcessDPIAware()

# ================= 2. 配置区 =================
# 关键词列表
KEYWORDS = ["表单", "钉钉文档", "智能填表", "预约", "填写", "问卷", "文档"]
EDGE_PATH = r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"
# ============================================

class ProHijacker:
    def __init__(self):
        # 记录 (句柄, 标题) 组合，支持单窗口多Tab切换
        self.processed_tasks = set()
        # 缓存钉钉PID，拒绝频繁系统调用
        self.ding_pids = self._get_dingtalk_pids()
        # 搜索超时：0.3秒，平衡速度与稳定性
        auto.SetGlobalSearchTimeout(0.3)

    def _get_dingtalk_pids(self):
        """获取所有钉钉进程ID"""
        pids = set()
        for p in psutil.process_iter(['pid', 'name']):
            if 'dingtalk' in p.info['name'].lower():
                pids.add(p.info['pid'])
        return pids

    def solve_via_handle(self, hwnd, title):
        try:
            win = auto.ControlFromHandle(hwnd)
            if not win.Exists(0): return False
            
            print(f"🚨 [捕获] {title}")
            win.SetActive()
            rect = win.BoundingRectangle
            
            # 优先 UI 语义，找不到则坐标兜底
            share_btn = win.ButtonControl(searchDepth=15, Name="分享")
            if share_btn.Exists(0.2):
                share_btn.Click(simulateMove=False)
                print("   - ✅ UI点击【分享】")
            else:
                auto.Click(rect.right - 85, rect.top + 75)
                print("   - ✅ 坐标点击【分享】")

            # --- 步骤 2：轮询菜单 (优化版) ---
            found_copy = False
            start_wait = time.time()
            
            while time.time() - start_wait < 1.5:
                # 依然从根节点搜，保证能抓到独立菜单窗口
                copy_btn = auto.ButtonControl(searchDepth=10, Name="复制链接")
                if not copy_btn.Exists(0):
                    copy_btn = auto.MenuItemControl(searchDepth=10, Name="复制链接")
                
                if copy_btn.Exists(0):
                    copy_btn.Click(simulateMove=False)
                    print(f"   - ✅ 复制点击成功 (耗时: {int((time.time()-start_wait)*1000)}ms)")
                    found_copy = True
                    break
                time.sleep(0.1)

            if found_copy:
                for _ in range(10): # 尝试 10 次提取剪贴板
                    url = pyperclip.paste().strip()
                    if url.startswith("http"):
                        print(f"   - 🚀 弹射: {url[:30]}...")
                        os.startfile(EDGE_PATH, "open", url)
                        win.GetWindowPattern().Close()
                        return True
                    time.sleep(0.05)
            
            print("   - ❌ 未提取到链接")
            return False
                
        except Exception as e:
            print(f"   - ⚠️ 逻辑中断: {e}")
            return False

    def scan(self):
        """扫描所有顶层窗口，寻找钉钉目标"""
        
        def callback(hwnd, extra):
            if not win32gui.IsWindowVisible(hwnd): return
            
            try:
                _, pid = win32process.GetWindowThreadProcessId(hwnd)
                if pid not in self.ding_pids: return
            except: return

            # 获取标题
            title = win32gui.GetWindowText(hwnd)
            if not title or title == "钉钉" or "qt_image" in title: return
            # 去重
            if (hwnd, title) in self.processed_tasks: return

            class_name = win32gui.GetClassName(hwnd)
            if "WebBrowserView" in class_name or any(k in title for k in KEYWORDS):
                if self.solve_via_handle(hwnd, title):
                    self.processed_tasks.add((hwnd, title))
                else:
                    
                    self.processed_tasks.add((hwnd, title))

        win32gui.EnumWindows(callback, None)

    def run(self):
        print("=== 🛡️ 钉钉劫持器 ===")
        print(f"当前监控 PID: {list(self.ding_pids)[:3]}...")
        
        while True:
            self.scan()
            time.sleep(0.2) # 0.2秒一轮

if __name__ == "__main__":
    app = ProHijacker()
    app.run()
