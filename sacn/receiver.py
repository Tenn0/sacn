import socket
import sys
import threading

from .messages.data_packet import DataPacket, calculate_multicast_addr


class sACNreceiver:
    def __init__(self, bind_address: str = '0.0.0.0', bind_port: int = 5568):
        """
        Make a receiver for sACN data. Do not forget to start and add callbacks for receiving messages!
        :param bind_address: if you are on a Windows system and want to use multicast provide a valid interface
        IP-Address! Otherwise omit.
        :param bind_port: Default: 5568. It is not recommended to change this value!
        Only use when you are know what you are doing!
        """
        # If you bind to a specific interface on the Mac, no multicast data will arrive.
        # If you try to bind to all interfaces on Windows, no multicast data will arrive.
        self._bindAddress = bind_address
        self._thread = None
        self.callbacks = []
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        try:
            self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        except:  # Not all systems support multiple sockets on the same port and interface
            pass
        self.sock.bind((bind_address, bind_port))

    def join_multicast(self, universe: int):
        """
        Joins the multicast address that is used for the given universe. Note: If you are on Windows you must have given
        a bind IP-Address for this feature to function properly. On the other hand you are not allowed to set a bind
        address if you are on any other OS.
        :param universe: the universe to join the multicast group.
        The network hardware has to support the multicast feature!
        """
        self.sock.setsockopt(socket.SOL_IP, socket.IP_ADD_MEMBERSHIP,
                             socket.inet_aton(calculate_multicast_addr(universe)) +
                             socket.inet_aton(self._bindAddress))

    def leave_multicast(self, universe: int):
        """
        Try to leave the multicast group with the specified universe. This does not throw any exception if the group
        could not be leaved.
        :param universe: the universe to leave the multicast group.
        The network hardware has to support the multicast feature!
        """
        try:
            self.sock.setsockopt(socket.SOL_IP, socket.IP_DROP_MEMBERSHIP,
                                 socket.inet_aton(calculate_multicast_addr(universe)) +
                                 socket.inet_aton(self._bindAddress))
        except:  # try to leave the multicast group for the universe
            pass

    def start(self):
        """
        Starts a new thread that handles the input. If a thread is already running, the thread will be restarted.
        """
        self.stop()  # stop an existing thread
        self._thread = _receiverThread(socket=self.sock, callbacks=self.callbacks)
        self._thread.start()

    def stop(self):
        """
        Stops a running thread. If no thread was started nothing happens.
        """
        try:
            self._thread.enabled_flag = False
        except:  # try to stop the thread
            pass

    def __del__(self):
        # stop a potential running thread
        self.stop()


class _receiverThread(threading.Thread):
    def __init__(self, socket: socket.socket, callbacks: list):
        """
        This is a private class and should not be used elsewhere. It handles the while loop running in the thread.
        :param socket: the socket to use to listen. It will not be initalized and only the socket.recv function is used.
        And the socket.settimeout function is also used
        :param callbacks: the list with all callbacks
        """
        self.enabled_flag = True
        self.sock = socket
        self.callbacks = callbacks
        super().__init__(name='sACN input/receiver thread')

    def run(self):
        socket.settimeout(0.1)  # timeout as 100ms
        self.enabled_flag = True
        while self.enabled_flag:
            try:
                raw_data = list(self.sock.recv(1024))
            except socket.timeout:
                continue  # if a timeout happens just go through while from the beginning
            try:
                tmp_packet = DataPacket.make_data_packet(raw_data)
            except:  # try to make a DataPacket. If it fails just go over it
                continue
            for callback in self.callbacks:
                try:
                    callback(tmp_packet)
                except:  # try to call back
                    pass