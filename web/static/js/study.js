let predTime = new Date();
let timePause = 0;
let timeStart = new Date();
let lesson_data = [];
let curr_sent_count = -1;
let shock_count = 0;
let right_answer_count_in_lesson = 0
let help_flag = false;
let sound_help_flag = false;
let mistake = false;
let know_phrase = [];

function removeDiacritics(str) {
    return str.normalize("NFD").replace(/[\u0300-\u036f]/g, "");
}

function open_window_pause(){
    document.getElementById('pause_box_back').style.display = "block";
     window.parent.serial_device.smoke();
    setTimeout(function (){
        document.getElementById('pause_box_back').style.display = "none";
    }, 60000);
}

function on_help(){
    help_flag = true;
    document.getElementById('help_box').innerText = lesson_data[curr_sent_count].phrase_sent;
    document.getElementById('help_box_back').style.display = "block";
    setTimeout(function (){
        document.getElementById('help_box_back').style.display = "none";
        document.getElementById('input_text').focus();
    }, 5000);
    lesson_data[curr_sent_count].phrase_audio.play();
}

function on_sound(){
    sound_help_flag = true;
    lesson_data[curr_sent_count].phrase_audio.play();
    document.getElementById('input_text').focus();
}

function next(){
    //console.info('next');
    mistake = false;
    help_flag = false;
    sound_help_flag = false;
    curr_sent_count++;
    while ((curr_sent_count !== lesson_data.length-1) && (know_phrase.lastIndexOf(lesson_data[curr_sent_count].id_phrase)!==-1)){
        curr_sent_count++;
    }
    if (curr_sent_count !== lesson_data.length-1){
       lesson_data[curr_sent_count].phrase_meaning_audio.play();
       document.getElementById('phrase_meaning').innerText = lesson_data[curr_sent_count].phrase_meaning;
       document.getElementById('input_text').focus();
    }else {
       let form = document.getElementById('response');
       let response = [];
       let timeStop = new Date();
       let lessonDuration = Math.round((timeStop - timeStart)/1000 - timePause)
       for (lesson of lesson_data){
           response.push({
               id_phrase: lesson.id_phrase,
               phrase_sent: lesson.phrase_sent,
               inc_flag: lesson.inc_flag,
               dec_flag: lesson.dec_flag,
               was_help_flag: lesson.was_help_flag,
               was_help_sound_flag: lesson.was_help_sound_flag,
               was_mistake_flag: lesson.was_mistake_flag
           });
       }

       let input_el = document.createElement('input');
       input_el.setAttribute('type', 'hidden');
       input_el.setAttribute('name', 'response');
       input_el.setAttribute('value', JSON.stringify(response));
       form.appendChild(input_el);
       input_el = document.createElement('input');
       input_el.setAttribute('type', 'hidden');
       input_el.setAttribute('name', 'timeStart');
       input_el.setAttribute('value', timeStart.toJSON());
       form.appendChild(input_el);
       input_el = document.createElement('input');
       input_el.setAttribute('type', 'hidden');
       input_el.setAttribute('name', 'timeStop');
       input_el.setAttribute('value', timeStop.toJSON());
       form.appendChild(input_el);
       input_el = document.createElement('input');
       input_el.setAttribute('type', 'hidden');
       input_el.setAttribute('name', 'duration');
       input_el.setAttribute('value', lessonDuration.toString());
       form.appendChild(input_el);
       input_el = document.createElement('input');
       input_el.setAttribute('type', 'hidden');
       input_el.setAttribute('name', 'shock_count');
       input_el.setAttribute('value', shock_count.toString());
       form.appendChild(input_el);
       input_el = document.createElement('input');
       input_el.setAttribute('type', 'hidden');
       input_el.setAttribute('name', 'lessons');
       input_el.setAttribute('value', JSON.stringify(window.parent.loaded_lesson));
       form.appendChild(input_el);

       form.submit();

       //показываем stat фрейм
        const frames = window.parent.document.querySelectorAll('iframe');
        frames.forEach(frame => {
            frame.style.display = 'none';
        });
        window.parent.document.getElementById('stat').style.display = 'block';

       //console.info('finish')
    }
}

function onEntryChangeStudy() {
    let currentTime = new Date();
    let deltaTime = (currentTime - predTime) / 1000; // seconds
    if (deltaTime > 180) {
        timePause += deltaTime;
    }
    predTime = currentTime;

    let text = document.getElementById('input_text').value;

    //console.info(text)
    if (!lesson_data[curr_sent_count].phrase_sent.toLowerCase().startsWith(text.toLowerCase())) {
        while (!lesson_data[curr_sent_count].phrase_sent.toLowerCase().startsWith(text.toLowerCase())){
            document.getElementById('input_text').value = text.slice(0,-1);
            text = document.getElementById('input_text').value;
        }
        shock_count += 1;
        mistake = true;
        window.parent.serial_device.shock();
        //console.info('wrong');
    }else {
        if (text.length > 0 ) {
            if (lesson_data[curr_sent_count].phrase_sent.length === text.length) {
                document.getElementById('input_text').value = '';
                //console.info(mistake)
                // проверяем были ли ошибки
                if (mistake) {
                    right_answer_count_in_lesson = 0;
                    mistake = false;
                    lesson_data[curr_sent_count].was_mistake_flag = true;
                } else {
                    //console.info('rigth');
                    lesson_data[curr_sent_count].was_mistake_flag = false;
                    right_answer_count_in_lesson += 1;

                    if (lesson_data[curr_sent_count].dec_flag || right_answer_count_in_lesson === 5) {
                        right_answer_count_in_lesson = 0;
                        if (curr_sent_count < lesson_data.length - 1) {
                            lesson_data[curr_sent_count + 1].phrase_meaning_audio.addEventListener('ended', open_window_pause)
                        }
                    }
                }

                lesson_data[curr_sent_count].phrase_audio.play()
                lesson_data[curr_sent_count].phrase_audio.addEventListener('ended', next)

                lesson_data[curr_sent_count].was_help_flag = help_flag;
                lesson_data[curr_sent_count].was_help_sound_flag = sound_help_flag;

                // если слово было введено правильно без произведения звуковой подсказки то показываем одни раз

                if (!(sound_help_flag || help_flag || lesson_data[curr_sent_count].was_mistake_flag) && lesson_data[curr_sent_count].dec_flag) {
                    if (know_phrase.lastIndexOf(lesson_data[curr_sent_count].id_phrase) === -1) {
                        know_phrase.push(lesson_data[curr_sent_count].id_phrase);
                    }

                }


            }



        }
    }
}