const FPS = 24;
const video = document.querySelector("#videoElement");
const canvas = document.getElementById('canvas');
const photo = document.getElementById('photo');
const context = canvas.getContext('2d');
const socket = io();
const maxWidth = 250;
let aspectRatio = 0;
let data = null;

function setMediaSize(){
    if (navigator.mediaDevices.getUserMedia) {
        navigator.mediaDevices.getUserMedia({
            audio: false,
            video: {
                facingMode: 'environment'
            }            
        }).then(function (stream) {
                const {width, height} = stream.getVideoTracks()[0].getSettings();
                aspectRatio = width / height;
                video.width = maxWidth;
                video.height = video.width / aspectRatio;
    
                canvas.width = video.width;
                canvas.height = video.height;
    
                photo.width = video.width;
                // photo.height = video.height;
    
                video.srcObject = stream;
                video.play();
            })
            .catch(function (error) {
                console.log('problem accessing the camera');
            });
    }   
}

socket.on('connect', function () {
    console.log("Connected...!", socket.connected)
    setMediaSize()
});

setInterval(() => {
    width = video.width;
    height = video.height;
    context.drawImage(video, 0, 0, width, height);
    data = canvas.toDataURL('image/jpeg', 0.5);
    context.clearRect(0, 0, width, height);
    socket.emit('image', data);
}, 1000 / FPS);

socket.on('processed_image', function (image) {
    photo.setAttribute('src', image);
});


window.addEventListener('resize', setMediaSize);
screen.orientation.addEventListener('change', setMediaSize);
setMediaSize();