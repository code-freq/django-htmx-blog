// Set random colors to elements with class "title" and "username"
function getRandomColor() {
    let letters = '0123456789ABCDEF';
    let color = '#';
    for (let i = 0; i < 6; i++) {
        color += letters[Math.floor(Math.random() * 16)];
    }
    return color;
}
document.addEventListener('DOMContentLoaded', function() {
    const titles = document.querySelectorAll('.title, .username');

    titles.forEach(function(title) {
        title.style.color = getRandomColor();
    });
});