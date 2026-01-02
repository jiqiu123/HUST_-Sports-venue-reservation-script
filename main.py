import time
import json
import sys
import random
import subprocess
import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
from datetime import datetime, timedelta, date

class QuietChromeService(ChromeService):
    def start(self):
        if getattr(self, "process", None):
            return
        cmd = [self.path] + self.command_line_args()
        try:
            self.process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                stdin=subprocess.DEVNULL,
                creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0),
            )
        except OSError as err:
            raise err
        self.assert_process_still_running()
        count = 0
        while not self.is_connectable():
            count += 1
            if count >= 50:
                raise Exception("ChromeDriver unable to start/connect")
            time.sleep(0.1)

# ================= 配置区域 (请修改以下参数) =================
BASE_URL = "https://pecg.hust.edu.cn"
QUERY_URL = "/cggl/front/ajax/getsyzt"
SUBMIT_URL = "/cggl/front/step2"
TARGET_URL = f"{BASE_URL}/wescms/"
COOKIE_FILE = "hust_cookies.json"

# ----------------- 抢购目标设置 -----------------
TARGET_VENUE_ID = "69"  # 西区体育馆_羽毛球 ID
TARGET_DATE = "2025-12-30"  # 【目标】日期
TARGET_START_TIME = "08:00:00"  # 【目标】开始时间
TARGET_END_TIME = "10:00:00"  # 【目标】结束时间
TARGET_PIAN_ID = "134"  # 【目标】场地 PIAN ID
PARTNER_CARD_TYPE = "1"  # 同伴身份 (1: 学生)
# ===========================================

VENUE_MAP = {
    # 室内场地
    "光谷体育馆_主馆羽毛球": "45",
    "光谷体育馆_乒乓球": "122",
    "西区体育馆_羽毛球": "69",
    "西区体育馆_乒乓球": "124",
    "游泳馆_游泳池": "96",
    "游泳馆_二楼羽毛球": "117",
    # 室外场地
    "东区操场_韵苑网球1": "74",
    "东区操场_匹克球": "127",
    "东区操场_韵苑网球2": "130",
    "中心区操场_沁苑网球1": "73",
    "中心区操场_沙地网球1": "75",
    "中心区操场_沙地网球2": "128",
    "中心区操场_沁苑网球2": "129",
    "西区操场_西边网球1": "72",
    "西区操场_西边网球2": "131",
}

