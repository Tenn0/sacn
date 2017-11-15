from ..messages.data_packet import DataPacket


class Output:
    """
    This class is a compact representation of an output with all relevant information
    """
    def __init__(self, packet: DataPacket, last_time_send: int = 0, destination: str = "127.0.0.1",
                 multicast: bool = False, ttl: int = 8):
        self._packet: DataPacket = packet
        self._last_time_send: int = last_time_send
        self.destination: str = destination
        self.multicast: bool = multicast
        self.ttl: int = ttl
        self._changed: bool = False

    @property
    def dmx_data(self) -> tuple:
        return self._packet.dmxData
    @dmx_data.setter
    def dmx_data(self, dmx_data: tuple):
        self._packet.dmxData = dmx_data
        self._changed = True

    @property
    def priority(self) -> int:
        return self._packet.priority
    @priority.setter
    def priority(self, priority: int):
        self._packet.priority = priority

    @property
    def preview_data(self) -> bool:
        return self._packet.option_PreviewData
    @preview_data.setter
    def preview_data(self, preview_data: bool):
        self._packet.option_PreviewData = preview_data

#
# class customList(list):
#     def __init__(self, args):
#         super().__init__(args)
#         self.callbacks: list = []
#
#     def __setitem__(self, key, value):
#         super().__setitem__(key, value)
#         for callback in self.callbacks:
#             callback()