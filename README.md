# ovos-solver-hivemind-plugin

Exposes a [HiveMind](https://jarbashivemind.github.io/HiveMind-community-docs/)
connection as an [OVOS solver plugin](https://openvoiceos.github.io/ovos-technical-manual/solvers/).

A solver plugin is a Q&A backend: given a question, return a spoken answer. This
plugin sends the question to a remote HiveMind hub, waits for the hub's `speak`
responses, and returns them as the answer. Any application that uses OVOS solvers can
use a HiveMind hub as its answering backend.

**Use cases:**
- Route questions from an app to a remote OVOS/HiveMind hub.
- Expose HiveMind to any OpenAI-compatible UI via
  [ovos-persona-server](https://github.com/OpenVoiceOS/ovos-persona-server).
- Integrate HiveMind/OVOS as one solver in a
  [Mixture of Solvers (MoS)](https://github.com/TigreGotico/ovos-MoS).

## Install

```bash
pip install ovos-solver-hivemind-plugin
```

## Quickstart

### 1. Register a client on the HiveMind hub

On the machine running `hivemind-core`:

```bash
hivemind-core add-client
# note the Access Key and Password
```

### 2. Set the identity on the client device

```bash
hivemind-client set-identity \
  --key <access_key> \
  --password <password> \
  --host <hub_ip> --port 5678 --siteid solver
```

Verify:

```bash
hivemind-client test-identity
# should print: == Identity successfully connected to HiveMind!
```

### 3. Use the solver

```python
from ovos_hivemind_solver import HiveMindSolver

solver = HiveMindSolver(config={"autoconnect": True})
print(solver.spoken_answer("what is the speed of light?"))
```

Or connect manually:

```python
solver = HiveMindSolver()
solver.connect()   # uses the identity file
print(solver.spoken_answer("what is the capital of France?"))
```

## Configuration

| Key           | Type   | Default                    | Description |
|---------------|--------|----------------------------|-------------|
| `autoconnect` | bool   | `false`                    | Connect to HiveMind automatically at construction time. |
| `useragent`   | string | `"ovos-hivemind-solver"`   | User-agent string sent to the hub. |
| `site_id`     | string | value from identity file   | Site ID for the HiveMind connection. |
| `lang`        | string | `"en-us"`                  | Default language when none is in context. |

Connection credentials (host, port, key, password) come from the identity file set
with `hivemind-client set-identity`. They cannot be passed inline.

## Using with ovos-persona

Add it as a solver in a persona JSON file:

```json
{
  "name": "HiveMind",
  "solvers": [
    {
      "module": "ovos-solver-hivemind-plugin",
      "ovos-solver-hivemind-plugin": {
        "autoconnect": true
      }
    }
  ]
}
```

## Using with ovos-persona-server

Start `ovos-persona-server` with a persona that includes this solver. Any
OpenAI-compatible client can then query HiveMind via the persona server's REST API.

## Documentation

- [`docs/solver_integration.md`](docs/solver_integration.md) — how the solver
  integrates with the OVOS solver framework.
- [`docs/configuration.md`](docs/configuration.md) — full configuration reference.

## Credits

This work was sponsored by VisioLab, part of
[Royal Dutch Visio](https://visio.org/) — the research and education center for
assistive technology for blind and visually impaired people.

## License

Apache 2.0.
