# Configuration

## Standalone / programmatic

```python
from ovos_hivemind_solver import HiveMindSolver

solver = HiveMindSolver(config={
    "autoconnect": True,
    "useragent": "my-app",
    "lang": "en-us"
})
```

## Via ovos-persona

```json
{
  "name": "HiveMind",
  "solvers": [
    {
      "module": "ovos-solver-hivemind-plugin",
      "ovos-solver-hivemind-plugin": {
        "autoconnect": true,
        "lang": "en-us"
      }
    }
  ]
}
```

## Key reference

| Key           | Type   | Default                  | Description |
|---------------|--------|--------------------------|-------------|
| `autoconnect` | bool   | `false`                  | Connect automatically at construction time. If `false`, call `solver.connect()` before the first query. |
| `useragent`   | string | `"ovos-hivemind-solver"` | User-agent string sent to the hub in the handshake. |
| `site_id`     | string | from identity file       | Site ID for the connection. Overrides the value in the identity file. |
| `lang`        | string | `"en-us"`                | Default language when no `lang` is present in the query context. |

## Connection identity

Host, port, access key, and password are read from the identity file at
`~/.config/hivemind/_identity.json`. Set it with:

```bash
hivemind-client set-identity \
  --key <access_key> \
  --password <password> \
  --host <hub_ip> --port 5678 --siteid solver
```

There is no way to pass credentials inline — the identity file is the only source.
