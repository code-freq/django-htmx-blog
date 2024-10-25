// Display message in message area on page load
document.body.addEventListener('htmx:afterOnLoad', function(evt) {
    const Message = document.querySelector('#message');
    if (Message) {
        document.querySelector('#message-area').innerHTML = Message.innerHTML;
        Message.remove();
    }
});