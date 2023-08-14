import pigpio
from nrf24 import *

from .rtcm_parser import RTCMParser

class NRF24Client:
    def __init__(self, address, channel, host="localhost", port=8888, logerr=logging.error, logwarn=logging.warning, loginfo=logging.info, logdebug=logging.debug):
        self._logerr = logerr
        self._logwarn = logwarn
        self._loginfo = loginfo
        self._logdebug = logdebug
        self._nrf = None
        self._host = host
        self._port = port
        self._address = address
        self._channel = channel
        self.rtcm_parser = RTCMParser(
            logerr=logerr,
            logwarn=logwarn,
            loginfo=loginfo,
            logdebug=logdebug
        )

    def connect(self):
        # Connect to pigpiod
        self._loginfo(f'Connecting to GPIO daemon on {self._host}:{self._port} ...')
        pi = pigpio.pi(hostname, port)
        if not pi.connected:
            self._logerr("Not connected to Raspberry Pi ... goodbye.")
            return False

        self._nrf = NRF24(pi, ce=25, payload_size=RF24_PAYLOAD.DYNAMIC, channel=self._channel, data_rate=RF24_DATA_RATE.RATE_250KBPS, pa_level=RF24_PA.HIGH)
        self._nrf.set_address_bytes(len(self._address))
        self._nrf.open_reading_pipe(RF24_RX_ADDR.P1, self._address, size=RF24_PAYLOAD.DYNAMIC)

        return True

    def shutdown(self):
        self._nrf.power_down()
    
    def send_nmea(self, sentence):
        pass

    def recv_rtcm(self):
        data = b''
        while self._nrf.data_ready() and len(data) < 1024:
            pipe = nrf.data_pipe()
            payload = nrf.get_payload()

            if pipe == RF24_RX_ADDR.P1:
                data += payload

        # Send the data to the RTCM parser to parse it
        return self.rtcm_parser.parse(data) if data else []
