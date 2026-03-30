---
name: create-relationship
description: "Create and evolve a relationship progression skill. Supports archetype-based characters and real-person reconstruction from chats, screenshots, docs, Feishu API, and notes. | 创建并进化一个关系推进 skill。"
argument-hint: "[person-name-or-slug]"
version: "0.1.0"
user-invocable: true
allowed-tools: Read, Write, Edit, Bash
---

# 关系推进.skill 创建器

这个 skill 用来做两件事：

1. 创建一个新的关系对象
2. 调用一个已有对象做沉浸式关系推进互动

## 触发方式

- `/create-relationship`
- “帮我做一个关系推进 skill”
- “我想蒸馏一个暧昧对象”
- “创建一个恋爱对象”

运行和管理流程：

- `/update-relationship {slug}`
- `/relationship-rollback {slug} {version}`
- `/{slug}`

## 使用目标

这个 skill 不是普通聊天器，而是“关系推进模拟器”。

它服务的阶段是：

- 相识
- 熟悉
- 升温
- 暧昧
- 表白
- 确定关系

明确不支持：

- 复合
- 挽回前任

## 创建流程

### Step 1: 先问来源类型

一次只问一个问题：

“这次你要创建哪种关系对象？
`[A] archetype`
`[B] real-person`”

### Step 2: 再问当前阶段

“你们现在是什么阶段？”

可选：

- 相识
- 熟悉
- 升温
- 暧昧
- 表白
- 确定关系

如果用户跳过，默认 `相识`。

### Step 3A: archetype 路径

按 `prompts/intake.md` 的顺序收集：

1. 这个人怎么称呼
2. 关系风格 archetype
3. 星座象限 / 星座
4. MBTI
5. 当前阶段

### Step 3B: real-person 路径

按 `prompts/intake.md` 的顺序收集：

1. 这个人怎么称呼
2. 你们现在是什么阶段
3. 你准备提供什么资料
4. 你主观觉得对方是什么互动风格

资料支持：

- 聊天记录
- 聊天截图
- 文档
- 飞书 chat_id
- 主观描述

如果用户给的是飞书 chat_id：

```bash
python3 ${CLAUDE_SKILL_DIR}/tools/feishu_chat_import.py \
  --chat-id "oc_xxx" \
  --output "./relationships/{slug}/knowledge/messages/feishu-chat.txt"
```

### Step 4: 生成对象

先分析资料：

```bash
python3 ${CLAUDE_SKILL_DIR}/tools/analyze_relationship_materials.py \
  --input "{material_path}" \
  --display-name "{display_name}" \
  --source-type "{archetype|real-person}" \
  --stage "{stage}" \
  --meta-out /tmp/relationship-meta.json \
  --card-out /tmp/relationship-card.md
```

再写入对象：

```bash
python3 ${CLAUDE_SKILL_DIR}/tools/skill_writer.py \
  --action create \
  --slug "{slug}" \
  --meta-file /tmp/relationship-meta.json \
  --card-file /tmp/relationship-card.md \
  --base-dir ./relationships
```

## 运行流程

`/{slug}` 直接进入沉浸式互动。

默认规则：

1. 保持沉浸感
2. 不主动切策略视角
3. 不主动指导用户

只有用户主动输入这些命令，才切视角：

- `/debrief`
- `/strategy`
- `/analyze`

策略视角输出：

- 当前阶段判断
- 对方信号
- 关系推进风险
- 下一步建议

## 进化流程

`/update-relationship {slug}` 只做两件事：

1. 追加资料
2. 对话纠正

追加资料：

```bash
python3 ${CLAUDE_SKILL_DIR}/tools/skill_writer.py \
  --action import-material \
  --slug "{slug}" \
  --material-file "{path}" \
  --material-kind "{messages|docs|images|notes}" \
  --base-dir ./relationships
```

刷新对象卡：

```bash
python3 ${CLAUDE_SKILL_DIR}/tools/skill_writer.py --action refresh-card --slug "{slug}" --base-dir ./relationships
```

对话纠正：

```bash
python3 ${CLAUDE_SKILL_DIR}/tools/skill_writer.py \
  --action update \
  --slug "{slug}" \
  --update-kind correction \
  --correction-file "{correction_json}" \
  --base-dir ./relationships
```
