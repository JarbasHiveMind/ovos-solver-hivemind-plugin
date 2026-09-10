"""Unit tests for forwarding a caller-declared session onto the HiveMind
utterance.

HIVEMIND-BRIDGE-1 §4: "a client that varies its declared session (a bridge
multiplexing several end-user conversations over one connection, or a peer
re-declaring its session) maps each declared name to its own Layer-1
session, never collapsing them into one." A bridge passes the session it is
speaking for via ``context["session"]``; that session must travel on the
emitted ``recognizer_loop:utterance`` message so the hub does not collapse
every caller onto the connection's default session.
"""
from unittest.mock import MagicMock

from ovos_hivemind_solver import HiveMindSolver


def _new_solver_with_mock_hm():
    solver = HiveMindSolver(config={})
    solver.hm = MagicMock()
    # avoid blocking on the response event
    solver._response.set()
    return solver


def test_get_spoken_answer_forwards_declared_session():
    solver = _new_solver_with_mock_hm()

    solver.get_spoken_answer(
        "hello",
        context={"session": {"session_id": "matrix-!room:x", "lang": "en-US"}},
    )

    assert solver.hm.emit_mycroft.called
    (sent_msg,), _ = solver.hm.emit_mycroft.call_args
    assert sent_msg.context["session"]["session_id"] == "matrix-!room:x"
    assert sent_msg.context["session"]["lang"] == "en-US"


def test_get_spoken_answer_without_context_carries_no_session():
    solver = _new_solver_with_mock_hm()

    solver.get_spoken_answer("hello")

    assert solver.hm.emit_mycroft.called
    (sent_msg,), _ = solver.hm.emit_mycroft.call_args
    assert "session" not in sent_msg.context


def test_get_spoken_answer_declared_session_without_lang_falls_back():
    solver = _new_solver_with_mock_hm()
    solver.config["lang"] = "pt-pt"

    solver.get_spoken_answer(
        "hello",
        context={"session": {"session_id": "matrix-!r:x"}},
    )

    assert solver.hm.emit_mycroft.called
    (sent_msg,), _ = solver.hm.emit_mycroft.call_args
    assert sent_msg.data["lang"] == "pt-pt"
    assert sent_msg.context["session"]["session_id"] == "matrix-!r:x"


def test_get_spoken_answer_declared_session_lang_still_wins():
    solver = _new_solver_with_mock_hm()
    solver.config["lang"] = "pt-pt"

    solver.get_spoken_answer(
        "hello",
        context={"session": {"session_id": "matrix-!r:x", "lang": "en-US"}},
    )

    assert solver.hm.emit_mycroft.called
    (sent_msg,), _ = solver.hm.emit_mycroft.call_args
    assert sent_msg.data["lang"] == "en-US"
    assert sent_msg.context["session"]["session_id"] == "matrix-!r:x"
