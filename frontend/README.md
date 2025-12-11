# LogSentinel

**专业的 Web 访问日志分析与取证系统**

LogSentinel 是一个全栈的网络安全日志分析平台，提供实时威胁检测、行为异常分析和安全可视化功能。专为安全分析师（SOC）设计，采用深色主题界面，支持高密度信息展示。

![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Python](https://img.shields.io/badge/python-3.10+-blue.svg)
![Next.js](https://img.shields.io/badge/next.js-14-black)
![TypeScript](https://img.shields.io/badge/typescript-5.0-blue.svg)

<img width="2160" height="1187" alt="image" src="https://github.com/user-attachments/assets/dce57260-22c6-4a21-8e2e-a1f51b71fd2b" />
<img width="2154" height="1146" alt="image" src="https://github.com/user-attachments/assets/fab4baef-e3cf-491f-a863-341bd31af5ef" />



## ✨ 核心特性

### 🔍 威胁检测引擎（基于签名）
- **OWASP Top 10 检测**：SQL 注入、XSS、RCE、路径遍历、文件包含等
- **工具指纹识别**：识别 Sqlmap、Nmap、Nikto、Acunetix 等扫描器
- **Webshell 流量检测**：检测针对 .jsp/.php/.asp 的可疑请求
- **30+ 攻击检测规则**：覆盖常见 Web 攻击模式

### 📊 行为异常分析（启发式/统计）
- **暴力破解检测**：高频 POST 请求到登录端点 + 高失败率（401/403）
- **扫描器检测**：短时间内产生大量 404 错误的 IP
- **数据泄露检测**：响应体大小显著异常
- **敏感路径访问**：访问 /admin、/config、.env 等敏感路径
- **罕见 IP 检测**：从未见过的 IP 访问敏感路径

### 📈 安全可视化仪表盘
- **威胁时间线**：流量趋势图表，标注攻击峰值
- **统计面板**：Top 10 攻击者、Top 10 受害 URL、状态码分布
- **实时监控**：自动刷新，实时更新安全态势
- **高对比度图表**：优化的颜色配置，清晰展示攻击流量

### 🔎 告警研判与取证
- **告警列表**：支持筛选、分页、排序（按严重程度/时间）
- **详情抽屉**：攻击载荷高亮显示
- **解码工具**：自动解码 URL 编码和 Base64 编码
- **原始日志查看**：查看完整的原始日志信息

### 🔬 日志浏览器
- **多条件筛选**：状态码、HTTP 方法、IP、URL、时间范围
- **全文搜索**：在 URL、User-Agent、Raw Log 中搜索
- **动态 Facets**：显示 Top IP 和 Top URL，点击即可筛选
- **URL 参数管理**：所有筛选条件通过 URL 参数保存，支持分享链接

### 🚀 高性能处理
- **支持大文件**：最大支持 1GB 日志文件
- **流式处理**：分批解析和处理，避免内存溢出
- **实时进度**：显示文件处理进度和日志处理进度
- **会话隔离**：每个浏览器会话独立的数据空间


## 🔒 安全特性

### 攻击检测规则

#### SQL 注入（10+ 规则）
- UNION SELECT 注入
- 布尔盲注
- 时间盲注
- 堆叠查询
- 报错注入
- 宽字节注入
- 文件操作（INTO OUTFILE）

#### XSS（15+ 规则）
- Script 标签注入
- 事件处理器（onerror, onclick, onload 等）
- JavaScript 协议
- DOM XSS 特征
- 编码绕过（URL 编码、Unicode 编码）

#### RCE（10+ 规则）
- 系统命令执行（system, exec, shell_exec）
- 反引号命令执行
- eval/assert 代码执行
- 文件包含（include, require）
- 模板注入
- 表达式注入

#### 其他攻击类型
- 路径遍历（../, ..\\）
- Webshell 特征
- 扫描器指纹（Sqlmap, Nmap, Nikto, Acunetix 等）
- SSRF、XXE、JWT 攻击等

### 异常检测

- **扫描器检测**：短时间内大量 404 错误
- **高频请求**：RPM 超过阈值
- **敏感路径访问**：访问管理后台、配置文件等
- **暴力破解**：高频 POST + 高失败率
- **数据泄露**：响应体大小异常
- **罕见 IP**：从未见过的 IP 访问敏感路径

## 🛠️ 技术栈

### 后端
- **Python 3.10+**
- **FastAPI** - 现代、高性能的 Web 框架
- **SQLAlchemy** - ORM 数据库操作
- **SQLite** - 轻量级数据库
- **Pandas** - 高性能日志处理和统计分析（向量化操作）
- **Pydantic** - 数据验证和序列化

### 前端
- **Next.js 14** (App Router) - React 框架
- **TypeScript** - 类型安全
- **Tailwind CSS** - 实用优先的 CSS 框架
- **Recharts** - 数据可视化图表库
- **Lucide React** - 图标库
- **Shadcn/UI** - UI 组件库

### 分析引擎
- **独立 Python 包** - 可单独使用，不依赖 API
- **Pandas 向量化操作** - 高性能日志处理
- **正则表达式模式匹配** - 30+ 攻击检测规则

## 📦 项目结构

```
LogSentinel/
├── analysis_engine/          # 核心分析引擎（独立包）
│   ├── __init__.py
│   ├── models.py            # 数据模型（Pydantic）
│   ├── parsers.py           # 日志解析器（Nginx/Apache）
│   └── detectors.py         # 威胁检测器（签名+异常）
│
├── backend/                 # FastAPI 后端
│   ├── __init__.py
│   ├── main.py             # 主应用入口
│   ├── database.py         # 数据库配置
│   ├── models.py           # ORM 模型（SQLAlchemy）
│   ├── schemas.py          # Pydantic 模型（API）
│   ├── services.py         # 业务逻辑服务
│   ├── migrate_db.py       # 数据库迁移脚本
│   └── routers/            # API 路由
│       ├── upload.py       # 文件上传
│       ├── dashboard.py    # 仪表盘
│       ├── alerts.py       # 告警查询
│       ├── logs.py         # 日志查询
│       ├── admin.py        # 管理功能
│       ├── session.py      # 会话管理
│       └── diagnostics.py  # 诊断工具
│
├── app/                     # Next.js 前端（App Router）
│   ├── layout.tsx          # 根布局
│   ├── page.tsx            # Dashboard 页面
│   ├── globals.css         # 全局样式
│   ├── alerts/             # 告警页面
│   │   └── page.tsx
│   ├── explorer/           # 日志浏览器
│   │   └── page.tsx
│   └── settings/           # 设置页面
│       └── page.tsx
│
├── components/              # React 组件
│   ├── Sidebar.tsx         # 左侧导航栏
│   ├── Header.tsx          # 顶部栏
│   ├── StatCard.tsx        # 统计卡片
│   ├── FileUpload.tsx      # 文件上传组件
│   ├── AnalysisProgress.tsx # 分析进度组件
│   ├── LogHighlighter.tsx # 日志高亮组件
│   ├── AlertDetailDrawer.tsx # 告警详情抽屉
│   ├── SessionProvider.tsx # 会话管理组件
│   └── ui/                 # UI 组件
│       ├── Badge.tsx
│       └── Table.tsx
│
├── lib/                     # 工具库
│   ├── api.ts              # API 客户端
│   ├── types.ts            # TypeScript 类型
│   ├── utils.ts            # 工具函数
│   ├── session.ts          # 会话管理
│   └── events.ts           # 事件系统
│
├── scripts/                 # 工具脚本
│   ├── check_port.py       # 端口检查工具
│   ├── check_analysis.py   # 分析状态检查
│   └── check_db_data.py    # 数据库数据检查
│
├── data/                    # 数据目录（自动创建，不提交到 Git）
│   ├── logsentinel.db     # SQLite 数据库
│   └── uploads/           # 上传的日志文件
│
├── requirements.txt         # Python 依赖
├── package.json            # Node.js 依赖
├── run_server.py           # 后端启动脚本
├── .gitignore              # Git 忽略文件
└── README.md               # 本文档
```

## 🚀 快速开始

### 1. 克隆项目

```bash
git clone https://github.com/yourusername/LogSentinel.git
cd LogSentinel
```

### 2. 安装后端依赖

```bash
# 创建虚拟环境（推荐）
python -m venv venv

# 激活虚拟环境
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# 安装依赖
pip install -r requirements.txt
```

### 3. 安装前端依赖

```bash
npm install
```

### 4. 配置环境变量

创建 `.env.local` 文件（前端）：

```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

### 5. 启动后端服务

```bash
# 方式 1: 使用启动脚本（推荐）
python run_server.py

# 方式 2: 使用自定义端口
python run_server.py 8001

# 方式 3: 直接使用 uvicorn
uvicorn backend.main:app --reload --host 127.0.0.1 --port 8000
```

后端服务将在 `http://localhost:8000` 启动（或您指定的端口）。

**注意**: 如果遇到端口占用错误，请参考"故障排除"部分。

### 6. 启动前端服务

```bash
npm run dev
```

前端应用将在 `http://localhost:3000` 启动。

### 7. 访问应用

打开浏览器访问 `http://localhost:3000`

## 📖 使用指南

### 1. 上传日志文件

1. 访问 Dashboard 页面
2. 点击"上传日志文件"区域
3. 选择或拖拽 Nginx/Apache 日志文件（支持 Common 或 Combined 格式）
4. 文件大小限制：最大 1GB
5. 系统会自动解析、检测威胁并存储
6. 实时查看分析进度

### 2. 查看仪表盘

Dashboard 页面显示：
- **4 个关键指标**：总请求数、总告警数、唯一 IP 数、告警率
- **流量趋势图**：显示总流量和攻击流量，攻击点用红色标记
- **Top 5 攻击源 IP**：横向条形图
- **告警严重程度分布**：饼图

### 3. 告警研判

1. 访问 `/alerts` 页面
2. 使用筛选条件过滤告警（严重程度、攻击类型、源 IP）
3. **排序功能**：
   - 默认按严重程度降序排序（Critical 优先）
   - 点击"时间"或"严重程度"表头切换排序
   - 再次点击同一表头可切换升序/降序
4. 点击表格行查看详情
5. 在详情抽屉中：
   - 查看高亮的攻击特征
   - 点击"解码载荷"查看解码后的内容
   - 查看原始日志信息

### 4. 日志浏览器

1. 访问 `/explorer` 页面
2. 使用搜索栏和过滤器筛选日志：
   - **搜索框**：全文搜索（URL、User-Agent、Raw Log）
   - **状态码**：输入状态码（如 404）
   - **HTTP 方法**：选择 GET、POST 等
   - **IP 地址**：输入 IP 地址
   - **URL**：输入 URL 关键词
   - **时间范围**：选择开始和结束时间
3. 左侧 Facets 显示 Top IP 和 Top URL，点击即可添加到筛选器
4. 所有筛选条件自动保存到 URL 参数，可以分享链接

### 5. 数据管理

访问 `/settings` 页面：
- **重置所有数据**：清除所有日志、告警、分析任务和上传的文件
- 显示详细的删除统计信息

## 🔌 API 文档

启动后端服务后，访问以下地址查看 API 文档：

- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`



## 🧪 开发

### 后端开发

```bash
# 安装开发依赖
pip install -r requirements.txt

# 运行开发服务器（自动重载）
python run_server.py

# 运行数据库迁移
python -m backend.migrate_db
```

### 前端开发

```bash
# 安装依赖
npm install

# 运行开发服务器
npm run dev

# 构建生产版本
npm run build

# 启动生产服务器
npm start

# 代码检查
npm run lint
```

### 工具脚本

```bash
# 检查端口占用
python scripts/check_port.py

# 检查分析状态
python scripts/check_analysis.py

# 检查数据库数据
python scripts/check_db_data.py
```

## 📝 日志格式支持

### Nginx/Apache Common Log Format
```
127.0.0.1 - - [25/Dec/2023:10:30:45 +0800] "GET /index.html HTTP/1.1" 200 1234
```

### Nginx/Apache Combined Log Format
```
127.0.0.1 - - [25/Dec/2023:10:30:45 +0800] "GET /index.html HTTP/1.1" 200 1234 "http://example.com" "Mozilla/5.0"
```

### 支持的时间戳格式
- `%d/%b/%Y:%H:%M:%S %z` (标准格式)
- `%d/%b/%Y:%H:%M:%S` (无时区)
- `%Y-%m-%d %H:%M:%S`


## 📊 性能特性

- **流式处理**：支持最大 1GB 文件，分批处理避免内存溢出
- **向量化操作**：使用 Pandas 向量化操作，高性能日志处理
- **批量数据库操作**：批量插入，提高存储效率
- **实时进度跟踪**：显示文件处理进度和日志处理进度
- **会话隔离**：每个浏览器会话独立的数据空间

---

**LogSentinel** - 让日志分析更简单、更高效、更安全 🔐
