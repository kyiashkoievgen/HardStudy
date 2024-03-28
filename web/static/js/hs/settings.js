
function activate_money_motivator(){
    close_message_box()
    document.getElementById('activate_motivator').value = "True"
    document.getElementById('setting_form_money').submit()
}

function fetchQRCode() {
            const url = "/top_up_balance";

            fetch(url)
                .then(response => response.text()) // Получаем ответ как простой текст
                .then(html => {
                    // Вставляем HTML код, полученный от сервера, в контейнер
                    show_message(null,null, null, null, html)
                })
                .catch(error => console.error('Error:', error));
        }

function check_balance(input, balance){

    if (input.value<=balance && input.value>0){
        document.getElementById('ok_btn').style.display = "block";
        document.getElementById('ok_btn').onclick = function (){
            window.location.href=`/top_up_money_motivator?val=${input.value}`
        }
    }else {
        document.getElementById('ok_btn').style.display = "none";
    }

}
// отправка формы на сервер при изменении валюты
function onCurrencyChange(){
    document.getElementById('setting_form').submit()
}