let help_flag = false;
let sound_help_flag = false;
let mistake = false;
let transl = null;
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
let voice = ''
const SENTENCE_WARM_UP = 0
const SENTENCE_NEW_WITH_MISTAKE = 1
const REPEATING_SENTENCE = 4
const NEW_SENTENCE = 5
const SENTENCE_RIGHT_MORE_THREE = 3
const SENTENCE_RIGHT_LESS_THREE = 2

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
    document.getElementById('right_answer').value = lesson_data[curr_sent_count].right_answer
    document.getElementById('full_understand').value = lesson_data[curr_sent_count].full_understand
    if (lesson_data[curr_sent_count].study_type===NEW_SENTENCE){
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
                let inc = '0'
                let dec ='0'
                if (lesson_data[curr_sent_count].study_type !== SENTENCE_WARM_UP){
                    if (lesson_data[curr_sent_count].showings_count === 0){
                        inc = money_motivator_inc
                        dec = money_motivator_dec
                    }else {
                        inc = '0'
                        dec = money_motivator_dec
                    }
                }
                if (money_motivator){
                    document.getElementById('money_motivator_inc').innerText = inc
                    document.getElementById('money_motivator_dec').innerText = dec
                    document.getElementById('btc_balance_my_out').innerText = response.win_btc
                    document.getElementById('btc_balance_no_my_out').innerText = response.lose_btc
                    document.getElementById('money_for_today').innerText = response.money_for_today
                }
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
    show_message(transl.smoke_txt, 30000);
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

function show_back_ground(img){
    // Находим контейнер, в котором находится изображение
    let container = document.getElementById('lesson_background');
    // Удаляем текущий элемент img из контейнера
    let currentImg = container.querySelector('img');
    if (currentImg) {
        container.removeChild(currentImg);
        container.appendChild(img);
    }
}

function prepare_lesson_data(data){
    for (let row of data){
        let destination = {
            id_phrase: row.id_phrase,
            num_showings: row.num_showings,
            phrase_for_checking: row.phrase_for_checking,
            phrase_native: row.phrase_native,
            phrase_study: row.phrase_study,
            study_type: row.study_type,
            was_help_flag: row.was_help_flag,
            was_help_sound_flag: row.was_help_sound_flag,
            was_mistake_flag: row.was_mistake_flag,
            showings_count: 0,
            mistake_count: 0,
            total_time: 0,
            right_answer: 0,
            full_understand: 0
          };

          // Создаем объекты аудио и изображения
          destination.phrase_study_audio = new Audio('/static/audio/hs/'+voice+'/'+row.phrase_study_audio+'.mp3');
          destination.phrase_native_audio = new Audio('/static/audio/hs/'+voice+'/'+row.phrase_native_audio+'.mp3');
          destination.img = new Image();
          destination.img.src = '/static/img/hs/back_ground/'+row.img;

          lesson_data.push(destination)
    }
}

function download_lessons(){
    let delay = 5000; // Задержка между попытками, по умолчанию 2 секунды
    $.ajax({
        url: '/get_lessons_data',
        dataType: 'json',
        success: function(data) {
            prepare_lesson_data(data)
            console.info(lesson_data)
            document.getElementById('load_lesson').style.display = 'none'
            document.getElementById('quest_view').style.display = 'flex'
            next()
        },
        error: function(jqXHR, textStatus) {
          console.error(`Ошибка загрузки: ${textStatus}. Попытка повторного запроса через 5с.`);
          setTimeout(function() {
            download_lessons(); // Повторный вызов функции после задержки
          }, delay);
        }
      });
}

function connect_com_device(){
    serial_device = new SerialDevice();
    if (serial_device.port == null){
                serial_device.requestPort().then(r => {
                        close_message_box();
                        show_message(transl.dev_connected, 1000, null)
                })
             }
}


function next(){
    lesson_data[curr_sent_count].phrase_study_audio.removeEventListener('ended', next)
    mistake = false;
    help_flag = false;
    sound_help_flag = false;
    document.getElementById('one_letter').style.display = "block";
    if (lesson_data[curr_sent_count].num_showings<=lesson_data[curr_sent_count].showings_count){
         if (lesson_data[curr_sent_count].study_type!==SENTENCE_WARM_UP) {
             send_study_data('statistic')
         }

        let array1 = lesson_data.slice(0, curr_sent_count)
        let array2 = lesson_data.slice(curr_sent_count+1, lesson_data.length)
        lesson_data = array1.concat(array2)
    }

    if (lesson_data.length>0){
        if (lesson_data[0].study_type===SENTENCE_RIGHT_MORE_THREE){
            curr_sent_count = Math.round(Math.random()*(lesson_data.length-1))
        }
        if (lesson_data[curr_sent_count].study_type===NEW_SENTENCE){
            document.getElementById('input_text_new_phrase').style.display = 'block'
        }else {
            document.getElementById('input_text_new_phrase').style.display = 'none'
        }
        if (lesson_data[curr_sent_count].study_type !== SENTENCE_WARM_UP && money_motivator){
            if (lesson_data[curr_sent_count].showings_count === 0){
                document.getElementById('money_motivator_inc').innerText = money_motivator_inc.toFixed(2)
                document.getElementById('money_motivator_dec').innerText = money_motivator_dec.toFixed(2)
            }else{
                document.getElementById('money_motivator_inc').innerText = '0'
                document.getElementById('money_motivator_dec').innerText = money_motivator_dec.toFixed(2)
            }

        }

        lesson_data[curr_sent_count].showings_count ++
        show_back_ground(lesson_data[curr_sent_count].img);
        lesson_data[curr_sent_count].phrase_native_audio.play();
        document.getElementById('phrase_meaning').innerText = lesson_data[curr_sent_count].phrase_native;
        document.getElementById('input_text').focus();
    }else {
        $.ajax({
            url: '/lesson_result',
            success: function(result) {
                let mess = transl.show_time + ' ' + result.shows + '\n'+
                    transl.spend_time+ ' ' + Math.round(result.total_time/60) + ' min\n' +
                    transl.right_ans + ' ' + result.right_answer + '\n' +
                    transl.err_ans + ' ' + result.mistake + '\n'+
                    transl.new_phr + ' ' + result.new_phrase + '\n'+
                    transl.no_help + ' ' + result.full_understand + '\n'+
                    transl.repeat_les
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
    let deltaTime = (currentTime - predTime);
    if (deltaTime < 180000) {
        lesson_data[curr_sent_count].total_time += deltaTime/1000;
    }
    predTime = currentTime;
    let text = document.getElementById('input_text').value;
    if (deltaTime < 200){
        document.getElementById('input_text').blur();
        show_message(transl.fast_txt, 500)
    }
    //console.info(text)
    if (!lesson_data[curr_sent_count].phrase_for_checking.toLowerCase().startsWith(text.toLowerCase())) {
        while (!lesson_data[curr_sent_count].phrase_for_checking.toLowerCase().startsWith(text.toLowerCase())){
            document.getElementById('input_text').value = text.slice(0,-1);
            text = document.getElementById('input_text').value;
        }
        lesson_data[curr_sent_count].mistake_count += 1;
        mistake = true;
        if (money_motivator && lesson_data[curr_sent_count].study_type !== SENTENCE_WARM_UP){
            document.getElementById('id_phrase').value = 'false'
            send_study_data("study_data")
        }
        if(shock_motivator){
            serial_device.shock();
        }
        show_message(transl.mistake_txt, 500)
        // console.info('wrong');

    }else {
        if (text.length > 0) {
            if (lesson_data[curr_sent_count].phrase_for_checking.length === text.length) {
                document.getElementById('input_text').value = '';
                if (lesson_data[curr_sent_count].showings_count===1){
                    if (lesson_data[curr_sent_count].study_type===SENTENCE_WARM_UP){
                        document.getElementById('id_phrase').value = 'false'
                    }else {
                        document.getElementById('id_phrase').value = lesson_data[curr_sent_count].id_phrase

                        if (!mistake && !help_flag) {
                            lesson_data[curr_sent_count].right_answer = 1
                            if (!sound_help_flag) {
                                lesson_data[curr_sent_count].full_understand = 1
                                lesson_data[curr_sent_count].showings_count = lesson_data[curr_sent_count].num_showings
                            }
                            if (smoke_motivator) {
                                serial_device.smoke()
                                show_message(transl.smoke_txt, 30000)
                            }
                        }
                    }
                    send_study_data("study_data")

                }
                // проверяем были ли ошибки
                if (lesson_data[curr_sent_count].study_type===SENTENCE_WARM_UP) {
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