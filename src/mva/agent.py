"""A small tool-using Claude loop. One system prompt, one user message, a few tool turns."""

from __future__ import annotations

import json
import re

import anthropic

from mva import config, tools


def _client() -> anthropic.Anthropic:
    return anthropic.Anthropic()  # reads ANTHROPIC_API_KEY


def extract_json(text: str):
    """Pull the last ```json block (or the whole text) out of a model reply."""
    blocks = re.findall(r"```json\s*(.*?)```", text, re.S)
    return json.loads(blocks[-1] if blocks else text)


def run(system: str, user: str, use_tools: bool = True, client=None, max_turns: int | None = None) -> str:
    """Run the loop and return the model's final text."""
    client = client or _client()
    messages = [{"role": "user", "content": user}]
    kwargs = {"model": config.MODEL, "max_tokens": 4096, "system": system}
    if use_tools:
        kwargs["tools"] = tools.schemas()
    for _ in range(max_turns or config.MAX_TURNS):
        resp = client.messages.create(messages=messages, **kwargs)
        messages.append({"role": "assistant", "content": resp.content})
        if resp.stop_reason != "tool_use":
            return "".join(b.text for b in resp.content if b.type == "text")
        results = [{"type": "tool_result", "tool_use_id": b.id,
                    "content": json.dumps(tools.call(b.name, b.input))[:12000]}
                   for b in resp.content if b.type == "tool_use"]
        messages.append({"role": "user", "content": results})
    # out of turns: ask for the answer with no more tool calls
    messages.append({"role": "user", "content": "Stop using tools and give your final answer now."})
    kwargs.pop("tools", None)
    resp = client.messages.create(messages=messages, **kwargs)
    return "".join(b.text for b in resp.content if b.type == "text")
