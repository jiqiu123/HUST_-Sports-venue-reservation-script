import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import threading
import sys
import main as hust_main
from datetime import date, timedelta
import time
import webbrowser

# 启用 GUI 模式
hust_main.GUI_MODE = True

# ==========================================
# 场地详细信息映射 (Generated from extra_pian.py)
# ==========================================
VENUE_PIAN_INFO = {
    "光谷体育馆_主馆羽毛球": [
        {'id': '110', 'name': '普通区1'}, {'id': '133', 'name': '普通区2'}, {'id': '215', 'name': '普通区3'},
        {'id': '216', 'name': '普通区4'}, {'id': '218', 'name': '普通区5'}, {'id': '376', 'name': '普通区21'},
        {'id': '217', 'name': '普通区6'}, {'id': '219', 'name': '普通区7'}, {'id': '220', 'name': '普通区8'},
        {'id': '221', 'name': '普通区9'}, {'id': '222', 'name': '普通区10'}, {'id': '223', 'name': '普通区11'},
        {'id': '224', 'name': '普通区12'}, {'id': '368', 'name': '普通区13'}, {'id': '369', 'name': '普通区14'},
        {'id': '370', 'name': '普通区15'}, {'id': '377', 'name': '普通区22'}, {'id': '371', 'name': '普通区16'},
        {'id': '372', 'name': '普通区17'}, {'id': '373', 'name': '普通区18'}, {'id': '374', 'name': '普通区19'},
        {'id': '375', 'name': '普通区20'},
    ],
    "光谷体育馆_乒乓球": [
        {'id': '606', 'name': '普通区10'}, {'id': '607', 'name': '普通区11'}, {'id': '608', 'name': '普通区12'},
        {'id': '609', 'name': '普通区13'}, {'id': '610', 'name': '普通区14'}, {'id': '611', 'name': '普通区15'},
        {'id': '612', 'name': '普通区16'}, {'id': '613', 'name': '普通区17'}, {'id': '614', 'name': '普通区18'},
    ],
    "西区体育馆_羽毛球": [
        {'id': '584', 'name': '9号场地'}, {'id': '300', 'name': '7号场地'}, {'id': '299', 'name': '6号场地'},
        {'id': '298', 'name': '5号场地'}, {'id': '297', 'name': '4号场地'}, {'id': '301', 'name': '8号场地'},
        {'id': '134', 'name': '1号场地'}, {'id': '295', 'name': '2号场地'}, {'id': '296', 'name': '3号场地'},
    ],
    "西区体育馆_乒乓球": [
        {'id': '625', 'name': '普通区11'}, {'id': '626', 'name': '普通区12'}, {'id': '627', 'name': '普通区13'},
        {'id': '628', 'name': '普通区14'}, {'id': '629', 'name': '普通区15'}, {'id': '630', 'name': '普通区16'},
        {'id': '631', 'name': '普通区17'}, {'id': '632', 'name': '普通区18'}, {'id': '633', 'name': '普通区19'},
    ],
    "游泳馆_二楼羽毛球": [
        {'id': '587', 'name': '羽毛球1'}, {'id': '588', 'name': '羽毛球2'}, {'id': '589', 'name': '羽毛球3'},
        {'id': '590', 'name': '羽毛球4'}, {'id': '591', 'name': '羽毛球5'}, {'id': '592', 'name': '羽毛球6'},
        {'id': '593', 'name': '羽毛球7'}, {'id': '594', 'name': '羽毛球8'}, {'id': '595', 'name': '羽毛球9'},
    ],
    "游泳馆_游泳池": [
        {'id': '550', 'name': '游泳池'},
    ],
    "东区操场_匹克球": [
        {'id': '651', 'name': '1号场地'}, {'id': '652', 'name': '2号场地'}, {'id': '653', 'name': '3号场地'},
        {'id': '654', 'name': '4号场地'}, {'id': '655', 'name': '5号场地'}, {'id': '656', 'name': '6号场地'},
        {'id': '657', 'name': '7号场地'}, {'id': '658', 'name': '8号场地'},
    ],
    "东区操场_韵苑网球1": [
        {'id': '662', 'name': '1号场地'}, {'id': '663', 'name': '2号场地'}, {'id': '664', 'name': '3号场地'},
        {'id': '665', 'name': '4号场地'},
    ],
    "中心区操场_沁苑网球1": [
        {'id': '660', 'name': '1号场地'}, {'id': '661', 'name': '2号场地'},
    ],
    "中心区操场_沁苑网球2": [
        {'id': '315', 'name': '3号场地'}, {'id': '317', 'name': '4号场地'}, {'id': '322', 'name': '5号场地'},
    ],
    "中心区操场_沙地网球1": [
        {'id': '659', 'name': '2号场地'}, {'id': '668', 'name': '3号场地'},
    ],
    "中心区操场_沙地网球2": [
        {'id': '318', 'name': '1号场地'},
    ],
    "西区操场_西边网球1": [
        {'id': '666', 'name': '1号场地'}, {'id': '667', 'name': '2号场地'},
    ],
    "西区操场_西边网球2": [
        {'id': '271', 'name': '3号球场'}, {'id': '272', 'name': '4号球场'},
    ],
}

