import serial.tools.list_ports


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
        return list(serial.tools.list_ports.comports())


class SerialDevice:
    def __init__(self, port, baudrate=9600, timeout=1):
        self.port = port
        self.baudrate = baudrate
        self.timeout = timeout
        self.serial = None
        self.avel_ports = available_ports()

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
    device = SerialDevice('COM1', baudrate=9600, timeout=1)

    if device.open():
        print("Устройство подключено")
        data_to_send = b'Hello, COM port!'
        device.send_data(data_to_send)

        received_data = device.receive_data(10)
        print(f"Принято: {received_data.decode('utf-8')}")

        device.close()
    else:
        print("Не удалось подключиться к устройству")
