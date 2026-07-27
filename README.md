## 项目文件体系


```text
COMPANY_QNA_AGENT/
│
├── api/                    # 外部 API 接口或服务集成模块
│
├── chroma_db/              # Chroma 本地向量数据库存储目录
│   ├── chroma.sqlite3      # 向量元数据 SQLite 数据库文件
│   └── */                  # 高维向量索引二进制分片数据
│
├── config/                 # 系统全局配置中心
│   └── config.py           # 环境变量与全局参数读取配置
│
├── core/                   # 核心业务逻辑层（大脑与引擎）
│   ├── document_parser/    # 文档解析底层支持模块
│   ├── llm_engine/         # 大模型交互引擎
│   │   └── chat_model.py   # 统一的大模型调用与流式/非流式回答生成封装
│   ├── vector_store/       # 向量数据库构建管理
│   │   ├── build_all.py    # 一键重建所有知识库脚本
│   │   ├── build_guide.py  # 受理指南向量化构建脚本
│   │   └── build_qa.py     # 业务问答向量化构建脚本
│   └── query_agent.py      # 主智能体核心逻辑（含智能动态路由与重叠检索）
│
├── data/                   # 数据资产中心（数据流水线原料与半成品）
│   ├── processed/          # 清洗后的结构化文本资产
│   │   ├── 检测受理指南.md   # 降维处理后的大白话结构块文本
│   │   └── AI业务问答.md   # 转化后的问答库标准文本
│   └── raw/                # 原始业务输入文件
│       ├── 健研检测材料送检业务受理指南...xlsx # 原始送检指南复杂表格
│       └── AI业务问答汇总...xlsx               # 原始问答库表格
│
├── prompts/                # 提示词工程管理中心
│   ├── guide_prompt.py     # 受理指南专属 Prompt（含去机械化、完整罗列约束）
│   └── qa_prompt.py        # 业务问答专属 Prompt（精准复刻与问答逻辑）
│
├── tests/                  # 自动化测试与连通性验证脚本
│   ├── test_chat.py        # 对话功能单元测试
│   └── test_llm.py         # 大模型 API 连通性测试
│
├── utils/                  # 工具函数与数据流水线中心
│   ├── parsers/            # 表格专项解析器
│   │   ├── __init__.py
│   │   ├── guide_parser.py # 破解 Excel 合并单元格与降维清洗逻辑
│   │   └── qa_parser.py    # 问答库表格清洗解析器
│   └── data_pipeline.py    # 数据清洗与转换总流水线调度脚本
│
├── venv/                   # Python 虚拟环境目录
├── .env                    # 本地敏感环境变量配置（如 DashScope API Key）
├── .gitignore              # Git 版本控制忽略文件配置
├── app.py                  # Streamlit 前端可视化交互应用入口
├── README.md               # 项目说明与架构文档
└── requirements.txt        # 项目 Python 依赖包清单
