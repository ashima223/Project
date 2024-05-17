document.addEventListener("DOMContentLoaded", function() {
    var videoElement = document.getElementById('myVideo');
  
    var observer = new IntersectionObserver((entries, observer) => { 
      entries.forEach(entry => {
        if(entry.isIntersecting){
          videoElement.play();
        } else {
          videoElement.pause();
        }
      });
    }, {threshold: 0.5}); // Adjust threshold based on when you want the video to start playing
  
    observer.observe(videoElement);
  });