from base import BaseBackend

class PaypalDigitalBackend(BaseBackend):
    human_name = 'Paypal'

    @property
    def valid(self):
        return not self.order.shippable