def interactive_setup():
    """交互式配置目标参数"""
    global TARGET_VENUE_ID, TARGET_DATE, TARGET_START_TIME, TARGET_END_TIME, PARTNER_CARD_TYPE
    
    if GUI_MODE:
        print("[-] GUI 模式：跳过命令行交互配置，使用全局变量设置。")
        return

    print("\n" + "=" * 60)
    print("【 交互式配置向导 】")
    print("=" * 60)
    
    # 1. 选择场馆
    print("\n[-] 请选择目标场馆:")
    venue_list = list(VENUE_MAP.items())
    for idx, (name, vid) in enumerate(venue_list):
        print(f"  [{idx}] {name} (ID: {vid})")
        
    while True:
        try:
            choice = input("\n>>> 请输入场馆序号 (回车默认使用 '西区体育馆_羽毛球'): ").strip()
            if not choice:
                TARGET_VENUE_ID = "69"
                print(f"[-] 已选择: 西区体育馆_羽毛球 (ID: {TARGET_VENUE_ID})")
                break
            
            choice_idx = int(choice)
            if 0 <= choice_idx < len(venue_list):
                name, vid = venue_list[choice_idx]
                TARGET_VENUE_ID = vid
                print(f"[-] 已选择: {name} (ID: {TARGET_VENUE_ID})")
                break
            else:
                print("输入序号超出范围。")
        except ValueError:
            print("请输入有效的数字序号。")

    # 2. 选择日期
    print("\n[-] 请选择目标日期:")
    today = date.today()
    date_options = [today + timedelta(days=i) for i in range(3)]
    
    for idx, d in enumerate(date_options):
        day_name = ["今天", "明天", "后天"][idx]
        print(f"  [{idx}] {d} ({day_name})")
        
    while True:
        try:
            choice = input(f"\n>>> 请输入日期序号 (回车默认使用 '{today}'): ").strip()
            if not choice:
                TARGET_DATE = str(today)
                print(f"[-] 已选择: {TARGET_DATE} (今天)")
                break
            
            choice_idx = int(choice)
            if 0 <= choice_idx < len(date_options):
                TARGET_DATE = str(date_options[choice_idx])
                day_name = ["今天", "明天", "后天"][choice_idx]
                print(f"[-] 已选择: {TARGET_DATE} ({day_name})")
                break
            else:
                print("输入序号超出范围。")
        except ValueError:
            print("请输入有效的数字序号。")

    # 3. 选择时间段
    
    # 确定是否为羽毛球馆
    # 通过遍历 VENUE_MAP 找到当前 ID 对应的名称
    selected_venue_name = ""
    for name, vid in VENUE_MAP.items():
        if vid == TARGET_VENUE_ID:
            selected_venue_name = name
            break
            
    is_badminton = "羽毛球" in selected_venue_name
    
    if is_badminton:
        print("\n[-] 请选择时间段 (2小时/段):")
        time_options = []
        # 从08:00到20:00，每2小时一个起点
        for h in range(8, 21, 2):
            start_str = f"{h:02d}:00:00"
            end_str = f"{h+2:02d}:00:00"
            time_options.append((start_str, end_str))
    else:
        print("\n[-] 请选择时间段 (1小时/段):")
        time_options = []
        # 从08:00到21:00，每1小时一个起点
        for h in range(8, 22, 1):
             start_str = f"{h:02d}:00:00"
             end_str = f"{h+1:02d}:00:00"
             time_options.append((start_str, end_str))
        
    for idx, (start, end) in enumerate(time_options):
        print(f"  [{idx}] {start} - {end}")
        
    while True:
        default_start, default_end = time_options[0]
        try:
            choice = input(f"\n>>> 请输入时间段序号 (回车默认使用 '{default_start} - {default_end}'): ").strip()
            if not choice:
                TARGET_START_TIME = default_start
                TARGET_END_TIME = default_end
                print(f"[-] 已选择: {TARGET_START_TIME} - {TARGET_END_TIME}")
                break
                
            choice_idx = int(choice)
            if 0 <= choice_idx < len(time_options):
                TARGET_START_TIME, TARGET_END_TIME = time_options[choice_idx]
                print(f"[-] 已选择: {TARGET_START_TIME} - {TARGET_END_TIME}")
                break
            else:
                print("输入序号超出范围。")
        except ValueError:
            print("请输入有效的数字序号。")

    # 4. 选择同伴身份
    print("\n[-] 请选择同伴身份:")
    partner_options = [("学生", "1"), ("教职工", "2"), ("校外人员", "3")]
    for idx, (label, code) in enumerate(partner_options):
        print(f"  [{idx}] {label} (代码: {code})")
    while True:
        try:
            choice = input("\n>>> 请输入身份序号 (回车默认使用 '学生'): ").strip()
            if not choice:
                PARTNER_CARD_TYPE = "1"
                print("[-] 已选择: 学生 (代码: 1)")
                break
            choice_idx = int(choice)
            if 0 <= choice_idx < len(partner_options):
                label, code = partner_options[choice_idx]
                PARTNER_CARD_TYPE = code
                print(f"[-] 已选择: {label} (代码: {code})")
                break
            else:
                print("输入序号超出范围。")
        except ValueError:
            print("请输入有效的数字序号。")

# ----------------- 动态变量 (强制初始化为失败标记) -----------------
DYNAMIC_TOKEN = "728706f14d2cc64c71739d48a0fb7a56"  # 初始 Token
CSRF_TOKEN = 'CSRF_EXTRACTION_FAILED'  # 失败标记
GUI_MODE = False  # GUI 模式标记
PAUSED = False

