# calvin.py

class CalvinPromethean:
    def create_metadata(self, nft_type, payload):
        return {
            "type": nft_type,
            "payload": payload,
            "serial": self.generate_serial()
        }

    def generate_serial(self):
        # placeholder
        return "CS-" + "000001"