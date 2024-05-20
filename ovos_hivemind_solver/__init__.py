from hivemind_bus_client import HiveMessageBusClient, HiveMessage, \
    HiveMessageType
from ovos_bus_client.message import Message
from ovos_plugin_manager.templates.solvers import QuestionSolver
from ovos_utils.log import LOG


class HiveMindSolver(QuestionSolver):
    enable_tx = False
    priority = 70

    def __init__(self, config=None):
        config = config or {}
        super().__init__(config)
        self.hm = None
        if self.config.get("autoconnect"):
            self.connect()

    def bind(self, hm: HiveMessageBusClient):
        """if you want to re-use a open connection"""
        self.hm = hm

    def connect(self):
        """assume identity set beforehand, eg via `hivemind-client set-identity`
        """
        self.hm = HiveMessageBusClient(useragent="ovos-hivemind-solver")
        self.hm.run_in_thread()

    # abstract Solver methods
    def get_data(self, query, context=None):
        return {"answer": self.get_spoken_answer(query, context)}

    def get_spoken_answer(self, query, context=None):
        if self.hm is None:
            LOG.error("not connected to HiveMind")
            return
        context = context or {}
        if "session" in context:
            lang = context["session"]["lang"]
        else:
            lang = context.get("lang") or self.config.get("lang", "en-us")
        mycroft_msg = Message("recognizer_loop:utterance",
                              {"utterances": [query], "lang": lang})
        msg = HiveMessage(HiveMessageType.BUS, mycroft_msg)
        response = self.hm.wait_for_payload_response(
            message=msg,
            reply_type=HiveMessageType.BUS,
            payload_type="speak",
            timeout=20)
        if response:
            return response.payload.data["utterance"]
        return None  # let next solver attempt


if __name__ == "__main__":
    cfg = {
        "autoconnect": True
    }
    bot = HiveMindSolver(config=cfg)
    print(bot.spoken_answer("what is th speed of light?"))
