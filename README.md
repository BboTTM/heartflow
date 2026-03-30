<div align="center">

# 关系推进.skill

<hr>

> “聊得来，不等于能推进关系。”<br>
> 让 AI 模仿一个真实的人，陪你把关系从相识走到确定关系。

**把互动风格、边界感、好感信号与推进节奏蒸馏成 AI Skill。<br>
让你在沉浸式互动里练习，必要时再切到策略视角。**

![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)
![Python 3.9+](https://img.shields.io/badge/Python-3.9%2B-blue.svg)
![Claude Code](https://img.shields.io/badge/Claude%20Code-Skill-blueviolet.svg)
![AgentSkills](https://img.shields.io/badge/AgentSkills-Standard-green.svg)

<br>

创建一个关系对象，然后直接开练。<br>
支持自选关系风格 archetype、星座象限/星座、MBTI 生成对象。<br>
也支持聊天截图、文档、飞书 API 和主观描述做真人复刻。<br>
角色不是一次性 prompt，会随着资料导入、对话纠正持续进化。<br>
你可以用它练相识、熟悉、升温、暧昧、表白和确定关系。

[安装](#安装) · [使用](#使用) · [阶段模型](#阶段模型) · [效果示例](#效果示例) · [English](README_EN.md)

</div>

## 安装

这个目录本身就是一个独立 skill。

Claude Code:

```bash
mkdir -p .claude/skills
cp -R /path/to/relationship-skill .claude/skills/create-relationship
```

或全局安装：

```bash
cp -R /path/to/relationship-skill ~/.claude/skills/create-relationship
```

可选依赖：

```bash
pip3 install -r requirements.txt
```

## 使用

### 1. 创建关系对象

```text
/create-relationship
```

创建时支持两条路径：

- `archetype`
  通过关系风格 + 星座 + MBTI 混合生成对象
- `real-person`
  根据聊天记录、截图、文档、飞书 API 和主观描述复刻某个人

创建时会问：

- 这个人怎么称呼
- 你们现在是什么阶段
- 是否从当前阶段直接开始

如果用户跳过阶段，默认从 `相识` 开始。

### 2. 继续养成和纠正

```text
/update-relationship lin
```

可以做两类更新：

- 追加资料
- 对话纠正

原始资料会归档到：

```text
relationships/{slug}/knowledge/
```

纠正记录会归档到：

```text
relationships/{slug}/corrections.jsonl
```

### 3. 直接互动

```text
/lin
```

默认始终保持沉浸式，不会主动跳出剧情给建议。
只有用户主动输入 `/debrief`、`/strategy`、`/analyze` 时，才切换到策略视角。

### 4. 回滚对象

```text
/relationship-rollback lin v2
```

## 阶段模型

固定主线：

`相识 -> 熟悉 -> 升温 -> 暧昧 -> 表白 -> 确定关系`

但用户可以在创建时直接指定当前阶段。

明确限制：

- 不支持复合分支
- 不做挽回前任路线

## 效果示例

场景一：从熟悉阶段开始

```text
用户              ❯ /lin

关系推进.skill     ❯ 今天怎么突然找我？
用户              ❯ 想起你之前说过那家店，我刚好路过。
关系推进.skill     ❯ 你这开场还挺自然的。你去了吗？
```

场景二：切策略视角

```text
用户              ❯ /strategy

关系推进.skill     ❯ 当前阶段判断：熟悉 -> 升温边缘
                  对方信号：回应稳定，愿意接你的话题，但还没有明显情绪投入
                  风险点：过早表露推进意图会破坏自然感
                  下一步建议：围绕共同记忆或线下轻邀约，测试主动性
```

## 飞书聊天记录导入

先准备环境变量：

```bash
export FEISHU_APP_ID="cli_xxx"
export FEISHU_APP_SECRET="xxx"
```

导入聊天记录：

```bash
python3 tools/feishu_chat_import.py \
  --chat-id "oc_xxx" \
  --output ./relationships/lin/knowledge/messages/feishu-chat.txt
```

然后刷新对象卡：

```bash
python3 tools/skill_writer.py --action refresh-card --slug lin --base-dir ./relationships
```

## 验证

```bash
python3 -m unittest discover -s tests -v
```
