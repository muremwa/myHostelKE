// requires jQuery 😞😞😞😞
$(function () {
    $('[data-toggle="tooltip"]').tooltip();
});

const acceptCookies = document.getElementById('accept-cookie');
acceptCookies.addEventListener('imageOpened', () => {
    acceptCookies.href = acceptCookies.dataset.ogLink + window.location.pathname + window.location.search + window.location.hash;
});