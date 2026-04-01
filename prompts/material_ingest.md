# 资料导入规则

支持：

- 聊天记录
- 聊天截图
- 文档
- 社交软件聊天导出
- 用户补充描述

导入后统一归档到：

```text
relationships/{slug}/knowledge/{kind}/
```

如果是社交软件聊天导出，优先用：

```bash
python3 tools/social_chat_import.py \
  --input ./exports/chat.json \
  --platform telegram \
  --output ./relationships/{slug}/knowledge/messages/social-chat.txt
```
