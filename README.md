<p align="center">
  <img src="https://img.shields.io/badge/version-1.0.0-blue.svg" alt="Version">
  <img src="https://img.shields.io/badge/python-3.8+-green.svg" alt="Python">
  <img src="https://img.shields.io/badge/license-MIT-orange.svg" alt="License">
  <img src="https://img.shields.io/badge/zero--dependencies-✓-brightgreen.svg" alt="Zero Dependencies">
</p>

<p align="center">
  <a href="#english">English</a> | 
  <a href="#简体中文">简体中文</a> | 
  <a href="#繁體中文">繁體中文</a>
</p>

---

<a name="english"></a>
# 🚀 PromptFlow-CLI

> **Lightweight Terminal AI Prompt Workflow Orchestration & Version Management Engine**

A zero-dependency Python CLI tool for managing AI prompts with version control, workflow orchestration, and multi-LLM backend support. Perfect for developers who want to organize, version, and orchestrate their AI prompts efficiently.

## ✨ Core Features

| Feature | Description |
|---------|-------------|
| 📜 **Prompt Management** | Create, edit, delete, and organize prompts with ease |
| 🔄 **Version Control** | Full version history with rollback support |
| 🔀 **Workflow Orchestration** | Chain multiple prompts into powerful workflows |
| 🎯 **Variable Substitution** | Template system with `{{variable}}` syntax |
| 🤖 **Multi-LLM Support** | OpenAI, Anthropic, Google, DeepSeek, Zhipu, Ollama, and more |
| 📊 **Interactive TUI** | Beautiful terminal dashboard for visual management |
| 💾 **Import/Export** | Backup and restore your prompts and workflows |
| ⚡ **Zero Dependencies** | Pure Python standard library implementation |

## 🚀 Quick Start

### Installation

```bash
# Install from PyPI (recommended)
pip install promptflow-cli

# Or install from source
git clone https://github.com/gitstq/PromptFlow-CLI.git
cd PromptFlow-CLI
pip install -e .
```

### Basic Usage

```bash
# Create a new prompt
promptflow create my-prompt --content "Write a {{style}} blog post about {{topic}}"

# List all prompts
promptflow list

# Show prompt details
promptflow show <prompt-id>

# Execute a prompt with variables
promptflow run <prompt-id> --var style=professional --var topic=AI

# Launch interactive dashboard
promptflow dashboard
```

## 📖 Detailed Usage Guide

### Prompt Management

```bash
# Create prompt from file
promptflow create code-reviewer --file prompt.txt --category coding --tags "review,code"

# Edit a prompt
promptflow edit <id> --content "New content" --message "Improved prompt"

# Delete a prompt
promptflow delete <id> --force
```

### Version Control

```bash
# List all versions
promptflow version list <id>

# Add new version
promptflow version add <id> --content "Updated content" --message "v2 improvements"

# Rollback to previous version
promptflow version rollback <id> 1.0.0

# Compare versions
promptflow version diff <id> 1.0.0 1.0.1
```

### Workflow Orchestration

```bash
# Create a workflow
promptflow workflow create content-pipeline --description "Content generation workflow"

# Add steps
promptflow workflow add-step content-pipeline --name "research" --prompt <id1>
promptflow workflow add-step content-pipeline --name "write" --prompt <id2>
promptflow workflow add-step content-pipeline --name "review" --prompt <id3>

# Execute workflow
promptflow workflow run content-pipeline --var topic="AI Trends"
```

### Configuration

```bash
# View configuration
promptflow config show

# Set configuration
promptflow config set default_model gpt-4o
promptflow config set default_temperature 0.8
```

## 💡 Design Philosophy

**Why PromptFlow-CLI?**

- **Version Control**: Track changes to your prompts over time, just like code
- **Reusability**: Create templates once, use everywhere with variable substitution
- **Workflow Orchestration**: Chain prompts together for complex AI workflows
- **Zero Dependencies**: No external dependencies means easy installation and deployment
- **Privacy First**: All data stored locally, no cloud required

## 📦 Project Structure

```
promptflow-cli/
├── promptflow/
│   ├── __init__.py      # Package initialization
│   ├── cli.py           # Command line interface
│   ├── core.py          # Core engine
│   ├── models.py        # Data models
│   ├── storage.py       # Storage layer
│   └── tui.py           # Terminal UI dashboard
├── tests/
│   └── test_promptflow.py
├── pyproject.toml
└── README.md
```

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'feat: Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

