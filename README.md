# HiveMind solver

exposes a [HiveMind](https://jarbashivemind.github.io/HiveMind-community-docs/) connection as a [OVOS solver plugin](https://openvoiceos.github.io/ovos-technical-manual/solvers/)

use cases:
- allow your OVOS device to get responses from HiveMind, via [companion fallback skill](https://github.com/JarbasHiveMind/ovos-skill-fallback-hivemind), ie, ask a smarter OVOS install to handle the utterance
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
