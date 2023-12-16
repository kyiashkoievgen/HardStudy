//показываем нужный фрейм
function showFrame(frameId) {
    const frames = document.querySelectorAll('iframe');
    frames.forEach(frame => {
        frame.style.display = 'none';
    });
    document.getElementById(frameId).style.display = 'block';
}

function new_chat(){
    const chat_name = document.getElementById('new_chat').value
    if (chat_name!==''){
        window.frames[0].location.href ="/chat_messages/new"
        showFrame('chat');
    }else {
        alert("введите имя чата");
    }
}
