let port = null
let writer = null
window.onload = async function () {
    showFrame('lessons');
    const button = document.getElementById('f1');
    button.addEventListener('click', function () {
        main();
    });
    const button2 = document.getElementById('f2');
    button2.addEventListener('click', function () {
       requestPort();
    });
};

let predTime = new Date();
let timePause = 0;

   document.getElementById('meaning').value = text.substring(0, textLen - 1);
        comport.sendData('Shock100\n'); // Здесь потребуется адаптация под ваше API или библиотеку
        shockCount++;
        console.log('Shock');
        mistake = true;
    } else if (textLen === curLesData.phraseSent.length) {
        document.getElementById('meaning').value = '';

        if (mistake) {
            rightAnswerCountInLesson = 0;
            mistake = false;
            curLesData.wasMistakeFlag = true;
        } else {
            curLesData.wasMistakeFlag = false;
            rightAnswerCountInLesson++;
            if (rightAnswerCountInLesson === 5) {
                openWindowPause(); // Эта функция должна быть определена где-то еще
                rightAnswerCountInLesson = 0;
            }
        }

        playSound(`audio/${curLesData.phraseAudio}.mp3`); // Здесь потребуется функция для воспроизведения звука

        curLesData.wasHelpFlag = helpFlag;
        curLesData.wasHelpSoundFlag = soundHelpFlag;

        // Далее идет код, который я не перевел, так как он зависит от конкретной реализации в вашем проекте
    }
}
function removeDiacritics(str) {
    return str.normalize("NFD").replace(/[\u0300-\u036f]/g, "");
}


async function getAvailablePorts() {
    // Получить все доступные порты
    const ports = await navigator.serial.getPorts();

    // Если нет доступных портов
    if (ports.length === 0) {
        return [''];
    }

    // Возвращаем список имен портов
    return ports.map(port => port.getInfo().serialNumber);
}

class SerialDevice {
    constructor(port, baudRate = 9600, timeout = 10) {
        this.port = port;
        this.baudRate = baudRate;
        this.timeout = timeout;
        this.reader = null;
        this.writer = null;
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
}

async function requestPort() {
    try {
        port = await navigator.serial.requestPort();
        await port.open({ baudRate: 9600 });
        writer = port.writable.getWriter();
        return null;
    } catch (err) {
        console.error("Error requesting the port:", err);
        return null;
    }
}





function delay(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
}
async function main() {

    let encoder = new TextEncoder(); // всегда кодирует в UTF-8
    let uint8Array = encoder.encode("\nSmoke60000\n");

    await writer.write(uint8Array);
    //writer.releaseLock();
    //const reader = port.readable.getReader();

// Listen to data coming from the serial device.
//while (true) {
 // const { value, done } = await reader.read();
 // console.log(0);
 // if (done) {
    // Allow the serial port to be closed later.
  //  reader.releaseLock();
   // console.log(1);
   // break;
 // }
  // value is a Uint8Array.
  //console.log(value);
  //console.log(2);
//}
    //const writer = port.writable.getWriter();




}

function playSound(src) {
    let audio = new Audio(src);
    audio.play();
}

playSound('path/to/your/audiofile.mp3');

let audio = new Audio('path/to/your/audiofile.mp3');

function playSound() {
    audio.currentTime = 0; // Если хотите начать воспроизведение с начала каждый раз
    audio.play();
}

audio.addEventListener('ended', function() {
    console.log('Audio playback has ended.');
});

<button onClick="playSound('path/to/your/audiofile.mp3')">Play Sound</button>
