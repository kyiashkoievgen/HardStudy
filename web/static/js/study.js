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