import plugins
import socket
import struct
import json

class Plugin(plugins.BasePlugin):
    __name__ = 'minecraft'

    def run(self, config):
        '''
        Fetch the amount of active and max players
        add to /etc/nixstats.ini
        [minecraft]
        enabled=yes 
        host=minecraft_host_or_IP
        port=minecraft_PORT
        '''

        try:
            # Connect
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            host = config.get('minecraft', 'host')
            port = int(config.get('minecraft', 'port'))
            s.connect((host, port))

            # Send handshake + status request
            s.send(self.pack_data("\x00\x00" + self.pack_data(host.encode('utf8')) + self.pack_port(port) + "\x01"))
            s.send(self.pack_data("\x00"))

            # Read response
            self.unpack_varint(s)     # Packet length
            self.unpack_varint(s)     # Packet ID
            l = self.unpack_varint(s) # String length

            d = ""
            while len(d) < l:
                d += s.recv(1024)

            # Close our socket
            s.close()
        except:
            return "Could not connect to server"

        results = {}

        try:
            players = json.loads(d.decode('utf8'))['players']
            results['online'] = int(players['online'])
            results['max'] = int(players['max'])
        except:
            results['online'] = 0
            results['max'] = 0

        return results

    def unpack_varint(self, s):
        d = 0
        for i in range(5):
            b = ord(s.recv(1))
            d |= (b & 0x7F) << 7*i
            if not b & 0x80:
                break
        return d

    def pack_varint(self, d):
        o = ""
        while True:
            b = d & 0x7F
            d >>= 7
            o += struct.pack("B", b | (0x80 if d > 0 else 0))
            if d == 0:
                break
        return o

    def pack_data(self, d):
        return self.pack_varint(len(d)) + d

    def pack_port(self, i):
        return struct.pack('>H', i)

if __name__ == '__main__':
    Plugin().execute()
