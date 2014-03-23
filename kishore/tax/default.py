from decimal import Decimal

from kishore import settings as kishore_settings

class KishoreTax(object):
    def __init__(self, order):
        self.tax_state = getattr(kishore_settings, "KISHORE_SALES_TAX_STATE", None)
        self.tax_country = getattr(kishore_settings, "KISHORE_SALES_TAX_COUNTRY", None)

        if not self.tax_state or not self.tax_country:
            raise Exception("Set KISHORE_SALES_TAX_STATE and KISHORE_SALES_TAX_COUNTRY")

        self.tax_rate = kishore_settings.KISHORE_TAX_RATES.get(self.tax_state)

        if not self.tax_rate:
            raise Exception("Error determining tax rate")

        self.order = order

    def calculate_tax(self):
        address = self.order.shipping_address
        if self.order.shippable and address:
            if address.country.lower() == self.tax_country.lower() and address.state.lower() == self.tax_state.lower():
                return Decimal(self.tax_rate) * (self.order.shipping_total + self.order.subtotal)

        return 0
