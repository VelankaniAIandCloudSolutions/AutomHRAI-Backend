from channels.generic.websocket import WebsocketConsumer
import json
from asgiref.sync import async_to_sync

class CheckInOutConsumer(WebsocketConsumer):
    def connect(self):
        self.accept()
        self.group_name = 'check_in_out_create_group'
        async_to_sync(self.channel_layer.group_add)(
            self.group_name,
            self.channel_name
        )

    def disconnect(self, close_code):
        async_to_sync(self.channel_layer.group_discard)(
            self.group_name,
            self.channel_name
        )

    def receive(self, text_data):
        pass

    def send_check_in_out_data(self, event):
        check_in_out_data = event['check_in_out_data']
        self.send(text_data=json.dumps({
            'check_in_out_data': check_in_out_data,
        }))
