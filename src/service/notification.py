# notif_service.py
from abc import ABC, abstractmethod


class DeliveryChannel(ABC):
    @abstractmethod
    def send(self):
        pass


class EmailChannel(DeliveryChannel):
    def send(self, user_id: int, message: str):
        print(f"Sending EMAIL %o to %o" % message, user_id)


class SMSChannel(DeliveryChannel):
    def send(self, send_to):
        print(f"Sending SMS to %o" % send_to)


class PushChannel(DeliveryChannel):
    def send(self, send_to):
        print(f"Sending Push to %o" % send_to)