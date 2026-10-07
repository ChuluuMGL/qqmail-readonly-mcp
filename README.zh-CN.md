# QQ 邮箱只读 MCP

> **在自己的电脑上，读取订阅、续费与扣款通知。**
>
> Created and maintained by **Chuluu**.

中文 | [English](README.md)

[![Version](https://img.shields.io/badge/version-0.1.0-green)](CHANGELOG.md)
[![License: MIT](https://img.shields.io/badge/license-MIT-yellow)](LICENSE)
[![by Chuluu](https://img.shields.io/badge/by-Chuluu-0E5E43)](https://github.com/ChuluuMGL)

[下载发行包](https://github.com/ChuluuMGL/qqmail-readonly-mcp/releases) · [平台发布说明](docs/PUBLISHING.md) · [安装说明](docs/INSTALL.md) · [测试记录](TESTING.md) · [隐私说明](PRIVACY.md) · [安全边界](SECURITY.md)

## 它是什么

一个精简的 QQ IMAP 只读 MCP 和订阅整理 Agent Skill。助手可按日期、发件人、主题找到候选通知，读取正文，再整理服务、金额、续费时间、自动续费和取消截止日期。关键词只是候选筛选，不保证所有重要邮件都能自动识别。

**0.1.0 · MIT 开源原型。** 每位使用者在自己的机器运行，连接自己的邮箱。当前支持按需读取；不发送邮件、不删除/移动/标记邮件、不取消订阅，也不自动启动后台提醒。

## 开始使用

需要 Python 3.13 或更新版本，运行时没有第三方 Python 依赖。

```sh
git clone https://github.com/ChuluuMGL/qqmail-readonly-mcp.git
cd qqmail-readonly-mcp
python3 -m unittest discover -s tests -v
python3 scripts/run_mcp.py
```

最后一条以 stdio 启动，不开放端口。无凭据时可初始化和列出工具，邮件调用返回 CREDENTIALS_NOT_CONFIGURED；Ctrl-D 退出。

在 macOS 上，可让 MCP 客户端通过以下入口启动安全会话：

```sh
python3 scripts/run_mcp.py --secure
```

**第 1 步填写 QQ 邮箱地址或 QQ 号码，第 2 步才填写授权码。** 授权码在本机遮蔽窗口中输入，仅保留在当前进程内存。不要发到聊天、工具参数、仓库或配置文件中。仅启动进程不会自动接入助手；参见[客户端配置](docs/INSTALL.md)。

## 能力与可靠性

| 能力 | 方式 |
|---|---|
| 文件夹列表 | LIST，解码中文 modified UTF-7 名称 |
| 日期检索 | since 包含当天，before 不包含当天，依据服务器 INTERNALDATE |
| 中文发件人/主题 | 解码 MIME 头后包含匹配；建议先缩小日期范围 |
| 可靠分页 | 保存完整 UID 快照，重启后 cursor 可恢复；新邮件由新查询发现 |
| 读取正文 | UID + UIDVALIDITY、PEEK，正文原始邮件上限 2 MiB |
| 增量恢复 | 未确认批次重放；确认后只推进本地检查点 |

每页 1–100 项，头上限 64 KiB，最多 100,000 个 UID；很大的 SEARCH 响应也可能先触发标准库行长度限制。socket I/O 超时 15 秒，断线最多重连一次；大范围头扫描尚无整体调用 deadline。单个状态目录只运行一个进程，分页快照暂不自动清理。

增量采用至少一次投递。下游先按账户、文件夹、UIDVALIDITY、UID 幂等落盘，再确认整个 receipt；网络失败时不要确认。UIDVALIDITY 改变会使旧身份失效，重新扫描，不按 Message-ID 自动丢弃邮件。

## 隐私与接入边界

严格验证 TLS 证书和主机名；只读 EXAMINE 与 BODY.PEEK；工具参数无法修改服务器、凭据或 TLS。邮箱内容是不可信数据，HTML 不执行、不载入外链。本地状态只存投递和分页元数据，不存正文或授权码。

正文返回给 AI 客户端后，可能按该客户端设置交给模型处理；“本地 IMAP”不表示整个 AI 流程都离线。不要在公开 Issue 上传真实邮件或授权码。

包含本地插件清单和 Skill，尚未在官方目录上架，也未实测桌面插件安装。配置本地 Codex 不会让 dot 自动获得工具。云端接入需另行授权 Tunnel/连接器和常在线机器；本项目不配置这些服务。Sites 托管层不能单独直连 QQ IMAP。

## 维护、版权与授权

由 [Chuluu](https://github.com/ChuluuMGL) 创建和维护，使用 AI 辅助开发。

Copyright (c) 2026 Chuluu。自有源码和文档采用 [MIT](LICENSE)，见 [NOTICE](NOTICE) 与[第三方说明](THIRD_PARTY_NOTICES.md)。独立开源项目，非腾讯或 OpenAI 官方产品。欢迎提交 Issue 和 Pull Request，示例请使用合成数据。

另提供 macOS MCPB 桌面安装包，见 [下载页](https://github.com/ChuluuMGL/qqmail-readonly-mcp/releases/tag/v0.1.0)。需要已有 Python 3.13+；平台收录和客户端安装仍需分别验证。见 [平台提交状态](docs/PLATFORM_SUBMISSION.md)。