<a name="简体中文"></a>
# 🚀 PromptFlow-CLI

> **轻量级终端AI Prompt工作流编排与版本管理引擎**

一个零依赖的Python CLI工具，用于管理AI提示词，支持版本控制、工作流编排和多LLM后端。非常适合希望高效组织、版本化和编排AI提示词的开发者。

## ✨ 核心特性

| 特性 | 描述 |
|------|------|
| 📜 **提示词管理** | 轻松创建、编辑、删除和组织提示词 |
| 🔄 **版本控制** | 完整的版本历史，支持回滚 |
| 🔀 **工作流编排** | 将多个提示词串联成强大的工作流 |
| 🎯 **变量替换** | 使用 `{{变量}}` 语法的模板系统 |
| 🤖 **多LLM支持** | 支持 OpenAI、Anthropic、Google、DeepSeek、智谱、Ollama 等 |
| 📊 **交互式TUI** | 美观的终端仪表盘，可视化管理工作流 |
| 💾 **导入/导出** | 备份和恢复您的提示词和工作流 |
| ⚡ **零依赖** | 纯Python标准库实现 |

## 🚀 快速开始

### 安装

```bash
# 从PyPI安装（推荐）
pip install promptflow-cli

# 或从源码安装
git clone https://github.com/gitstq/PromptFlow-CLI.git
cd PromptFlow-CLI
pip install -e .
```

### 基本使用

```bash
# 创建新提示词
promptflow create my-prompt --content "写一篇关于{{topic}}的{{style}}博客文章"

# 列出所有提示词
promptflow list

# 查看提示词详情
promptflow show <prompt-id>

# 执行提示词（带变量）
promptflow run <prompt-id> --var style=专业 --var topic=AI

# 启动交互式仪表盘
promptflow dashboard
```

## 📖 详细使用指南

### 提示词管理

```bash
# 从文件创建提示词
promptflow create code-reviewer --file prompt.txt --category coding --tags "review,code"

# 编辑提示词
promptflow edit <id> --content "新内容" --message "改进了提示词"

# 删除提示词
promptflow delete <id> --force
```

### 版本控制

```bash
# 列出所有版本
promptflow version list <id>

# 添加新版本
promptflow version add <id> --content "更新内容" --message "v2改进"

# 回滚到之前的版本
promptflow version rollback <id> 1.0.0

# 比较版本差异
promptflow version diff <id> 1.0.0 1.0.1
```

### 工作流编排

```bash
# 创建工作流
promptflow workflow create content-pipeline --description "内容生成工作流"

# 添加步骤
promptflow workflow add-step content-pipeline --name "research" --prompt <id1>
promptflow workflow add-step content-pipeline --name "write" --prompt <id2>
promptflow workflow add-step content-pipeline --name "review" --prompt <id3>

# 执行工作流
promptflow workflow run content-pipeline --var topic="AI趋势"
```

### 配置管理

```bash
# 查看配置
promptflow config show

# 设置配置
promptflow config set default_model gpt-4o
promptflow config set default_temperature 0.8
```

## 💡 设计理念

**为什么选择 PromptFlow-CLI？**

- **版本控制**：像管理代码一样追踪提示词的变化
- **可复用性**：一次创建模板，随处使用变量替换
- **工作流编排**：将提示词串联起来实现复杂的AI工作流
- **零依赖**：无外部依赖，安装部署简单
- **隐私优先**：所有数据本地存储，无需云端

## 📦 项目结构

```
promptflow-cli/
├── promptflow/
│   ├── __init__.py      # 包初始化
│   ├── cli.py           # 命令行接口
│   ├── core.py          # 核心引擎
│   ├── models.py        # 数据模型
│   ├── storage.py       # 存储层
│   └── tui.py           # 终端UI仪表盘
├── tests/
│   └── test_promptflow.py
├── pyproject.toml
└── README.md
```

## 🤝 贡献指南

欢迎贡献！请随时提交Pull Request。

1. Fork本仓库
2. 创建特性分支 (`git checkout -b feature/amazing-feature`)
3. 提交更改 (`git commit -m 'feat: 添加新特性'`)
4. 推送到分支 (`git push origin feature/amazing-feature`)
5. 打开Pull Request

## 📄 许可证

本项目采用MIT许可证 - 详情请查看 [LICENSE](LICENSE) 文件。

---

<a name="繁體中文"></a>
# 🚀 PromptFlow-CLI

> **輕量級終端AI Prompt工作流編排與版本管理引擎**