class RedirectText(object):
    def __init__(self, text_ctrl):
        self.output = text_ctrl

    def write(self, string):
        self.output.insert(tk.END, string)
        self.output.see(tk.END)

    def flush(self):
        pass

class App:
    def __init__(self, root):
        self.root = root
        self.root.title("HUST 场馆预约助手 (GUI版)")
        self.root.geometry("600x750")
        
        self.driver = None
        
        # 样式设置
        style = ttk.Style()
        style.configure("TButton", font=("Microsoft YaHei", 10))
        style.configure("TLabel", font=("Microsoft YaHei", 10))
        
        # 主框架
        main_frame = ttk.Frame(root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # --- 顶部功能区 ---
        top_bar = ttk.Frame(main_frame)
        top_bar.pack(fill=tk.X, pady=(0, 5))
        self.btn_refresh = ttk.Button(top_bar, text="刷新", command=self.refresh_page, state=tk.DISABLED, width=8)
        self.btn_refresh.pack(side=tk.RIGHT, padx=(8, 0))
        self.btn_pause = ttk.Button(top_bar, text="暂停", command=self.toggle_pause, width=8)
        self.btn_pause.pack(side=tk.RIGHT, padx=(8, 0))
        ttk.Button(top_bar, text="联系作者", command=self.show_contact_info, width=10).pack(side=tk.RIGHT)
        
        # --- 配置区域 ---
        config_frame = ttk.LabelFrame(main_frame, text="预约配置", padding="10")
        config_frame.pack(fill=tk.X, pady=5)
        
        # 1. 场馆选择
        ttk.Label(config_frame, text="选择场馆:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.venue_var = tk.StringVar()
        self.venue_names = list(hust_main.VENUE_MAP.keys())
        self.venue_cb = ttk.Combobox(config_frame, textvariable=self.venue_var, values=self.venue_names, state="readonly", width=30)
        self.venue_cb.grid(row=0, column=1, sticky=tk.W, padx=5, pady=5)
        self.venue_cb.current(0)
        self.venue_cb.bind("<<ComboboxSelected>>", self.on_venue_change)
        
        # 2. 日期选择
        ttk.Label(config_frame, text="选择日期:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.date_var = tk.StringVar()
        self.date_cb = ttk.Combobox(config_frame, textvariable=self.date_var, state="readonly", width=30)
        self.date_cb.grid(row=1, column=1, sticky=tk.W, padx=5, pady=5)
        self.update_date_options()
        
        # 3. 时间段选择
        ttk.Label(config_frame, text="选择时间:").grid(row=2, column=0, sticky=tk.W, pady=5)
        self.time_var = tk.StringVar()
        self.time_cb = ttk.Combobox(config_frame, textvariable=self.time_var, state="readonly", width=30)
        self.time_cb.grid(row=2, column=1, sticky=tk.W, padx=5, pady=5)
        # 初始化时间段
        self.update_time_slots()
        
        # 4. 同伴身份
        ttk.Label(config_frame, text="同伴身份:").grid(row=3, column=0, sticky=tk.W, pady=5)
        self.partner_var = tk.StringVar()
        self.partner_cb = ttk.Combobox(config_frame, textvariable=self.partner_var, state="readonly", width=30)
        self.partner_cb['values'] = ("学生 (代码: 1)", "教职工 (代码: 2)", "校外人员 (代码: 3)")
        self.partner_cb.current(0)
        self.partner_cb.grid(row=3, column=1, sticky=tk.W, padx=5, pady=5)

        # 5. 自定义场地
        ttk.Label(config_frame, text="自定义场地:").grid(row=4, column=0, sticky=tk.W, pady=5)
        self.manual_id_var = tk.StringVar()
        self.manual_id_entry = ttk.Entry(config_frame, textvariable=self.manual_id_var, width=32)
        self.manual_id_entry.grid(row=4, column=1, sticky=tk.W, padx=5, pady=5)
        ttk.Label(config_frame, text="(可选，多个用逗号分隔，可输入名称，空着默认随机可用场地)").grid(row=5, column=1, sticky=tk.W, padx=5)
        self.btn_show_ids = ttk.Button(config_frame, text="查看场地列表", command=self.show_pian_ids)
        self.btn_show_ids.grid(row=4, column=2, sticky=tk.W, padx=8)
        
        # --- 操作按钮 ---
        btn_frame = ttk.Frame(main_frame, padding="10")
        btn_frame.pack(fill=tk.X, pady=5)
        
        self.btn_browser = ttk.Button(btn_frame, text="1. 打开浏览器并登录", command=self.launch_browser)
        self.btn_browser.pack(side=tk.LEFT, padx=10, expand=True, fill=tk.X)
        
        self.btn_start = ttk.Button(btn_frame, text="2. 开始预约", command=self.start_snatching, state=tk.DISABLED)
        self.btn_start.pack(side=tk.LEFT, padx=10, expand=True, fill=tk.X)
        
        # --- 日志输出 ---
        log_frame = ttk.LabelFrame(main_frame, text="运行日志", padding="5")
        log_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        
        self.log_text = scrolledtext.ScrolledText(log_frame, height=15, state='normal', font=("Consolas", 9))
        self.log_text.pack(fill=tk.BOTH, expand=True)
        
        # 重定向 stdout
        sys.stdout = RedirectText(self.log_text)
        print("[-] GUI 初始化完成。请选择配置并按步骤操作。")
        
        # 版权水印
        footer = ttk.Label(main_frame, text="本脚本版权归于“几秋123”所有，仅供学习交流使用禁止用于商业用途！！！", 
                           font=("Microsoft YaHei", 9), foreground="gray", anchor="center")
        footer.pack(side=tk.BOTTOM, pady=5)

    def update_date_options(self):
        today = date.today()
        options = []
        self.date_values = [] # 存储真实日期字符串
        for i in range(3):
            d = today + timedelta(days=i)
            day_name = ["今天", "明天", "后天"][i]
            options.append(f"{d} ({day_name})")
            self.date_values.append(str(d))
        self.date_cb['values'] = options
        self.date_cb.current(0)

    def on_venue_change(self, event):
        self.update_time_slots()

    def update_time_slots(self):
        venue_name = self.venue_var.get()
        is_badminton = "羽毛球" in venue_name
        
        self.time_slots = [] # 存储 (start, end)
        display_values = []
        
        if is_badminton:
            # 2小时一段
            for h in range(8, 21, 2):
                start = f"{h:02d}:00:00"
                end = f"{h+2:02d}:00:00"
                self.time_slots.append((start, end))
                display_values.append(f"{start} - {end}")
        else:
            # 1小时一段
            for h in range(8, 22, 1):
                start = f"{h:02d}:00:00"
                end = f"{h+1:02d}:00:00"
                self.time_slots.append((start, end))
                display_values.append(f"{start} - {end}")
                
        self.time_cb['values'] = display_values
        if display_values:
            self.time_cb.current(0)
            
    def launch_browser(self):
        def _task():
            try:
                print("[-] 正在启动浏览器...")
                self.btn_browser.config(state=tk.DISABLED)
                self.driver = hust_main.init_browser()
                print("[+] 浏览器已启动。请在浏览器中手动登录。")
                print("[-] 登录成功后，请点击下方 '开始抢购' 按钮。")
                def enable_controls():
                    self.btn_start.config(state=tk.NORMAL)
                    self.btn_refresh.config(state=tk.NORMAL)
                self.root.after(0, enable_controls)
            except Exception as e:
                print(f"[!] 启动浏览器失败: {e}")
                self.root.after(0, lambda: self.btn_browser.config(state=tk.NORMAL))
                
        threading.Thread(target=_task, daemon=True).start()

    def start_snatching(self):
        if not self.driver:
            messagebox.showerror("错误", "请先打开浏览器！")
            return
            
        # 1. 更新全局配置
        venue_idx = self.venue_cb.current()
        if venue_idx >= 0:
            name = self.venue_names[venue_idx]
            hust_main.TARGET_VENUE_ID = hust_main.VENUE_MAP[name]
            print(f"[-] 设定场馆: {name} (ID: {hust_main.TARGET_VENUE_ID})")
            
        date_idx = self.date_cb.current()
        if date_idx >= 0:
            hust_main.TARGET_DATE = self.date_values[date_idx]
            print(f"[-] 设定日期: {hust_main.TARGET_DATE}")
            
        time_idx = self.time_cb.current()
        if time_idx >= 0:
            start, end = self.time_slots[time_idx]
            hust_main.TARGET_START_TIME = start
            hust_main.TARGET_END_TIME = end
            print(f"[-] 设定时间: {start} - {end}")
            
        partner_idx = self.partner_cb.current()
        # 0->1, 1->2, 2->3
        hust_main.PARTNER_CARD_TYPE = str(partner_idx + 1)
        print(f"[-] 设定同伴类型代码: {hust_main.PARTNER_CARD_TYPE}")

        # 手动ID/名称解析
        manual_input = self.manual_id_var.get().strip()
        if manual_input:
            ids = manual_input.replace("，", ",").split(",")
            raw_parts = [x.strip() for x in ids if x.strip()]
            
            final_ids = []
            # 获取当前场馆的映射表
            current_venue_name = self.venue_names[venue_idx] if venue_idx >= 0 else ""
            info_list = VENUE_PIAN_INFO.get(current_venue_name, [])
            name_to_id = {item['name']: item['id'] for item in info_list}
            
            for part in raw_parts:
                if part in name_to_id:
                    final_ids.append(name_to_id[part])
                else:
                    # 尝试作为ID直接使用
                    final_ids.append(part)
            
            if final_ids:
                hust_main.TARGET_PIAN_ID = final_ids
                print(f"[-] 设定自定义场地ID: {final_ids} (原始输入: {manual_input})")
        
        # 2. 启动任务
        self.btn_start.config(state=tk.DISABLED)
        
        def _task():
            try:
                print("[-] 开始执行抢购任务...")
                hust_main.run_task(self.driver)
            except Exception as e:
                print(f"[!] 任务执行出错: {e}")
            finally:
                print("[-] 任务结束。")
                self.root.after(0, lambda: self.btn_start.config(state=tk.NORMAL))

        threading.Thread(target=_task, daemon=True).start()

    def refresh_page(self):
        if not self.driver:
            messagebox.showerror("错误", "浏览器尚未启动。")
            return
        try:
            self.driver.refresh()
            print("[-] 已刷新当前页面。")
        except Exception as e:
            print(f"[!] 刷新失败: {e}")

    def toggle_pause(self):
        hust_main.PAUSED = not getattr(hust_main, "PAUSED", False)
        state_text = "继续" if hust_main.PAUSED else "暂停"
        self.btn_pause.config(text=state_text)
        print(f"[-] 已切换状态: {'已暂停' if hust_main.PAUSED else '正常运行'}")

    def show_pian_ids(self):
        name = self.venue_var.get()
        
        # 优先使用提取的详细信息
        pian_info_list = VENUE_PIAN_INFO.get(name, [])
        display_items = []
        
        if pian_info_list:
            # 如果有详细信息，显示名称
            for item in pian_info_list:
                display_items.append(item['name'])
        else:
            # 降级：尝试使用 main.py 中的 PIAN_ID_MAP (如果存在)
            vid = hust_main.VENUE_MAP.get(name)
            ids = getattr(hust_main, "PIAN_ID_MAP", {}).get(vid, [])
            display_items = ids

        if not display_items:
            messagebox.showinfo("提示", "当前场馆未配置场地信息。")
            return
            
        top = tk.Toplevel(self.root)
        top.title(f"{name} 场地选择")
        top.geometry("420x360")
        frame = ttk.Frame(top, padding=10)
        frame.pack(fill=tk.BOTH, expand=True)
        
        title_text = f"{name} 可选场地:" if pian_info_list else f"{name} 可选ID:"
        ttk.Label(frame, text=title_text).pack(anchor=tk.W)
        
        lb = tk.Listbox(frame, height=12)
        for i in display_items:
            lb.insert(tk.END, i)
        lb.pack(fill=tk.BOTH, expand=True, pady=6)
        
        btns = ttk.Frame(frame)
        btns.pack(fill=tk.X)
        
        def add_id():
            sel = lb.curselection()
            if not sel:
                return
            val = lb.get(sel[0])
            cur = self.manual_id_var.get().strip()
            if cur:
                parts = [x.strip() for x in cur.replace("，", ",").split(",") if x.strip()]
                if val not in parts:
                    parts.append(val)
                self.manual_id_var.set(",".join(parts))
            else:
                self.manual_id_var.set(val)
                
        def replace_id():
            sel = lb.curselection()
            if not sel:
                return
            val = lb.get(sel[0])
            self.manual_id_var.set(val)
            
        ttk.Button(btns, text="添加到自定义", command=add_id).pack(side=tk.LEFT, padx=6)
        ttk.Button(btns, text="替换为所选", command=replace_id).pack(side=tk.LEFT, padx=6)
        ttk.Button(btns, text="关闭", command=top.destroy).pack(side=tk.RIGHT, padx=6)

    def show_contact_info(self):
        top = tk.Toplevel(self.root)
        top.title("联系作者")
        top.geometry("380x160")
        # 居中显示
        root_x = self.root.winfo_x()
        root_y = self.root.winfo_y()
        top.geometry(f"+{root_x + 100}+{root_y + 100}")
        
        frame = ttk.Frame(top, padding=20)
        frame.pack(fill=tk.BOTH, expand=True)
        
        # 博客链接
        link_frame = ttk.Frame(frame)
        link_frame.pack(anchor=tk.W, pady=5)
        ttk.Label(link_frame, text="作者CSDN博客：", font=("Microsoft YaHei", 10)).pack(side=tk.LEFT)
        
        link = "https://blog.csdn.net/jiqiu12"
        link_lbl = tk.Label(link_frame, text=link, font=("Microsoft YaHei", 10, "underline"), fg="blue", cursor="hand2")
        link_lbl.pack(side=tk.LEFT)
        link_lbl.bind("<Button-1>", lambda e: webbrowser.open(link))
        
        # 邮箱
        ttk.Label(frame, text="联系作者：123jiqiu@gmail.com", font=("Microsoft YaHei", 10)).pack(anchor=tk.W, pady=5)
        
        ttk.Button(frame, text="关闭", command=top.destroy).pack(pady=10)

if __name__ == "__main__":
    root = tk.Tk()
    app = App(root)
    
    # 设置关闭处理
    def on_closing():
        if messagebox.askokcancel("退出", "确定要退出吗？"):
            if app.driver:
                try:
                    app.driver.quit()
                except:
                    pass
            root.destroy()
            sys.exit(0)
            
    root.protocol("WM_DELETE_WINDOW", on_closing)
    root.mainloop()
