#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import json
import re
import sys
from pathlib import Path


TEXT_KEYS = ("text", "content", "message", "body", "msg")
SENDER_KEYS = ("sender", "sender_name", "author", "author_name", "name", "user", "username", "from")
TIME_KEYS = ("timestamp", "time", "datetime", "date", "created_at", "sent_at")

TXT_LINE_PATTERNS = [
    re.compile(r"^\[(?P<time>[^\]]+)\]\s*(?P<sender>[^:：]+)[:：]\s*(?P<text>.+)$"),
    re.compile(r"^(?P<time>\d{4}[-/]\d{1,2}[-/]\d{1,2}\s+\d{1,2}:\d{2}(?::\d{2})?)\s+(?P<sender>[^:：]+)[:：]\s*(?P<text>.+)$"),
    re.compile(r"^(?P<sender>[^:：]+)[:：]\s*(?P<text>.+)$"),
]


def clean_text(value: object) -> str:
    if value is None:
        return ""
    text = str(value).strip()
    return re.sub(r"\s+", " ", text)


def pick_first(data: dict, keys: tuple[str, ...]) -> str:
    for key in keys:
        if key in data and clean_text(data[key]):
            return clean_text(data[key])
    return ""


def normalize_record(item: dict, fallback_sender: str = "unknown") -> dict | None:
    sender = pick_first(item, SENDER_KEYS) or fallback_sender
    text = pick_first(item, TEXT_KEYS)
    timestamp = pick_first(item, TIME_KEYS)
    if not text:
        return None
    return {
        "timestamp": timestamp,
        "sender": sender,
        "text": text,
    }


def parse_txt(text: str, fallback_sender: str = "unknown") -> list[dict]:
    messages: list[dict] = []
    for raw_line in text.splitlines():
        line = raw_line.strip()
        if not line:
            continue
        matched = None
        for pattern in TXT_LINE_PATTERNS:
            m = pattern.match(line)
            if m:
                matched = {
                    "timestamp": clean_text(m.groupdict().get("time", "")),
                    "sender": clean_text(m.groupdict().get("sender", fallback_sender)) or fallback_sender,
                    "text": clean_text(m.groupdict().get("text", "")),
                }
                break
        if matched and matched["text"]:
            messages.append(matched)
        else:
            messages.append({"timestamp": "", "sender": fallback_sender, "text": line})
    return messages


def parse_json_text(text: str, fallback_sender: str = "unknown") -> list[dict]:
    payload = json.loads(text)
    if isinstance(payload, dict):
        if isinstance(payload.get("messages"), list):
            payload = payload["messages"]
        else:
            payload = [payload]
    if not isinstance(payload, list):
        raise ValueError("JSON input must be a message object, a list of message objects, or contain a messages array")
    messages: list[dict] = []
    for item in payload:
        if isinstance(item, dict):
            normalized = normalize_record(item, fallback_sender=fallback_sender)
            if normalized:
                messages.append(normalized)
    return messages


def parse_jsonl_text(text: str, fallback_sender: str = "unknown") -> list[dict]:
    messages: list[dict] = []
    for line in text.splitlines():
        line = line.strip()
        if not line:
            continue
        item = json.loads(line)
        if isinstance(item, dict):
            normalized = normalize_record(item, fallback_sender=fallback_sender)
            if normalized:
                messages.append(normalized)
    return messages


def parse_csv_text(text: str, fallback_sender: str = "unknown") -> list[dict]:
    rows = csv.DictReader(text.splitlines())
    messages: list[dict] = []
    for row in rows:
        normalized = normalize_record(row, fallback_sender=fallback_sender)
        if normalized:
            messages.append(normalized)
    return messages


def detect_format(path: Path, explicit_format: str) -> str:
    if explicit_format != "auto":
        return explicit_format
    suffix = path.suffix.lower()
    if suffix == ".json":
        return "json"
    if suffix == ".jsonl":
        return "jsonl"
    if suffix == ".csv":
        return "csv"
    return "txt"


def parse_input(path: Path, file_format: str, fallback_sender: str = "unknown") -> list[dict]:
    text = path.read_text(encoding="utf-8")
    if file_format == "txt":
        return parse_txt(text, fallback_sender=fallback_sender)
    if file_format == "json":
        return parse_json_text(text, fallback_sender=fallback_sender)
    if file_format == "jsonl":
        return parse_jsonl_text(text, fallback_sender=fallback_sender)
    if file_format == "csv":
        return parse_csv_text(text, fallback_sender=fallback_sender)
    raise ValueError(f"unsupported format: {file_format}")


def render_messages(messages: list[dict], platform: str = "") -> str:
    lines: list[str] = []
    if platform:
        lines.append(f"# platform: {platform}")
    for message in messages:
        timestamp = clean_text(message.get("timestamp", ""))
        sender = clean_text(message.get("sender", "unknown")) or "unknown"
        text = clean_text(message.get("text", ""))
        if timestamp:
            lines.append(f"[{timestamp}] {sender}: {text}")
        else:
            lines.append(f"{sender}: {text}")
    return "\n".join(lines).strip() + ("\n" if lines else "")


def parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        description="Import exported social chat history from txt/json/jsonl/csv into HeartFlow's normalized text format."
    )
    p.add_argument("--input", required=True, help="Exported chat file path.")
    p.add_argument("--output", required=True, help="Normalized text output path.")
    p.add_argument("--format", default="auto", choices=["auto", "txt", "json", "jsonl", "csv"])
    p.add_argument("--platform", default="", help="Optional platform label, e.g. wechat, telegram, whatsapp, qq.")
    p.add_argument("--fallback-sender", default="unknown", help="Sender name used when input lacks sender fields.")
    return p


def main() -> int:
    args = parser().parse_args()
    input_path = Path(args.input)
    if not input_path.exists():
        print(f"error: input not found: {input_path}", file=sys.stderr)
        return 1
    try:
        file_format = detect_format(input_path, args.format)
        messages = parse_input(input_path, file_format, fallback_sender=args.fallback_sender)
        output_path = Path(args.output)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(render_messages(messages, platform=args.platform), encoding="utf-8")
        print(output_path)
        return 0
    except Exception as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
