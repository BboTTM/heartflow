#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import sys
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime
from pathlib import Path


AUTH_URL = "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal"
MESSAGES_URL = "https://open.feishu.cn/open-apis/im/v1/messages"


def http_json(url: str, method: str = "GET", headers: dict | None = None, payload: dict | None = None) -> dict:
    data = None
    request_headers = {"Content-Type": "application/json; charset=utf-8"}
    if headers:
        request_headers.update(headers)
    if payload is not None:
        data = json.dumps(payload).encode("utf-8")
    request = urllib.request.Request(url, data=data, headers=request_headers, method=method)
    with urllib.request.urlopen(request) as response:
        return json.loads(response.read().decode("utf-8"))


def fetch_tenant_access_token(app_id: str, app_secret: str) -> str:
    response = http_json(
        AUTH_URL,
        method="POST",
        payload={"app_id": app_id, "app_secret": app_secret},
    )
    token = response.get("tenant_access_token")
    if not token:
        raise RuntimeError(f"failed to fetch tenant_access_token: {response}")
    return token


def parse_message_content(message_type: str, content: str) -> str:
    try:
        payload = json.loads(content)
    except json.JSONDecodeError:
        return content

    if message_type == "text":
        return payload.get("text", "")
    if message_type == "post":
        pieces: list[str] = []
        for locale in payload.values():
            for block in locale.get("content", []):
                for item in block:
                    if item.get("tag") == "text":
                        pieces.append(item.get("text", ""))
        return "".join(pieces)
    if message_type == "image":
        return "[image]"
    if message_type == "file":
        return "[file]"
    return json.dumps(payload, ensure_ascii=False)


def normalize_message(item: dict) -> dict:
    body = item.get("body", {})
    sender = item.get("sender", {})
    create_time = item.get("create_time", "")
    timestamp = ""
    if create_time:
        try:
            timestamp = datetime.fromtimestamp(int(create_time) / 1000).isoformat(timespec="seconds")
        except ValueError:
            timestamp = create_time
    return {
        "message_id": item.get("message_id", ""),
        "create_time": create_time,
        "timestamp": timestamp,
        "message_type": body.get("message_type", "unknown"),
        "sender_id": sender.get("id", ""),
        "sender_id_type": sender.get("id_type", ""),
        "chat_id": item.get("chat_id", ""),
        "text": parse_message_content(body.get("message_type", "unknown"), body.get("content", "")),
    }


def fetch_messages(token: str, chat_id: str, page_size: int = 50, max_pages: int = 10, user_id: str | None = None) -> list[dict]:
    items: list[dict] = []
    page_token = ""
    for _ in range(max_pages):
        query = {
            "container_id_type": "chat",
            "container_id": chat_id,
            "sort_type": "ByCreateTimeAsc",
            "page_size": str(page_size),
        }
        if page_token:
            query["page_token"] = page_token
        url = MESSAGES_URL + "?" + urllib.parse.urlencode(query)
        response = http_json(url, headers={"Authorization": f"Bearer {token}"})
        data = response.get("data", {})
        for raw in data.get("items", []):
            normalized = normalize_message(raw)
            if user_id and normalized["sender_id"] != user_id:
                continue
            items.append(normalized)
        if not data.get("has_more"):
            break
        page_token = data.get("page_token", "")
        if not page_token:
            break
    return items


def render_messages(messages: list[dict]) -> str:
    lines = []
    for message in messages:
        time = message.get("timestamp") or message.get("create_time", "")
        sender = message.get("sender_id", "unknown")
        text = message.get("text", "").strip() or f"[{message.get('message_type', 'unknown')}]"
        lines.append(f"[{time}] {sender}: {text}")
    return "\n".join(lines).strip() + ("\n" if lines else "")


def parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Import Feishu chat history through the official OpenAPI.")
    p.add_argument("--chat-id", required=True, help="Feishu chat id, usually starts with oc_.")
    p.add_argument("--output", required=True, help="Output text file path.")
    p.add_argument("--app-id", default=os.getenv("FEISHU_APP_ID", ""))
    p.add_argument("--app-secret", default=os.getenv("FEISHU_APP_SECRET", ""))
    p.add_argument("--page-size", type=int, default=50)
    p.add_argument("--max-pages", type=int, default=10)
    p.add_argument("--user-id", help="Optional sender id filter.")
    return p


def main() -> int:
    args = parser().parse_args()
    if not args.app_id or not args.app_secret:
        print("error: missing --app-id/--app-secret or FEISHU_APP_ID/FEISHU_APP_SECRET", file=sys.stderr)
        return 1
    try:
        token = fetch_tenant_access_token(args.app_id, args.app_secret)
        messages = fetch_messages(
            token=token,
            chat_id=args.chat_id,
            page_size=args.page_size,
            max_pages=args.max_pages,
            user_id=args.user_id,
        )
        output_path = Path(args.output)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(render_messages(messages), encoding="utf-8")
        print(output_path)
        return 0
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace")
        print(f"error: http {exc.code} {body}", file=sys.stderr)
        return 1
    except Exception as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
