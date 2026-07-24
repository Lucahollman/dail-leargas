document.addEventListener("DOMContentLoaded", function () {
    var track = document.getElementById("debate-scroll");
    var buttons = document.querySelectorAll(".carousel-btn");

    if (!track || !buttons.length) return;

    buttons.forEach(function (btn) {
        btn.addEventListener("click", function () {
            var dir = parseInt(btn.dataset.dir, 10) || 1;
            track.scrollBy({ left: dir * 280, behavior: "smooth" });
        });
    });
});