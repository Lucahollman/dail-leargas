document.addEventListener("DOMContentLoaded", function () {
    var searchInput = document.getElementById("search-input");
    var resultCount = document.getElementById("result-count");
    var rail = document.getElementById("date-rail");
    var entriesList = document.getElementById("entries-list");
    var pills = document.querySelectorAll(".filter-pill");
    var rows = entriesList.querySelectorAll(".entry-row");
    var railItems = rail.querySelectorAll(".rail-item");
 
    var activeCategory = "all";
    var activeDate = "all";
 
    function setActiveDateVisual() {
        railItems.forEach(function (item) {
            item.classList.toggle("is-active", item.dataset.date === activeDate);
        });
    }
 
    function applyFilters() {
        var query = searchInput.value.trim().toLowerCase();
        var visible = 0;
        var matchedDates = {};
 
        rows.forEach(function (row) {
            var matchesCategory = activeCategory === "all" || row.dataset.category === activeCategory;
            var matchesQuery = row.dataset.title.indexOf(query) !== -1;
            var matchesDate = activeDate === "all" || row.dataset.date === activeDate;
            var show = matchesCategory && matchesQuery && matchesDate;
            row.style.display = show ? "flex" : "none";
            if (show) {
                visible += 1;
                matchedDates[row.dataset.date] = true;
            }
        });
 
        resultCount.textContent = visible + (visible === 1 ? " result" : " results");
 
        railItems.forEach(function (item) {
            if (item.dataset.date === "all") return;
            var hasMatch = matchedDates[item.dataset.date];
            if (activeDate !== "all") {
                item.classList.toggle("is-dim", item.dataset.date !== activeDate);
            } else if (query) {
                item.classList.toggle("is-dim", !hasMatch);
            } else {
                item.classList.remove("is-dim");
            }
        });
    }
 
    rail.addEventListener("click", function (event) {
        var item = event.target.closest(".rail-item");
        if (!item) return;
        activeDate = item.dataset.date;
        setActiveDateVisual();
        applyFilters();
    });
 
    searchInput.addEventListener("input", function () {
        if (searchInput.value.trim() && activeDate !== "all") {
            activeDate = "all";
            setActiveDateVisual();
        }
        applyFilters();
    });
 
    pills.forEach(function (pill) {
        pill.addEventListener("click", function () {
            pills.forEach(function (p) { p.classList.remove("is-active"); });
            pill.classList.add("is-active");
            activeCategory = pill.dataset.cat;
            applyFilters();
        });
    });
 
    applyFilters();
});