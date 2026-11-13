"""Unit tests for HiveMindSolver.connect() websocket keepalive defaults.

Hub implementations commonly drop idle clients ~15s after the last pong.
Current hivemind_bus_client (>=1.0.13a1) defaults keepalive ON at 25s/10s,
which is too slack against that ~15s drop window for a consumer with
multi-second gaps between queries (e.g. an LLM judge deliberating between
rounds); older stable clients (0.4.x) have no keepalive kwargs at all.
`connect()` must therefore pass explicit tighter kwargs (default 10s
interval / 5s timeout, config-overridable), and must fall back to the bare
constructor if an older installed `hivemind_bus_client` does not accept
those kwargs.

This is the start of a unit test directory for this repo; previously only
`tests/test_e2e.py` existed.
"""
from unittest.mock import MagicMock, patch

from ovos_hivemind_solver import HiveMindSolver


def _new_unconnected_solver(config=None):
    """A HiveMindSolver instance without triggering autoconnect."""
    return HiveMindSolver(config=config or {})


@patch("ovos_hivemind_solver.HiveMessageBusClient")
def test_connect_passes_default_keepalive_kwargs(mock_client_cls):
    """connect() must default to keepalive ON (10s/5s) so idle sessions
    survive the hub's ~15s pong-drop window."""
    mock_client_cls.return_value = MagicMock()

    solver = _new_unconnected_solver()
    solver.connect()

    assert mock_client_cls.called
    _, kwargs = mock_client_cls.call_args
    assert kwargs.get("websocket_ping_interval") == 10
    assert kwargs.get("websocket_ping_timeout") == 5


@patch("ovos_hivemind_solver.HiveMessageBusClient")
def test_connect_honors_config_overrides(mock_client_cls):
    """Explicit config values are passed through verbatim to the client
    (note: the client resolves None back to its own defaults; 0 disables)."""
    mock_client_cls.return_value = MagicMock()

    solver = _new_unconnected_solver(config={
        "websocket_ping_interval": None,
        "websocket_ping_timeout": None,
    })
    solver.connect()

    _, kwargs = mock_client_cls.call_args
    assert kwargs.get("websocket_ping_interval") is None
    assert kwargs.get("websocket_ping_timeout") is None


@patch("ovos_hivemind_solver.HiveMessageBusClient")
def test_connect_falls_back_on_old_client(mock_client_cls):
    """If the installed hivemind_bus_client is too old to accept the
    keepalive kwargs (raises TypeError), connect() must retry with the bare
    constructor instead of crashing."""
    bare_instance = MagicMock()

    def _side_effect(*args, **kwargs):
        if "websocket_ping_interval" in kwargs or "websocket_ping_timeout" in kwargs:
            raise TypeError("unexpected keyword argument 'websocket_ping_interval'")
        return bare_instance

    mock_client_cls.side_effect = _side_effect

    solver = _new_unconnected_solver()
    solver.connect()

    assert mock_client_cls.call_count == 2
    assert solver.hm is bare_instance
    # second (successful) call must not carry the unsupported kwargs
    _, kwargs = mock_client_cls.call_args
    assert "websocket_ping_interval" not in kwargs
    assert "websocket_ping_timeout" not in kwargs


@patch("ovos_hivemind_solver.HiveMessageBusClient")
def test_connect_propagates_bad_value_typeerror(mock_client_cls):
    """A TypeError caused by a bad user-supplied config value (not by an old
    client signature) must propagate — the fallback must not silently hide
    operator misconfiguration behind a keepalive-less connect."""
    import pytest

    mock_client_cls.side_effect = TypeError(
        "'<' not supported between instances of 'str' and 'int'")

    solver = _new_unconnected_solver(config={
        "websocket_ping_interval": "10",  # wrong type
    })
    with pytest.raises(TypeError):
        solver.connect()

    # no bare-constructor retry happened
    assert mock_client_cls.call_count == 1
