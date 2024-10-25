// Search for the 'from' parameter in the URL and scroll to the bottom of the page if it is 'comments'
window.onload = function() {
    const urlParams = new URLSearchParams(window.location.search);
    const fromParam = urlParams.get('from');
    if (fromParam == 'comments') {
        window.scrollTo(0, document.body.scrollHeight - 800);
    }
}