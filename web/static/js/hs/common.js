function show_message(text, time, func1, func2){
    document.getElementById('message_box_text').innerText = text;
    if (func1!=null){
        document.getElementById('ok_btn').onclick = func1;
        document.getElementById('ok_btn').style.display = "block";
    }else {
        document.getElementById('ok_btn').style.display = "none";
    }
    if (func2!=null){
        document.getElementById('cancel_btn').onclick = func2;
    }else {
        document.getElementById('cancel_btn').onclick = close_message_box;
    }
    document.getElementById('message_box').style.display = "flex";
    document.getElementsByClassName('button_block')[0].focus();
    if (time>0) {
        setTimeout(function () {
            document.getElementById('message_box').style.display = "none";
            document.getElementById('input_text').focus();
        }, time);
    }
}


function close_message_box(){
    document.getElementById('message_box').style.display = "none";
}