window.onload = function () {
 // переменная хранит загруженные уроки
    window.loaded_lesson = [];
    window.serial_device = new SerialDevice();
}

class SerialDevice {
    constructor(baudRate = 9600, timeout = 10) {
        this.port = null;
        this.baudRate = baudRate;
        this.timeout = timeout;
        this.reader = null;
        this.writer = null;
    }

    async requestPort() {
        try {
            this.port = await navigator.serial.requestPort();
            await this.port.open({ baudRate: 9600 });
            this.writer = this.port.writable.getWriter();
            return null;
        } catch (err) {
            console.error("Error requesting the port:", err);
            return null;
        }
    }

    async open() {
        try {
            await this.port.open({ baudRate: this.baudRate });
            this.reader = this.port.readable.getReader();
            this.writer = this.port.writable.getWriter();
            return true;
        } catch (err) {
            console.error("Error opening the port:", err);
            return false;
        }
    }

    close() {
        if (this.reader) {
            this.reader.cancel();
            this.reader.releaseLock();
            this.reader = null;
        }
        if (this.writer) {
            this.writer.close();
            this.writer.releaseLock();
            this.writer = null;
        }
        this.port.close();
    }

    async sendData(data) {
        if (this.writer) {
            const encoder = new TextEncoder();
            await this.writer.write(encoder.encode(data));
        }
    }

    async receiveData(numBytes) {
        if (this.reader) {
            const { value } = await this.reader.read();
            return value.slice(0, numBytes);
        }
        return null;
    }

    async smoke() {
        if (this.writer !== null){
            let encoder = new TextEncoder(); // всегда кодирует в UTF-8
            let uint8Array = encoder.encode("\nSmoke15000\n");
            await this.writer.write(uint8Array);
        }
    }

    async shock() {
        if (this.writer !== null){
            let encoder = new TextEncoder(); // всегда кодирует в UTF-8
            let uint8Array = encoder.encode("\nShock800\n");
            await this.writer.write(uint8Array);
        }
    }

}


//показываем нужный фрейм
function showFrame(frameId) {
    const frames = document.querySelectorAll('iframe');
    frames.forEach(frame => {
        frame.style.display = 'none';
    });
    document.getElementById(frameId).style.display = 'block';
}

//если уроки не загружены или отличаются от выбранные то перегружаем страницу с уроками если нет то просто показываем страницу с обучением
function start_study(){
    if (window.serial_device.port == null){
        window.serial_device.requestPort().then(r => {
                        console.log("Success:");
                    })
    }
    let sel_lesson_id = window.document.getElementsByClassName('id_sent')
    let equal = false;
    if (sel_lesson_id.length===window.loaded_lesson.length){
        equal = true;
        for (let i=0; i< window.loaded_lesson.length; i++){
            if (window.loaded_lesson[i] !== sel_lesson_id[i].getAttribute('name')){
                equal = false;
            }
        }
    }
    if (!equal){
        document.forms[0].submit();
    }
    showFrame('study');
}
