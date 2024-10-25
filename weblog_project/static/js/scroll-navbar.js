// Show and hide navbar on scroll function
(function() {
    let previousScrollPosition = window.pageYOffset;
    const navbar = document.querySelector('nav');

    window.onscroll = function() {
        let currentScrollPosition = window.pageYOffset;
        if (previousScrollPosition > currentScrollPosition) {
            navbar.style.top = "0";
        } else {
            navbar.style.top = "-76.45px";
        }
        previousScrollPosition = currentScrollPosition;
    };
})();
