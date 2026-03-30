# 资料导入规则

支持：

- 聊天记录
- 聊天截图
- 文档
- 飞书聊天记录
- 用户补充描述

导入后统一归档到：

```text
relationships/{slug}/knowledge/{kind}/
```

如果是飞书聊天记录，优先用：

```bash
python3 tools/feishu_chat_import.py \
  --chat-id "oc_xxx" \
  --output ./relationships/{slug}/knowledge/messages/feishu-chat.txt
```