def get_resource_path(p):
    base = getattr(sys, "_MEIPASS", os.path.abspath("."))
    return os.path.join(base, p)

# ===============================================================
# 场地 PIAN ID 映射表 (Hardcoded fallback IDs)
# ===============================================================
PIAN_ID_MAP = {
    # 1. 光谷体育馆
    "45": ['110', '133', '215', '216', '218', '376', '217', '219', '220', '221', '222', '223', '224', '368', '369', '370', '377', '371', '372', '373', '374', '375'],  # 光谷体育馆_主馆羽毛球
    "122": ['606', '607', '608', '609', '610', '611', '612', '613', '614'], # 光谷体育馆_乒乓球 (场2网上)

    # 2. 西区体育馆
    "69": ['584', '300', '299', '298', '297', '301', '134', '295', '296'],  # 西区体育馆_羽毛球
    "124": ['625', '626', '627', '628', '629', '630', '631', '632', '633'], # 西区体育馆_乒乓球

    # 3. 游泳馆
    "96": ['550'], # 游泳馆_游泳池
    "117": ['587', '588', '589', '590', '591', '592', '593', '594', '595'], # 游泳馆_二楼羽毛球

    # 4. 东区操场
    "127": ['651', '652', '653', '654', '655', '656', '657', '658'], # 东区操场_匹克球
    "130": ['662', '663', '664', '665'], # 东区操场_韵苑网球2 (1小时场)
    "74": ['662', '663', '664', '665'],#东区操场_韵苑网球1 (ID 74)

    # 5. 中心区操场
    "129": ['660', '661'], # 中心区操场_沁苑网球2 (1小时场)
    "73": ['315', '317', '322'], # 中心区操场_沁苑网球1 (2小时场)
    "128": ['659', '668'], # 中心区操场_沙地网球2 (1小时场)
    "75": ['318'], # 中心区操场_沙地网球1 (2小时场)

    # 6. 西区操场
    "131": ['666', '667'], # 西区操场_西边网球2 (1小时场)
    "72": ['271', '272'], # 西区操场_西边网球1 (2小时场)
}

# =================================================================
# 核心稳定功能：使用 Driver 发送 AJAX 请求
# =================================================================

def extract_csrf_token(driver):
    """使用 JavaScript 强行验证 CSRF 字段是否存在及获取其值"""
    try:
        # 使用 JavaScript 直接查找元素并返回其 value。这是最稳定的提取方式。
        js_code_check = """
            var element = document.getElementsByName('cg_csrf_token')[0];
            return element ? element.value : 'ELEMENT_NOT_FOUND';
        """
        token = driver.execute_script(js_code_check)

        if token == 'ELEMENT_NOT_FOUND':
            print("\n" + "!" * 60)
            print("[!!! 致命错误：CSRF 字段名很可能错了 !!!]")
            print("脚本在当前页面没有找到名为 'cg_csrf_token' 的元素。")
            print("请手动检查页面源码，并用正确的 'name' 替换代码中的 'cg_csrf_token'。")
            print("脚本已退出，请修正名称。")
            print("!" * 60)
            return 'CSRF_EXTRACTION_FAILED'

        if token and token != 'ELEMENT_NOT_FOUND':
            print(f"[+] 动态提取 CSRF Token 成功: {token[:10]}...")
            return token

        print("[!!!] 警告：找到 cg_csrf_token 元素，但其 value 为空。")
        return 'CSRF_EXTRACTION_FAILED'

    except Exception as e:
        print(f"[!!!] 提取 CSRF Token 发生异常: {e}")
        return 'CSRF_EXTRACTION_FAILED'


