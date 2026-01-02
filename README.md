# 场地预约脚本（GUI 与 CLI）

本项目用于华中科技大学场馆预约页面的自动化抢场地，提供图形界面（GUI）和命令行（CLI）两种使用方式。GUI 支持按“场地名称”选择并自动映射到后端的 pian ID，前端不再展示原始 ID，提高易用性。

## 功能概览
- 图形界面选择场馆、日期、时段、同伴身份，支持按“场地名称”自定义选择
- 自动监控所选场地的开放与可用状态，仅在目标场地可用时提交预约
- 命令行模式支持交互配置与自动提交
- 可打包为 Windows 可执行文件（.exe）分发使用

## 主要文件
- GUI 启动器：[gui_launcher.py](file:///d:/python/venv/%E9%A2%84%E7%BA%A6/gui_launcher.py)
- 核心逻辑（CLI）：[main.py](file:///d:/python/venv/%E9%A2%84%E7%BA%A6/main.py)
- 场地信息提取：从 HTML 中解析 pian 与场地名称映射 [extra_pian.py](file:///d:/python/venv/%E9%A2%84%E7%BA%A6/extra_pian/extra_pian.py)
- 浏览器与驱动：项目会使用的是 Chrome浏览器与 chromedriver（捆绑资源）。请自行在本地安装Chorme浏览器，并下载好对应的chromedriver.exe放在同main.py目录下，项目会自动调用运行。

## 环境要求
- Windows 10/11
- Python 3.10（或兼容版本）
- 依赖库：selenium、webdriver_manager、beautifulsoup4、tkinter（标准库）

安装依赖示例：

```bash
d:\python\venv\Scripts\python.exe -m pip install selenium webdriver-manager beautifulsoup4
```

## 使用指南（GUI）
- 运行 GUI：

```bash
d:\python\venv\Scripts\python.exe gui_launcher.py
```

- 在弹出的浏览器中手动登录至主页
- 在界面中选择：
  - 场馆、日期、时间段、同伴身份
  - 可点击“查看场地列表”，选择“场地名称”（例如：普通区1）
  - 支持在“自定义场地”中输入“名称或ID”，多个用逗号分隔
- 点击“开始”，程序会仅监控你的自定义选择（如已设置），否则使用该场馆的预设场地列表

相关代码参考：
- GUI 自定义名称→ID 的解析与设置：[gui_launcher.py:L270-L296](file:///d:/python/venv/%E9%A2%84%E7%BA%A6/gui_launcher.py#L270-L296)
- “查看场地列表”展示名称而非 ID：[gui_launcher.py:L329-L389](file:///d:/python/venv/%E9%A2%84%E7%BA%A6/gui_launcher.py#L329-L389)

## 使用指南（CLI）
直接执行：

```bash
d:\python\venv\Scripts\python.exe main.py
```

- 命令行将引导选择场馆、日期、时间段和同伴身份
- 程序将从硬编码的映射或自定义 ID 列表中加载监控目标
- 监控到目标场地可用后，在可抢时段自动提交

关键逻辑参考：
- 自定义列表优先（不再被预设覆盖）：[main.py:L301-L310](file:///d:/python/venv/%E9%A2%84%E7%BA%A6/main.py#L301-L310)
- 监控与提交：构造查询 payload 并更新 token，[query_and_submit_via_selenium](file:///d:/python/venv/%E9%A2%84%E7%BA%A6/main.py#L351-L506) 与 [submit_reservation_via_selenium](file:///d:/python/venv/%E9%A2%84%E7%BA%A6/main.py#L515-L653)

## 打包为 EXE（PyInstaller）
推荐使用项目虚拟环境的 Python 调用 pip 与 PyInstaller：

```bash
d:\python\venv\Scripts\python.exe -m pip install pyinstaller
```

打包 GUI（建议单目录，便于捆绑资源）：

```bash
d:\python\venv\Scripts\python.exe -m PyInstaller ^
  -n 场地预约GUI ^
  --icon 1.ico ^
  --add-data "resources/chrome-win64/chrome-win64/*;resources/chrome/" ^
  --add-data "chromedriver.exe;." ^
  gui_launcher.py
```

- 输出路径为 `dist/场地预约GUI/场地预约GUI.exe`
- `--add-data` 的第二段为打包后内部路径。脚本会从 `resources/chrome/chrome.exe` 与 `resources/chromedriver.exe` 读取，如果你的源码目录是 `resources/chrome-win64/chrome-win64`，上面的指令会在打包时映射到 `resources/chrome/`，保持一致
- 如需单文件模式（不推荐，体积大且资源管理不便），可使用 `-F` 替换上面的命令

示例单文件打包：

```bash
d:\python\venv\Scripts\python.exe -m PyInstaller ^
  -F -n 场地预约GUI ^
  --icon 1.ico ^
  --add-data "resources/chrome-win64/chrome-win64/*;resources/chrome/" ^
  --add-data "chromedriver.exe;." ^
  gui_launcher.py
```

## 常见问题
- pip 命令不可用：使用 `python -m pip` 而非 `pip`
- CSRF Token 提取失败：请确保访问合法预约页并检查页面中 `name='cg_csrf_token'`，参考 [extract_csrf_token](file:///d:/python/venv/%E9%A2%84%E7%BA%A6/main.py#L260-L289)
- Chrome 版本不匹配：项目尝试优先使用打包内置的 Chrome 与 chromedriver；如仍失败，请在系统中安装匹配版本或更新驱动
- 自定义场地无效：GUI 的自定义场地会被优先使用；若为空才会加载预设列表（见 [main.py:L301-L310](file:///d:/python/venv/%E9%A2%84%E7%BA%A6/main.py#L301-L310)）

## 免责声明
本项目仅供学习与研究使用，请遵守学校相关规定与网站使用条款。作者不对使用本项目造成的任何后果承担责任。

