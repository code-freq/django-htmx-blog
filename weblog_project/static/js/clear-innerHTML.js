// Clear innerHTML of an element
function clearInnerHTML(elementId) {
    const element = document.getElementById(elementId);
    if (element) {
        element.innerHTML = '';
    }
}