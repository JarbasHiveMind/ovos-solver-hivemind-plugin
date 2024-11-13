# HiveMind solver

exposes a hivemind connection as a solver plugin

use cases:
- allow your apps to get responses from a remote HiveMind
- expose HiveMind to any OpenAI compatible UI, via [ovos-persona-server](https://github.com/OpenVoiceOS/ovos-persona-server)
- Integrate HiveMind/OVOS into a [MOS (Mixture Of Solvers)](https://github.com/TigreGotico/ovos-MoS)

## Install

`pip install ovos-solver-hivemind-plugin`

## Setup

You need to register the solver in the HiveMind server
```bash
$ hivemind-core add-client
Credentials added to database!

Node ID: 2
Friendly Name: HiveMind-Node-2
Access Key: 5a9e580a2773a262cbb23fe9759881ff
Password: 9b247ca66c7cd2b6388ad49ca504279d
Encryption Key: 4185240103de0770
WARNING: Encryption Key is deprecated, only use if your client does not support password
```

And then set the identity file in the satellite device (where the solver will run)
```bash
$ hivemind-client set-identity --key 5a9e580a2773a262cbb23fe9759881ff --password 9b247ca66c7cd2b6388ad49ca504279d --host 0.0.0.0 --port 5678 --siteid test
identity saved: /home/miro/.config/hivemind/_identity.json
```

check the created identity file if you like
```bash
$ cat ~/.config/hivemind/_identity.json
{
    "password": "9b247ca66c7cd2b6388ad49ca504279d",
    "access_key": "5a9e580a2773a262cbb23fe9759881ff",
    "site_id": "test",
    "default_port": 5678,
    "default_master": "ws://0.0.0.0"
}
```

test that a connection is possible using the identity file
```bash
$ hivemind-client test-identity
(...)
2024-05-20 21:22:28.003 - OVOS - hivemind_bus_client.client:__init__:112 - INFO - Session ID: 34d75c93-4e65-4ea9-b5f4-87169dcfda01
(...)
== Identity successfully connected to HiveMind!
```

## Usage

For usage with any solver framework, such as persona, use `"ovos-solver-hivemind-plugin"` for the solver id

Standalone usage

```python
from ovos_hivemind_solver import HiveMindSolver

bot = HiveMindSolver()
bot.connect()  # connection info from identity file
print(bot.spoken_answer("what is the speed of light?"))
```

## Credits

![image](https://github.com/user-attachments/assets/809588a2-32a2-406c-98c0-f88bf7753cb4)

> This work was sponsored by VisioLab, part of [Royal Dutch Visio](https://visio.org/), is the test, education, and research center in the field of (innovative) assistive technology for blind and visually impaired people and professionals. We explore (new) technological developments such as Voice, VR and AI and make the knowledge and expertise we gain available to everyone.
