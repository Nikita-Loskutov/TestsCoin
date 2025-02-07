document.getElementById('hour').addEventListener('click', function() {
    const tap = document.getElementById('block_tap');
    const hour = document.getElementById('block_hour');
    tap.style.display = "none";
    hour.style.display = "flex";

});

document.getElementById('tap').addEventListener('click', function() {
    const tap = document.getElementById('block_tap');
    const hour = document.getElementById('block_hour');
    tap.style.display = "flex";
    hour.style.display = "none";

});