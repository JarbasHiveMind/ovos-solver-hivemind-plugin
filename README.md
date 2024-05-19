# HiveMind solver

exposes a hivemind connection as a solver plugin

use cases:
- allow your OVOS device to get responses from HiveMind, via dedicated skill or pipeline (TODO - companion integrations)
- expose HiveMind to any OpenAI compatible UI, via [ovos-persona-server](https://github.com/OpenVoiceOS/ovos-persona-server)
- Integrate HiveMind/OVOS into a [MOS (Mixture Of Solvers)](https://github.com/TigreGotico/ovos-MoS)

## Usage

```python
from ovos_hivemind_solver import HiveMindSolver

cfg = {
    "hivemind": 
       {"key": "XXX",
        "password": "XXX",
        "host": "0.0.0.0",
        "port": 5678
       }
}
bot = HiveMindSolver(config=cfg) # will connect to HM here
print(bot.spoken_answer("what is th speed of light?"))
```