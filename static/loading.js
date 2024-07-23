document.addEventListener('DOMContentLoaded', () => {
    const animation = lottie.loadAnimation({
        container: document.getElementById('loading-animation'),
        renderer: 'svg',
        loop: true,
        autoplay: true,
        path: '/static/loading_animation.json'
    });
});