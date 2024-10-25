// Update file name (Selected file name or Not chosen yet)
function updateFileName() {
    var input = document.getElementById('profile_picture');
    var fileName = input.files[0]?.name || 'Not chosen yet';
    document.querySelector('.file-chosen').innerText = fileName;
}