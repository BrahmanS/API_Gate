$(document).ready(function() {
    // Initialize the carousel
    $('#carouselExampleIndicators').carousel({
        interval: 5000 // Slide interval in milliseconds
    });

    // Toggle navbar visibility on small screens
    $('.navbar-toggler').on('click', function() {
        $('#navbarNav').toggleClass('show');
    });
});