def scrape_and_select_pian(driver):
    """
    根据当前选择的场馆 ID，直接加载预设的 Pian ID 列表。
    如果预设列表中没有，则提示使用手动输入。
    (已禁用自动探测功能，改为使用可靠的硬编码列表)
    """
    global TARGET_PIAN_ID
    
    print("\n" + "=" * 60)
    print("【 场地 (Pian) ID 配置 】")
    print("=" * 60)

    # 优先检查是否已有自定义设置 (例如 GUI 传入的列表)
    if isinstance(TARGET_PIAN_ID, list) and len(TARGET_PIAN_ID) > 0:
        print(f"[-] 检测到已设定自定义场地列表 (GUI/Manual)。")
        print(f"[-] 使用目标列表: {TARGET_PIAN_ID}")
        return TARGET_PIAN_ID

    # 优先检查预设映射表
    if TARGET_VENUE_ID in PIAN_ID_MAP:
        preset_ids = PIAN_ID_MAP[TARGET_VENUE_ID]
        print(f"[-] 检测到当前场馆 ({TARGET_VENUE_ID}) 存在预设场地列表。")
        print(f"[-] 加载 {len(preset_ids)} 个场地 ID: {preset_ids}")
        TARGET_PIAN_ID = preset_ids
        print(f"\n[+] 已启用全选监控模式 (预设列表)")
        return TARGET_PIAN_ID
    
    # 如果没有预设，则提示手动输入
    print("\n" + "!" * 60)
    print(f"[!!! 注意：当前场馆 (ID: {TARGET_VENUE_ID}) 尚未录入预设场地列表 !!!]")
    print("自动探测功能已关闭，请手动输入场地 ID。")
    print("!" * 60)
    
    if GUI_MODE:
        if TARGET_PIAN_ID and len(TARGET_PIAN_ID) > 0:
             print(f"[-] GUI模式使用预设/手动ID: {TARGET_PIAN_ID}")
             return TARGET_PIAN_ID
        
        print("[!] GUI 模式下未检测到预设 ID，且不支持中途弹窗输入，设置为空列表。")
        TARGET_PIAN_ID = []
        return TARGET_PIAN_ID

    # 提供手动输入作为救急方案
    manual_input = input("\n>>> 请手动输入场地 ID (如有多个用逗号分隔): ").strip()
    if manual_input:
        # 处理逗号分隔
        parts = manual_input.replace("，", ",").split(",")
        manual_ids = []
        for p in parts:
            p = p.strip()
            if p:
                manual_ids.append(p)
        
        if manual_ids:
            TARGET_PIAN_ID = manual_ids
            print(f"[-] 已手动设置目标场地 ID: {TARGET_PIAN_ID}")
        else:
            print("[!] 输入无效，设置为空列表。")
            TARGET_PIAN_ID = []
    else:
        print("[!] 未输入任何 ID，设置为空列表。")
        TARGET_PIAN_ID = []

    return TARGET_PIAN_ID


