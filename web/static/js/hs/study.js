let help_flag = false;
let sound_help_flag = false;
let mistake = false;

let lesson_data = [];
let curr_sent_count = 0;
let predTime = new Date();
let serial_device = null;
let shock_motivator = false;
let smoke_motivator = false;
let money_motivator = false;
let money_motivator_inc = 0;
let money_motivator_dec = 0;
let btc_balance_my_out = 0;
let btc_balance_no_my_out = 0;
let money_for_today = 0;

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
            let uint8Array = encoder.encode("\nSmoke30000\n");
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

function send_study_data(form){
    document.getElementById('was_help_flag').value = help_flag
    document.getElementById('was_help_sound_flag').value = sound_help_flag
    document.getElementById('was_mistake_flag').value = mistake
    document.getElementById('total_phrase').value = lesson_data.length

    document.getElementById('statistic_id_phrase').value = lesson_data[curr_sent_count].id_phrase
    document.getElementById('shows').value = lesson_data[curr_sent_count].showings_count
    document.getElementById('mistake_count').value = lesson_data[curr_sent_count].mistake_count
    document.getElementById('total_time').value = Math.round(lesson_data[curr_sent_count].total_time)
    document.getElementById('time_start').value = lesson_data[curr_sent_count].time_start.toJSON()
    document.getElementById('right_answer').value = lesson_data[curr_sent_count].right_answer
    document.getElementById('full_understand').value = lesson_data[curr_sent_count].full_understand
    if (lesson_data[curr_sent_count].study_type===5){
         document.getElementById('new_phrase').value = 1
    }else {
        document.getElementById('new_phrase').value = 0
    }

    let formData = $(document.getElementById(form)).serialize();
    $.ajax({
        type: 'POST',
        url: '/save_lesson_data',
        data: formData,
        success: function(response) {
            if (response.money_motivator){
                money_motivator_inc = response.money_motivator_inc;
                money_motivator_dec = response.money_motivator_dec;
                let inc = 0
                let dec =0
                if (lesson_data[curr_sent_count].study_type !== 0){
                    if (lesson_data[curr_sent_count].showings_count === 1){
                        inc = money_motivator_inc
                        dec = money_motivator_dec
                    }else {
                        inc = 0
                        dec = money_motivator_dec
                    }
                }

                document.getElementById('money_motivator_inc').innerText = inc.toString()
                document.getElementById('money_motivator_dec').innerText = dec.toString()
                document.getElementById('btc_balance_my_out').innerText = response.win_btc.toString()
                document.getElementById('btc_balance_no_my_out').innerText = response.lose_btc.toString()
                document.getElementById('money_for_today').innerText = response.money_for_today.toString()
            }
            console.info(response)
        },
        error: function(response) {
            // Обработка ошибок
        }
    });
}

function open_window_pause(){
    window.parent.serial_device.smoke();
    show_message('Перекур', 30000);
}

function on_help(){
    help_flag = true;
    show_message(lesson_data[curr_sent_count].phrase_study, 5000)
    lesson_data[curr_sent_count].phrase_study_audio.play();
}

function on_sound(){
    sound_help_flag = true;
    lesson_data[curr_sent_count].phrase_study_audio.play();
    document.getElementById('input_text').focus();
}

function on_one_letter(){
    let symbol_num = document.getElementById('input_text').value.length
    show_message(lesson_data[curr_sent_count].phrase_study.slice(symbol_num, symbol_num+1), 500)
    document.getElementById('one_letter').style.display = "none";
}

function repeat_lesson(){
    window.location.href = '/study'
}

function to_home(){
    window.location.href = '/'
}



function connect_com_device(){
    serial_device = new SerialDevice();
    if (serial_device.port == null){
                serial_device.requestPort().then(r => {
                        close_message_box();
                        show_message("Устройство подключено", 1000, null)
                })
             }
}


