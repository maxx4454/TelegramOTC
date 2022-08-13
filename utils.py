class Utils:

    # check if busd amount is ok else return None
    @staticmethod
    def input_int(msg):
        return int(msg) if msg.isdigit() else None

    # check if wallet address is ok else return None
    @staticmethod
    def input_address(msg):
        flag = True
        if len(msg) != 42:
            flag = False
        for c in msg:
            if not c.isalpha() or not c.isdigit():
                flag = False
                break
        if flag:
            return msg
        else:
            return None

