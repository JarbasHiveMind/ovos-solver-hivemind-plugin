"""End-to-end tests for ovos-solver-hivemind-plugin.

The plugin exposes a HiveMind connection as an OVOS *question solver*: given a
query it injects ``recognizer_loop:utterance`` into a HiveMind hub and returns
the hub's ``speak`` responses as the spoken answer.

These tests wire the solver to a **real** ``HiveMindListenerProtocol`` master
through hivescope's in-process topology simulator (no sockets, no servers).
A query driven through the solver therefore travels the genuine HiveMind path:

    solver.get_spoken_answer(query)
        -> emit_mycroft(recognizer_loop:utterance)        # upstream
        -> SatelliteNode.send -> master.hm_protocol.handle_message
        -> master injects on its OVOS agent bus                  (proves arrival)
    a "skill" answers on the master agent bus (speak + handled)
        -> TestAgentProtocol reverse-routes to the satellite peer  # downstream
        -> satellite internal bus -> solver._receive_answer
        -> get_spoken_answer returns the answer text

hivescope is a hard test dependency (declared in the ``test`` extra); these
tests must never be importorskip'd.
"""
from threading import Thread

import pytest
from ovos_bus_client.message import Message
from ovos_utils.fakebus import FakeBus

from hivescope import TopologyBuilder

from ovos_hivemind_solver import HiveMindSolver


class _SatelliteHiveClient:
    """In-process stand-in for ``HiveMessageBusClient``, backed by a hivescope
    ``SatelliteNode``.

    Implements exactly the surface ``HiveMindSolver`` uses:

    * ``emit_mycroft(msg)`` — send an OVOS message upstream to the master
      (the real client wraps it in a ``BUS`` HiveMessage and ships it over the
      websocket; here it routes through the satellite's in-process link).
    * ``on_mycroft(event, fn)`` — register ``fn`` on the satellite's internal
      OVOS bus, which is where the slave protocol re-emits messages the master
      routes downstream (mirrors the real client's ``internal_bus``).
    """

    def __init__(self, satellite):
        self._sat = satellite
        self.session_id = satellite.shim.session_id
        self.site_id = satellite.identity.site_id

    def emit_mycroft(self, message: Message):
        self._sat.send(message)

    def on_mycroft(self, event_name, func):
        self._sat.internal_bus.on(event_name, func)


def _bind_solver(solver: HiveMindSolver, satellite):
    """Bind the solver to an in-process satellite-backed client and register the
    solver's speak/end-of-turn handlers (the work the solver's own ``connect()``
    does; ``bind()`` only swaps the connection in)."""
    client = _SatelliteHiveClient(satellite)
    solver.bind(client)
    client.on_mycroft("speak", solver._receive_answer)
    client.on_mycroft("ovos.utterance.handled", solver._end_of_response)
    return client


def _topology():
    """Single master + one satellite allowed to inject utterances / receive speak."""
    b = TopologyBuilder()
    m = b.add_master("M0")
    b.add_satellite(
        "S0", upstream=m,
        allowed_types=["recognizer_loop:utterance", "speak",
                       "ovos.utterance.handled"],
    )
    return b


def test_solver_loads_via_entry_point():
    """The solver is discoverable through the OVOS ``opm.solver.question`` group
    (NOT the forbidden ``neon.plugin.solver`` group) and the loaded class is
    HiveMindSolver."""
    from ovos_plugin_manager.solvers import find_question_solver_plugins

    plugins = find_question_solver_plugins()
    assert "ovos-solver-hivemind-plugin" in plugins, (
        f"solver not registered under opm.solver.question; found: {list(plugins)}"
    )
    assert plugins["ovos-solver-hivemind-plugin"] is HiveMindSolver


def test_no_neon_entry_point():
    """The plugin must not expose any Neon entry-point group (forbidden org-wide)."""
    from importlib.metadata import entry_points

    neon = entry_points(group="neon.plugin.solver")
    assert "ovos-solver-hivemind-plugin" not in [e.name for e in neon]


def test_query_reaches_master_and_returns_answer():
    """A query driven through the solver reaches a real HiveMind master and the
    master's spoken answer flows back as the solver's answer."""
    b = _topology()
    b.start_all()
    try:
        master = b.get_master("M0")
        sat = b.get_satellite("S0")

        solver = HiveMindSolver()
        _bind_solver(solver, sat)

        # A "skill" on the master side answers the next utterance: when the
        # utterance is injected on the master's agent bus, reply with a speak
        # (routed back to the originating satellite peer) and signal end-of-turn.
        def _skill(injected: Message):
            if injected.msg_type != "recognizer_loop:utterance":
                return
            dest = sat.peer
            master.emit_on_bus(Message(
                "speak",
                {"utterance": "the speed of light is 299792458 m/s"},
                {"destination": [dest], "session": injected.context.get("session", {})},
            ))
            master.emit_on_bus(Message(
                "ovos.utterance.handled",
                {},
                {"destination": [dest], "session": injected.context.get("session", {})},
            ))

        master.agent_protocol.bus.on("recognizer_loop:utterance", _skill)

        answer = solver.get_spoken_answer("what is the speed of light?", timeout=10)

        # The utterance really arrived at the master (genuine HiveMind path).
        master.agent_protocol.assert_injected("recognizer_loop:utterance", count=1)
        # ...and the master's spoken reply came back through the solver.
        assert answer == "the speed of light is 299792458 m/s"
    finally:
        b.stop_all()


def test_get_data_wraps_spoken_answer():
    """get_data returns the spoken answer under the 'answer' key."""
    b = _topology()
    b.start_all()
    try:
        master = b.get_master("M0")
        sat = b.get_satellite("S0")

        solver = HiveMindSolver()
        _bind_solver(solver, sat)

        def _skill(injected: Message):
            if injected.msg_type != "recognizer_loop:utterance":
                return
            dest = sat.peer
            master.emit_on_bus(Message(
                "speak", {"utterance": "Paris"},
                {"destination": [dest], "session": injected.context.get("session", {})},
            ))
            master.emit_on_bus(Message(
                "ovos.utterance.handled", {},
                {"destination": [dest], "session": injected.context.get("session", {})},
            ))

        master.agent_protocol.bus.on("recognizer_loop:utterance", _skill)

        data = solver.get_data("what is the capital of France?")
        assert data["answer"] == "Paris"
    finally:
        b.stop_all()


def test_unconnected_solver_returns_none():
    """With no HiveMind connection bound, the solver yields no answer (and lets
    the next solver in a chain attempt) rather than raising."""
    solver = HiveMindSolver()
    assert solver.hm is None
    assert solver.get_spoken_answer("anything", timeout=1) is None
