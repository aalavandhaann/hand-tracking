const FPS = 2;
const video = document.querySelector("#videoElement");
const canvas = document.getElementById('canvas');
const photo = document.getElementById('photo');
const context = canvas.getContext('2d');
const socket = io();
const maxWidth = 500;
let aspectRatio = 0;
let data = null;

function setMediaSize(){
    if (navigator.mediaDevices.getUserMedia) {
        navigator.mediaDevices.getUserMedia({
            audio: false,
            video: {
                width: 9999, 
                height: 9999,
                facingMode: 'environment'
            }            
        }).then(function (stream) {
                const isPortrait = screen.availHeight > screen.availWidth;
                const settings = stream.getVideoTracks()[0].getSettings();
                const width = settings.width;
                const height = settings.height;
                aspectRatio = settings.aspectRatio 
                
                video.srcObject = stream;

                video.width = maxWidth;
                video.aspectRatio = aspectRatio;
                video.height = video.width / aspectRatio;

                canvas.width = video.width;
                canvas.height = video.height;
    
                photo.width = video.width;
                photo.height = video.height;
                // console.log('==============================================================');
                // console.log('Stream width, height, aspectRatio', width, height, aspectRatio);
                // console.log('Stream Settings ', stream.getVideoTracks()[0].getSettings());  
                // console.log('Video width and height ', video.width, video.height);
                
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
    data = canvas.toDataURL('image/jpeg', 0.1);
    context.clearRect(0, 0, width, height);
    socket.emit('image', data);
    // console.log(`<Width , Height> <${width}, ${height}>`);
}, 1000 / FPS);

socket.on('processed_image', function (image) {
    photo.setAttribute('src', image);
});


window.addEventListener('resize', setMediaSize);
// screen.orientation.addEventListener('change', setMediaSize);
setMediaSize();