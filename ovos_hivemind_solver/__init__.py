from hivemind_bus_client import HiveMessageBusClient, HiveMessage, \
    HiveMessageType
from ovos_bus_client.message import Message
from ovos_plugin_manager.templates.solvers import QuestionSolver


class HiveMindSolver(QuestionSolver):
    enable_tx = False
    priority = 70

    def __init__(self, config=None):
        config = config or {}
        super().__init__(config)
        self.hm = None
        self.connect()

    def connect(self):
        hm_settings = self.config.get("hivemind", {})
        key = hm_settings["key"]
        pswd = hm_settings["password"]
        host = hm_settings["host"]
        port = hm_settings.get("port", 5678)
        self.hm = HiveMessageBusClient(key=key, password=pswd,
                                       host=host, port=port,
                                       useragent="ovos-hivemind-solver")
        self.hm.run_in_thread()

    # abstract Solver methods
    def get_data(self, query, context=None):
        return {"answer": self.get_spoken_answer(query, context)}

    def get_spoken_answer(self, query, context=None):
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
        "hivemind": 
           {"key": "XXX",
            "password": "XXX",
            "host": "0.0.0.0",
            "port": 5678
           }
    }
    bot = HiveMindSolver(config=cfg)
    print(bot.spoken_answer("what is th speed of light?"))
