from pymodbus.client import ModbusTcpClient


class ModbusClient:
    def __init__(self, host, slave, port=502):
        self.slave = slave
        self.client = ModbusTcpClient(host, port, timeout=2)

    def connect(self):
        if not self.client.connect():
            raise ConnectionError("Failed to connect to Modbus server")

    def read_coils(self, address, count=8):
        result = self.client.read_coils(address, count, slave=self.slave)
        if result.isError():
            raise Exception("Modbus error: {}".format(result))
        return result.bits[0]

    def write_coil(self, address, values):
        result = self.client.write_coil(address, values, slave=self.slave)
        if result.isError():
            raise Exception("Modbus error: {}".format(result))

    def close(self):
        self.client.close()

# real = ModbusClient()
# real.connect()
# real.write_coil(1, True)
# real.close()
