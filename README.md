COMPANY_QNA_AGENT/
│
├── api/                    # 外部 API 接口或服务集成模块
├── chroma_db/              # Chroma 向量数据库持久化存储目录
│   ├── 34285c64-.../       # 向量索引二进制分片数据
│   └── chroma.sqlite3      # 向量数据库元数据 SQLite 记录文件
│
├── config/                 # 系统全局配置
│   └── config.py           # 读取环境变量与核心参数配置
│
├── core/                   # 核心业务逻辑层
│   ├── document_parser/    # 文档解析核心逻辑
│   ├── llm_engine/         # 大模型交互引擎
│   │   └── chat_model.py   # 统一的大模型调用与生成封装
│   ├── vector_store/       # 向量库构建脚本
│   │   ├── build_all.py    # 一键重建所有知识库脚本
│   │   ├── build_guide.py  # 受理指南向量化构建
│   │   └── build_qa.py     # 业务问答向量化构建
│   └── query_agent.py      # 主智能体核心逻辑（含智能路由与检索）
│
├── data/                   # 数据资产管理中心
│   ├── processed/          # 清洗后的中间文本资产
│   │   ├── 检测量受理指南.md # 转化后的结构化大白话文本
│   │   └── AI业务问答.md   # 转化后的问答库标准文本
│   └── raw/                # 原始业务输入文件
│       ├── 健研检测材料送检业务受理指南...xlsx # 原始送检指南表格
│       └── AI业务问答汇总...xlsx               # 原始问答库表格
│
├── prompts/                # 提示词工程管理中心
│   ├── guide_prompt.py     # 受理指南专属 Prompt 模板
│   ├── qa_prompt.py        # 业务问答专属 Prompt 模板
│   └── system_prompt.py    # 系统通用基底 Prompt
│
├── tests/                  # 自动化测试与验证脚本
│   ├── test_chat.py        # 对话功能单元测试
│   └── test_llm.py         # 大模型连通性测试
│
├── utils/                  # 工具函数与数据流水线
│   ├── parsers/            # 表格专项解析器
│   │   ├── __init__.py
│   │   ├── guide_parser.py # 处理指南 Excel 合并单元格与降维
│   │   └── qa_parser.py    # 处理问答库表格清洗
│   └── data_pipeline.py    # 数据清洗与转换总流水线
│
├── venv/                   # Python 虚拟环境目录
├── .env                    # 本地敏感环境变量配置（如 API Key）
├── .gitignore              # Git 版本控制忽略文件
├── app.py                  # Streamlit 前端交互界面应用
├── README.md               # 项目说明文档
└── requirements.txt        # 项目 Python 依赖包清单