function next(){
    lesson_data[curr_sent_count].phrase_study_audio.removeEventListener('ended', next)
    document.getElementById('img'+lesson_data[curr_sent_count].id_phrase).style.display = "none";
    mistake = false;
    help_flag = false;
    sound_help_flag = false;
    document.getElementById('one_letter').style.display = "block";
    if (lesson_data[curr_sent_count].num_showings<=lesson_data[curr_sent_count].showings_count){
         if (lesson_data[curr_sent_count].study_type!==0) {
             send_study_data('statistic')
         }

        let array1 = lesson_data.slice(0, curr_sent_count)
        let array2 = lesson_data.slice(curr_sent_count+1, lesson_data.length)
        lesson_data = array1.concat(array2)
    }

    if (lesson_data.length>0){
        if (lesson_data[0].study_type===3){
            curr_sent_count = Math.round(Math.random()*(lesson_data.length-1))
        }
        if (lesson_data[curr_sent_count].study_type !== 0){
            document.getElementById('money_motivator_inc').innerText = money_motivator_inc.toString()
            document.getElementById('money_motivator_dec').innerText = money_motivator_dec.toString()
        }

        lesson_data[curr_sent_count].showings_count ++
        document.getElementById('img'+lesson_data[curr_sent_count].id_phrase).style.display = "block";
        lesson_data[curr_sent_count].phrase_native_audio.play();
        document.getElementById('phrase_meaning').innerText = lesson_data[curr_sent_count].phrase_native;
        document.getElementById('input_text').focus();
    }else {
        $.ajax({
            url: '/lesson_result',
            success: function(result) {
                let mess = 'Показано ' + result.shows + ' раз\n'+
                    'Потрачено времени ' + Math.round(result.total_time/60) + ' минут\n' +
                    'Правильных ответов ' + result.right_answer + '\n' +
                    'Ошибок ' + result.mistake + '\n'+
                    'Новых фраз ' + result.new_phrase + '\n'+
                    'Без подсказок ' + result.full_understand + '\n'+
                    'Повторить урок?'
                show_message(mess, 0, repeat_lesson, to_home)
            },
            error: function(response) {
                // Обработка ошибок
            }
        });

    }

}

function onEntryChangeStudy() {
    let currentTime = new Date();
    let deltaTime = (currentTime - predTime) / 1000; // seconds
    if (deltaTime < 180) {
        lesson_data[curr_sent_count].total_time += deltaTime;
    }
    predTime = currentTime;
    let text = document.getElementById('input_text').value;

    //console.info(text)
    if (!lesson_data[curr_sent_count].phrase_for_checking.toLowerCase().startsWith(text.toLowerCase())) {
        while (!lesson_data[curr_sent_count].phrase_for_checking.toLowerCase().startsWith(text.toLowerCase())){
            document.getElementById('input_text').value = text.slice(0,-1);
            text = document.getElementById('input_text').value;
        }
        lesson_data[curr_sent_count].mistake_count += 1;
        mistake = true;
        if (money_motivator && lesson_data[curr_sent_count].study_type !== 0){
            document.getElementById('id_phrase').value = 'false'
            send_study_data("study_data")
        }
        if(shock_motivator){
            serial_device.shock();
        }
        console.info('wrong');
    }else {
        if (text.length > 0) {
            if (lesson_data[curr_sent_count].phrase_for_checking.length === text.length) {
                document.getElementById('input_text').value = '';
                if (lesson_data[curr_sent_count].showings_count===1 && lesson_data[curr_sent_count].study_type!==0){
                    document.getElementById('id_phrase').value = lesson_data[curr_sent_count].id_phrase
                    send_study_data("study_data")
                    if (!mistake && !help_flag){
                        lesson_data[curr_sent_count].right_answer = 1
                        if (!sound_help_flag){
                            lesson_data[curr_sent_count].full_understand = 1
                            lesson_data[curr_sent_count].showings_count = lesson_data[curr_sent_count].num_showings
                        }
                        if (smoke_motivator){
                            serial_device.smoke()
                            show_message("Перекур", 30000)
                        }
                    }

                }
                // проверяем были ли ошибки
                if (lesson_data[curr_sent_count].study_type===0) {
                    if (mistake){
                        lesson_data[curr_sent_count].showings_count = 0
                    }else {
                        lesson_data[curr_sent_count].showings_count = lesson_data[curr_sent_count].num_showings
                    }

                }

                lesson_data[curr_sent_count].phrase_study_audio.addEventListener('ended', next)
                lesson_data[curr_sent_count].phrase_study_audio.play()

            }



        }
    }
}