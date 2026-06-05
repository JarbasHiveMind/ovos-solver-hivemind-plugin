# Solver Integration

## What is an OVOS solver?

An OVOS solver plugin (`QuestionSolver`) provides a `get_spoken_answer(query, context)`
method. The OVOS framework calls it when trying to answer a question that local skills
cannot handle. Solvers are composable: a persona or a Mixture-of-Solvers (MoS) chains
multiple solvers and returns the first non-empty answer.

`HiveMindSolver` implements this interface by forwarding the query to a remote
HiveMind hub and collecting the hub's spoken responses.

## Request flow

```
caller (persona, MoS, app)
    |
    | get_spoken_answer("what is the speed of light?")
    v
HiveMindSolver
    |
    | emit recognizer_loop:utterance to hub
    v
HiveMind hub (hivemind-core + agent)
    |
    | skill or agent handles the query
    | emits speak messages
    v
HiveMindSolver._receive_answer()   <-- collects speak messages
HiveMindSolver._end_of_response()  <-- waits for ovos.utterance.handled
    |
    | returns joined speak messages as the answer string
    v
caller receives answer
```

## Timeout and extension

`get_spoken_answer` waits up to `timeout` seconds (default: 5) for the first response.
If a `speak` message arrives before the timeout, the solver extends the wait by another
5 seconds to collect follow-on sentences. The wait resets each time a new `speak`
arrives, and terminates when `ovos.utterance.handled` fires. Multiple `speak` messages
are joined with `"\n"`.

## Re-using an existing connection

If your application already manages a `HiveMessageBusClient`, pass it via `bind`:

```python
from hivemind_bus_client import HiveMessageBusClient
from ovos_hivemind_solver import HiveMindSolver

hm = HiveMessageBusClient(useragent="my-app")
hm.connect()

solver = HiveMindSolver()
solver.bind(hm)
print(solver.spoken_answer("what time is it?"))
```

This avoids opening a second WebSocket connection to the hub.

## Entry point

```
group: neon.plugin.solver
name:  ovos-solver-hivemind-plugin
class: ovos_hivemind_solver.HiveMindSolver
```

The `neon.plugin.solver` group is the standard solver entry point shared across OVOS
and compatible frameworks.
