function toggleMenu() {
    const menu = document.getElementById("dropdownMenu");
    if (menu.classList.contains("hidden")) {
        menu.classList.remove("hidden");
    } else {
        menu.classList.add("hidden");
    }
}