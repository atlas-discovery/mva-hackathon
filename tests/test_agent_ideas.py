from types import SimpleNamespace as NS

from mva import agent, ideas, levers, tools


class FakeClient:
    """Returns one tool call, then a final JSON answer."""

    def __init__(self, final_text):
        self.final = final_text
        self.calls = 0
        self.messages = self

    def create(self, **kw):
        self.calls += 1
        if self.calls == 1 and kw.get("tools"):
            blk = NS(type="tool_use", id="t1", name="pubmed_search", input={"query": "x"})
            return NS(stop_reason="tool_use", content=[blk])
        return NS(stop_reason="end_turn", content=[NS(type="text", text=self.final)])


def test_extract_json_prefers_last_block():
    assert agent.extract_json('a ```json\n[1]``` b ```json\n[2]```') == [2]


def test_agent_runs_tool_then_answers(monkeypatch):
    monkeypatch.setitem(tools.TOOLS, "pubmed_search", (lambda query: {"total": 3}, "d", {}))
    c = FakeClient("done")
    assert agent.run("sys", "usr", client=c) == "done" and c.calls == 2


def test_unknown_tool_and_tool_error_are_returned_not_raised():
    assert "unknown tool" in tools.call("nope", {})["error"]
    assert "error" in tools.call("pubmed_search", {"bad_arg": 1})


def test_levers_and_ideas_pipeline(monkeypatch):
    lv = levers.propose({"variants": []}, client=FakeClient('```json\n[{"name": "L1"}]```'))
    assert lv == [{"name": "L1"}]
    monkeypatch.setattr(tools, "call", lambda n, a: {"max_phase": 4, "n_applications": 2, "total": 7, "mechanisms": ["m"]})
    rows = ideas.propose(lv, "dis", "GENE", client=FakeClient('```json\n[{"drug": "drugx", "why": "w", "caveat": "c"}]```'))
    assert rows[0]["checks"]["chembl_max_phase"] == 4
    assert "| L1 | drugx | yes | 2 | 7 | 7 | w | c |" in ideas.to_markdown(rows)


def test_refusal_raises_clear_error():
    import pytest

    class Refuser:
        messages = None

        def __init__(self):
            self.messages = self

        def create(self, **kw):
            return NS(stop_reason="refusal", content=[], stop_details=NS(category="bio"))

    with pytest.raises(agent.RefusalError, match="bio"):
        agent.run("s", "u", client=Refuser())