def query_and_submit_via_selenium(driver):
    global DYNAMIC_TOKEN
    global CSRF_TOKEN
    loop_count = 0
    pending_pian_id = None

    # 构造查询 Payload
    # 注意: TARGET_PIAN_ID 现在应该是一个列表
    if isinstance(TARGET_PIAN_ID, str):
        target_ids = [TARGET_PIAN_ID]
    else:
        target_ids = TARGET_PIAN_ID
        
    print(f"[-] 监控场地列表: {target_ids}")

    time_slot = f"{TARGET_START_TIME}-{TARGET_END_TIME}"
    data_payload_parts = [f"{pid}@{time_slot}" for pid in target_ids]
    data_payload = ",".join(data_payload_parts) + ","

    # 构造查询用的 JS 代码模板 (使用同步XHR，因为这是被允许且能更新token的)
    QUERY_JS_TEMPLATE = """
        var xhr = new XMLHttpRequest();
        xhr.open('POST', arguments[0], false); 
        xhr.setRequestHeader('Content-Type', 'application/x-www-form-urlencoded; charset=UTF-8');
        xhr.setRequestHeader('X-Requested-With', 'XMLHttpRequest');

        var payload = 'changdibh=' + arguments[1] + 
                      '&data=' + arguments[2] + 
                      '&date=' + arguments[3] + 
                      '&time=' + arguments[4] + 
                      '&token=' + arguments[5];

        xhr.send(payload);
        return xhr.responseText;
    """

    print("\n" + "=" * 50)
    print("【测试模式启动】正在运行测试脚本...")
    print(f"目标: {TARGET_DATE} {TARGET_START_TIME} 场地ID: {TARGET_PIAN_ID}")
    print("=" * 50)

    # 解析目标时间对象
    target_dt_str = f"{TARGET_DATE} {TARGET_START_TIME}"
    target_dt = datetime.strptime(target_dt_str, "%Y-%m-%d %H:%M:%S")

    while True:
        loop_count += 1
        now = datetime.now()
        current_time = now.strftime("%Y-%m-%d %H:%M:%S")
        
        if PAUSED:
            time.sleep(0.5)
            continue

        open_today_8 = datetime.combine(date.today(), datetime.strptime("08:00:00", "%H:%M:%S").time())
        open_nextday_8 = open_today_8 + timedelta(days=1)
        if now.time() >= datetime.strptime("22:00:00", "%H:%M:%S").time():
            open_time = open_nextday_8
        else:
            open_time = open_today_8
        to_open = (open_time - now).total_seconds()
        to_target = (target_dt - now).total_seconds()

        if to_open > 60:
            sleep_time = 1.0
            mode = "预热巡航(>60s)"
        elif 10 < to_open <= 60:
            sleep_time = 0.3
            mode = "预热巡航(<=60s)"
        elif 0 < to_open <= 10:
            sleep_time = 0.1
            mode = "临近开枪(<=10s)"
        else:
            if to_target > 120:
                sleep_time = 0.5
                mode = "常规巡航"
            elif 30 < to_target <= 120:
                sleep_time = 0.3
                mode = "加速巡航"
            elif 3 < to_target <= 30:
                sleep_time = 0.1
                mode = "高速巡航"
            else:
                sleep_time = 0.08
                mode = "冲刺模式"

        sleep_time = max(0.05, sleep_time + random.uniform(-0.02, 0.02))

        hh = int(max(0, to_open) // 3600)
        mm = int(max(0, to_open % 3600) // 60)
        ss = int(max(0, to_open % 60))
        countdown = f"{hh:02d}:{mm:02d}:{ss:02d}"
        print(f"[-] [{mode}] 倒计时到8:00 {countdown}, 距离开始 {to_target:.1f}s, 下次等待 {sleep_time:.2f}s")

        try:
            print(f"[Debug] 发送查询请求... Token: {DYNAMIC_TOKEN[:10]}...")
            response_text = driver.execute_script(
                QUERY_JS_TEMPLATE,
                QUERY_URL,
                TARGET_VENUE_ID,
                data_payload,
                TARGET_DATE,
                current_time,
                DYNAMIC_TOKEN
            )
            
            # 打印响应的前200个字符用于调试
            print(f"[Debug] 收到响应: {response_text[:200]}...")
            
            data = json.loads(response_text)

            # 2. 更新 Token
            new_token = data[0].get('token')
            if new_token: 
                print(f"[Debug] Token 更新: {DYNAMIC_TOKEN[:10]}... -> {new_token[:10]}...")
                DYNAMIC_TOKEN = new_token
            else:
                print("[Debug] 响应中未包含新 Token")

            # 3. 检查可用性
            is_available = False
            for message in data[0].get('message', []):
                # 打印所有场地的状态以便确认
                # print(f"[Debug] 场地 {message.get('pian')} 状态: {message.get('zt')}")
                
                # 如果 TARGET_PIAN_ID 是列表，则检查所有在列表中的场地
                current_pian = message.get('pian')
                target_ids = TARGET_PIAN_ID if isinstance(TARGET_PIAN_ID, list) else [TARGET_PIAN_ID]
                
                if current_pian in target_ids:
                    # zt=2 表示已预订/不可用, 其它值表示可用
                    if message.get('zt') != 2:
                        is_available = True
                        print(f"[!!!] 发现目标场地 {current_pian} 可用！状态码: {message.get('zt')}")
                        
                        # 只有在需要提交时才更新全局 TARGET_PIAN_ID 为当前找到的这个 ID
                        global TARGET_PIAN_ID_FINAL
                        TARGET_PIAN_ID_FINAL = current_pian
                        break
                    else:
                        pass # 目标场地不可用
                        # print(f"[-] 目标场地 {current_pian} 不可用")

            if is_available:
                print(
                    f"\n[SUCCESS!!!] 场地 {TARGET_PIAN_ID_FINAL} ({TARGET_START_TIME}-{TARGET_END_TIME}) 当前可用！")
                if to_open <= 0:
                    print("[-] 已到开放时间，立即提交预定...")
                    if submit_reservation_via_selenium(driver, final_pian_id=TARGET_PIAN_ID_FINAL):
                        return True
                else:
                    pending_pian_id = TARGET_PIAN_ID_FINAL
                    print("[-] 未到开放时间，已锁定目标场地，继续等待至 08:00 再提交。")

            time.sleep(sleep_time) 

        except Exception as e:
            # 这里的查询失败通常是网络或 token 导致的，重试是合理的。
            print(f"[!!!] 查询过程中发生错误: {e}")
            time.sleep(random.uniform(0.5, 1.5))


# 文件名: login_script.py (替换 submit_reservation_via_selenium 函数)

def submit_reservation_via_selenium(driver, final_pian_id=None):
    global DYNAMIC_TOKEN
    global CSRF_TOKEN

    # 如果没有传入 final_pian_id，则尝试使用全局 TARGET_PIAN_ID
    # 但如果全局是列表，这里会报错，所以必须确保传入确定的 ID
    if not final_pian_id:
        if isinstance(TARGET_PIAN_ID, str):
            final_pian_id = TARGET_PIAN_ID
        else:
            print("[!!!] 错误：提交时未指定具体的场地 ID，且全局设置为列表模式。")
            return False

    # 强制检查 CSRF token 是否已经获取
    if CSRF_TOKEN == 'CSRF_EXTRACTION_FAILED':
        print("[!!!] 无法提交：CSRF Token 提取失败。请确保是选择的合法时间段预约！请重启脚本并修正 CSRF 字段名称。")
        return False

    # 1. 构造完整的 Payload
    submission_payload = (
        f"changdibh={TARGET_VENUE_ID}"
        f"&date={TARGET_DATE}"
        f"&starttime={TARGET_START_TIME}"
        f"&endtime={TARGET_END_TIME}"
        f"&partnerCardtype={PARTNER_CARD_TYPE}"
        f"&choosetime={final_pian_id}"
        f"&cg_csrf_token={CSRF_TOKEN}"
        f"&token={DYNAMIC_TOKEN}"
    )

    print(f"\n[Debug] 提交使用的 CSRF Token: {CSRF_TOKEN[:10]}...")

    # --- 终极修复：使用 JS 提交表单 ---
    SUBMIT_FORM_JS_TEMPLATE = """
        var form = document.createElement('form');
        form.method = 'POST';
        form.action = arguments[0]; // SUBMIT_URL

        // 解析 Payload 字符串，并创建隐藏的 input 字段
        var payload = arguments[1].split('&');
        for (var i = 0; i < payload.length; i++) {
            var parts = payload[i].split('=');
            var input = document.createElement('input');
            input.type = 'hidden';
            input.name = parts[0];
            input.value = parts[1];
            form.appendChild(input);
        }

        document.body.appendChild(form);
        form.submit(); // 浏览器将自动处理重定向和 Referer
    """

    try:
        # 2. 执行 JS 脚本，触发 POST 请求并跳转
        print("[Debug] 正在执行 JS 提交表单...")
        driver.execute_script(
            SUBMIT_FORM_JS_TEMPLATE,
            SUBMIT_URL,
            submission_payload
        )
        print("[Debug] JS 提交表单完成，等待页面跳转...")
        try:
            WebDriverWait(driver, 2).until(EC.alert_is_present())
            alert = driver.switch_to.alert
            print(f"[Debug] 页面提示: {alert.text}")
            alert.accept()
            print("[Debug] 检测到预约未开放提示，恢复监控。")
            return False
        except Exception:
            pass
        try:
            driver.execute_script("""
                var els = Array.from(document.querySelectorAll('button, a, input[type=button]'));
                for (var el of els) {
                    var t = (el.innerText || el.value || '').trim();
                    if (t.indexOf('确定') !== -1) { el.click(); }
                }
            """)
        except Exception:
            pass

        # 3. 等待浏览器跳转到支付页面
        try:
            WebDriverWait(driver, 30).until(
                EC.url_contains("toPay")
            )
        except Exception as wait_error:
            print(f"[Debug] 等待跳转超时或失败: {wait_error}")
            print(f"[Debug] 当前页面 URL: {driver.current_url}")
            # 即使超时，也尝试检查一下 URL，万一已经跳了只是没捕获到

        final_url = driver.current_url
        print(f"[Debug] 最终页面 URL: {final_url}")
        
        if 'toPay' in final_url and 'orderId' in final_url:
            print("\n" + "=" * 50)
            print("[!!! GREAT SUCCESS !!!]")
            print(f"预约成功！浏览器已跳转到支付页面: {final_url}")
            print("请在浏览器中立即完成支付！不要关闭窗口！")
            
            # --- 强制跳转修复：如果当前页面没有显示支付内容，尝试手动跳转到该 URL ---
            if not GUI_MODE:
                print("\n[!!!] 正在尝试强制刷新支付页面...")
                try:
                    driver.get(final_url)
                    print("[-] 已执行强制跳转/刷新。")
                except Exception as e:
                    print(f"[!] 强制跳转失败: {e}")

            print("=" * 50)
            
            print("\n[!!!] 浏览器将保持开启状态，请手动支付。")
            if GUI_MODE:
                return True
            else:
                try:
                    input(">>> 支付完成后，请在此处按回车键以关闭脚本和浏览器...")
                except Exception:
                    return True
            
            return True
        else:
            # 如果没有跳转到 toPay，但页面变化了
            print("\n" + "!" * 50)
            print("[!!! 提交失败，但已绕过 XHR 限制 !!!]")
            print(f"浏览器当前 URL: {driver.current_url[:100]}...")
            print("服务器可能返回了错误页面，请在浏览器中查看详情。")
            print("!" * 50)
            return False

    except Exception as e:
        # 如果超时或发生其他异常
        print("\n" + "!" * 50)
        print(f"[!!!] 提交预定失败: 跳转支付页面超时或发生异常。错误: {e}")
        print("请检查浏览器当前页面内容，可能服务器返回了错误信息。")
        print("!" * 50)
        return False

def init_browser():
    """初始化并返回 Chrome 驱动"""
    options = webdriver.ChromeOptions()
    options.headless = False
    options.add_argument("--start-maximized")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-extensions")
    options.add_experimental_option("excludeSwitches", ["enable-automation", "enable-logging"])
    options.add_argument("--log-level=3")
    options.add_argument("--disable-logging")
    options.add_experimental_option('useAutomationExtension', False)
    # 保持 User-Agent 伪装
    options.add_argument(
        'user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36')
    temp_profile = os.path.join(os.environ.get("LOCALAPPDATA", os.path.abspath(".")), "hust_portable_profile")
    try:
        os.makedirs(temp_profile, exist_ok=True)
    except:
        pass
    options.add_argument(f"--user-data-dir={temp_profile}")

    bundled_chrome = get_resource_path("resources/chrome/chrome.exe")
    bundled_driver = get_resource_path("resources/chromedriver.exe")
    
    if os.path.exists(bundled_chrome):
        options.binary_location = bundled_chrome
    
    driver = None
    try:
        if os.path.exists(bundled_driver):
            service = QuietChromeService(executable_path=bundled_driver)
            driver = webdriver.Chrome(service=service, options=options)
        else:
            driver = webdriver.Chrome(options=options)
    except Exception:
        service = QuietChromeService(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=options)

    driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
        "source": """
            Object.defineProperty(navigator, 'webdriver', {
              get: () => undefined
            })
        """
    })

    driver.get(TARGET_URL)
    return driver