一個零依賴的Python CLI工具，用於管理AI提示詞，支援版本控制、工作流編排和多LLM後端。非常適合希望高效組織、版本化和編排AI提示詞的開發者。

## ✨ 核心特性

| 特性 | 描述 |
|------|------|
| 📜 **提示詞管理** | 輕鬆創建、編輯、刪除和組織提示詞 |
| 🔄 **版本控制** | 完整的版本歷史，支援回滾 |
| 🔀 **工作流編排** | 將多個提示詞串聯成強大的工作流 |
| 🎯 **變數替換** | 使用 `{{變數}}` 語法的模板系統 |
| 🤖 **多LLM支援** | 支援 OpenAI、Anthropic、Google、DeepSeek、智譜、Ollama 等 |
| 📊 **互動式TUI** | 美觀的終端儀表板，視覺化管理工作流 |
| 💾 **匯入/匯出** | 備份和恢復您的提示詞和工作流 |
| ⚡ **零依賴** | 純Python標準庫實現 |

## 🚀 快速開始

### 安裝

```bash
# 從PyPI安裝（推薦）
pip install promptflow-cli

# 或從源碼安裝
git clone https://github.com/gitstq/PromptFlow-CLI.git
cd PromptFlow-CLI
pip install -e .
```

### 基本使用

```bash
# 創建新提示詞
promptflow create my-prompt --content "寫一篇關於{{topic}}的{{style}}博客文章"

# 列出所有提示詞
promptflow list

# 查看提示詞詳情
promptflow show <prompt-id>

# 執行提示詞（帶變數）
promptflow run <prompt-id> --var style=專業 --var topic=AI

# 啟動互動式儀表板
promptflow dashboard
```

## 📖 詳細使用指南

### 提示詞管理

```bash
# 從文件創建提示詞
promptflow create code-reviewer --file prompt.txt --category coding --tags "review,code"

# 編輯提示詞
promptflow edit <id> --content "新內容" --message "改進了提示詞"

# 刪除提示詞
promptflow delete <id> --force
```

### 版本控制

```bash
# 列出所有版本
promptflow version list <id>

# 添加新版本
promptflow version add <id> --content "更新內容" --message "v2改進"

# 回滾到之前的版本
promptflow version rollback <id> 1.0.0

# 比較版本差異
promptflow version diff <id> 1.0.0 1.0.1
```

### 工作流編排

```bash
# 創建工作流
promptflow workflow create content-pipeline --description "內容生成工作流"

# 添加步驟
promptflow workflow add-step content-pipeline --name "research" --prompt <id1>
promptflow workflow add-step content-pipeline --name "write" --prompt <id2>
promptflow workflow add-step content-pipeline --name "review" --prompt <id3>

# 執行工作流
promptflow workflow run content-pipeline --var topic="AI趨勢"
```

### 配置管理

```bash
# 查看配置
promptflow config show

# 設置配置
promptflow config set default_model gpt-4o
promptflow config set default_temperature 0.8
```

## 💡 設計理念

**為什麼選擇 PromptFlow-CLI？**

- **版本控制**：像管理代碼一樣追蹤提示詞的變化
- **可復用性**：一次創建模板，隨處使用變數替換
- **工作流編排**：將提示詞串聯起來實現複雜的AI工作流
- **零依賴**：無外部依賴，安裝部署簡單
- **隱私優先**：所有數據本地存儲，無需雲端

## 📦 專案結構

```
promptflow-cli/
├── promptflow/
│   ├── __init__.py      # 包初始化
│   ├── cli.py           # 命令行接口
│   ├── core.py          # 核心引擎
│   ├── models.py        # 數據模型
│   ├── storage.py       # 存儲層
│   └── tui.py           # 終端UI儀表板
├── tests/
│   └── test_promptflow.py
├── pyproject.toml
└── README.md
```

## 🤝 貢獻指南

歡迎貢獻！請隨時提交Pull Request。

1. Fork本倉庫
2. 創建特性分支 (`git checkout -b feature/amazing-feature`)
3. 提交更改 (`git commit -m 'feat: 添加新特性'`)
4. 推送到分支 (`git push origin feature/amazing-feature`)
5. 打開Pull Request

## 📄 授權條款

本專案採用MIT授權條款 - 詳情請查看 [LICENSE](LICENSE) 文件。

---

<p align="center">
  Made with ❤️ by <a href="https://github.com/gitstq">gitstq</a>
</p>
