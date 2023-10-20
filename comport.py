import serial.tools.list_ports
import time


# # Получаем список доступных COM-портов
# available_ports = list(serial.tools.list_ports.comports())
#
# # Выводим список COM-портов
# for port in available_ports:
#     print(f"Имя порта: {port.device}, Описание: {port.description}")


def available_ports():
    ports = list(serial.tools.list_ports.comports())
    if len(ports) == 0:
        return ['']
    else:
        com_port_name = []
        for port, desc, hwid in sorted(serial.tools.list_ports.comports()):
            com_port_name.append(port)
        return com_port_name


class SerialDevice:
    def __init__(self, port, baudrate=9600, timeout=10):
        self.port = port
        self.baudrate = baudrate
        self.timeout = timeout
        self.serial = None
        self.avel_ports = available_ports()
        # if self.open():
        #     print("Устройство подключено")
        #     data_to_send = b'HandShake\n'
        #     time.sleep(3)
        #     self.send_data(data_to_send)
        #     received_data = b''
        #     #i=0
        #     #while received_data == b'':
        #     received_data = self.receive_data(20)
        #     print(f"Принято: {received_data}")
        #     #    i += 1
        #
        #     self.close()
        # else:
        #     print("Не удалось подключиться к устройству")
    def open(self):
        try:
            self.serial = serial.Serial(self.port, self.baudrate, timeout=self.timeout)
            return True
        except serial.SerialException:
            return False

    def close(self):
        if self.serial and self.serial.is_open:
            self.serial.close()

    def send_data(self, data):
        if self.serial and self.serial.is_open:
            self.serial.write(data)

    def receive_data(self, num_bytes):
        if self.serial and self.serial.is_open:
            return self.serial.read(num_bytes)


# Пример использования класса
if __name__ == "__main__":
    device = SerialDevice('COM12', baudrate=9600, timeout=10)
    if device.open():
        print("Устройство подключено")
        data_to_send = b'Smoke60000\n'
        device.send_data(data_to_send)

        received_data = device.receive_data(10)
        print(f"Принято: {received_data.decode('utf-8')}")

        device.close()
    else:
        print("Не удалось подключиться к устройству")