def run_task(driver):
    """登录后执行的抢购任务"""
    global CSRF_TOKEN
    
    # 0. 交互式配置 (如果 GUI_MODE 会自动跳过)
    interactive_setup()

    # 登录完成后，跳转到预约查询页面，这个页面包含 CSRF token
    driver.get(f"{BASE_URL}/cggl/front/syqk?date={TARGET_DATE}&type=1&cdbh={TARGET_VENUE_ID}")
    print("[-] 浏览器已跳转到查询页面。")
    
    # 核心：动态提取 CSRF Token
    CSRF_TOKEN = extract_csrf_token(driver)

    if CSRF_TOKEN == 'CSRF_EXTRACTION_FAILED':
        # 如果提取失败，脚本已打印错误信息，直接退出
        return
        
    # 1. 在开始抢购前，自动探测或选择 Pian ID
    scrape_and_select_pian(driver)

    # 使用 LIVE DRIVER 进行抢购
    query_and_submit_via_selenium(driver)

def login_and_start_snatching():
    global CSRF_TOKEN
    driver = None
    try:
        # ... (浏览器配置) ...
        driver = init_browser()

        # 提示用户手动登录 (流程不变)
        art_text = r"""
            ========================================================================
            ██╗  ██╗██╗   ██╗███████╗████████╗    ██████╗ ███████╗ ██████╗  ██████╗ 
            ██║  ██║██║   ██║██╔════╝╚══██╔══╝    ██╔══██╗██╔════╝██╔════╝ ██╔════╝ 
            ███████║██║   ██║███████╗   ██║       ██████╔╝█████╗  ██║      ██║  ███╗
            ██╔══██║██║   ██║╚════██║   ██║       ██╔═══╝ ██╔══╝  ██║      ██║   ██║
            ██║  ██║╚██████╔╝███████║   ██║       ██║     ███████╗╚██████╗ ╚██████╔╝
            ╚═╝  ╚═╝ ╚═════╝ ╚══════╝   ╚═╝       ╚═╝     ╚══════╝ ╚═════╝  ╚═════╝
            ========================================================================
                华中科技大学场馆预约脚本 --- By 几秋！！！
            ========================================================================
            """
        # 打印输出
        print(art_text)
        print("\n" + "=" * 50)
        print("【重要提示】请在弹出的浏览器中手动完成登录。")
        print("请登录直到你看到【登录成功后的主页】。")
        print("=" * 50 + "\n")

        while True:
            if GUI_MODE:
                # GUI 模式下由外部调用 run_task，这里只是占位或等待
                time.sleep(1)
                continue

            user_input = input(">>> 如果您已在浏览器中登录成功，请输入 'y' 并回车启动抢购: ")
            if user_input.lower() == 'y':
                run_task(driver)
                break
            time.sleep(1)

    except Exception as e:
        print(f"[!!!] 登录或抢购脚本发生错误: {e}")
        try:
            if hasattr(sys, "frozen"):
                input(">>> 出错后按回车退出...")
        except:
            pass

    finally:
        if driver:
            try:
                print("[-] 正在安全关闭浏览器会话...")
                driver.quit()
            except Exception:
                pass


if __name__ == "__main__":
    login_and_start_snatching()
