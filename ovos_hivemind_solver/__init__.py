from hivemind_bus_client import HiveMessageBusClient
from ovos_bus_client.message import Message
from ovos_plugin_manager.templates.solvers import QuestionSolver
from ovos_utils.log import LOG
from threading import Event


class HiveMindSolver(QuestionSolver):
    def __init__(self, config=None):
        config = config or {}
        super().__init__(config, enable_tx=False, priority = 70)
        self.hm = None
        self._response = Event()
        self._responses = []
        if self.config.get("autoconnect"):
            self.connect()

    def bind(self, hm: HiveMessageBusClient):
        """if you want to re-use a open connection"""
        self.hm = hm

    def connect(self):
        """assume identity set beforehand, eg via `hivemind-client set-identity`
        """
        self.hm = HiveMessageBusClient(useragent="ovos-hivemind-solver")
        self.hm.connect()
        self.hm.on_mycroft("speak", self._receive_answer)
        self.hm.on_mycroft("ovos.utterance.handled", self._end_of_response)

    def _end_of_response(self, message):
        self._response.set()

    def _receive_answer(self, message):
        utt = message.data["utterance"]
        self._responses.append(utt)

    # abstract Solver methods
    def get_data(self, query, context=None):
        return {"answer": self.get_spoken_answer(query, context)}

    def get_spoken_answer(self, query, context=None, timeout=10):
        if self.hm is None:
            LOG.error("not connected to HiveMind")
            return
        self._response.clear()
        self._responses = []

        context = context or {}
        if "session" in context:
            lang = context["session"]["lang"]
        else:
            lang = context.get("lang") or self.config.get("lang", "en-us")
        mycroft_msg = Message("recognizer_loop:utterance",
                              {"utterances": [query], "lang": lang})
        self.hm.emit_mycroft(mycroft_msg)
        self._response.wait(timeout=timeout)
        if self._responses:
            # merge multiple speak messages into one
            return "\n".join(self._responses)
        return None  # let next solver attempt


if __name__ == "__main__":
    cfg = {
        "autoconnect": True
    }
    bot = HiveMindSolver(config=cfg)
    print(bot.spoken_answer("what is the speed of light?"))
