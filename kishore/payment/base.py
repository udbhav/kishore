class BaseBackend(object):
    human_name = "Payment method"
    priority = 1

    def __init__(self, order):
        self.order = order
