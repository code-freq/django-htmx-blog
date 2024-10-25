// Get the url from data-url attribute of the element and redirect to it
function goToLink(element) {
    const url = element.getAttribute('data-url');
    window.location.href = url;
}