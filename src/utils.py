class Utils:

    # check if busd amount is ok else return None
    @staticmethod
    def input_int(msg):
        return int(msg) if msg.isdigit() else None

    # check if wallet address is ok else return None
    @staticmethod
    def input_address(msg):
        if len(msg) != 42:
            return False
        if msg[:2] != '0x':
            return False
        for c in msg:
            if not c.isalpha() or not c.isdigit():
                return False
        return True

    @classmethod
    def print_best_offers(cls, best_offers):
        (best_buy_orders, best_sell_orders) = best_offers
        s = ""
        for item in best_buy_orders:
            s += item

        for item in best_sell_orders:
            s += item

        return s

    @classmethod
    def generate_creds_string(cls, creds, deal_amount):
        creds_left = creds[deal_amount - 1:]

        s = ""
        for cred in creds_left:
            s += cred
            s += "\n"
        return s
