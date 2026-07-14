document.addEventListener("DOMContentLoaded", function () {
    var searchInput = document.getElementById("search-input");
    var resultCount = document.getElementById("result-count");
    var rows = document.querySelectorAll("#entries-list .entry-row");
 
    function applyFilter() {
        var query = searchInput.value.trim().toLowerCase();
        var visible = 0;
        rows.forEach(function (row) {
            var show = row.dataset.search.indexOf(query) !== -1;
            row.style.display = show ? "flex" : "none";
            if (show) visible += 1;
        });
        resultCount.textContent = visible + (visible === 1 ? " result" : " results");
    }
 
    searchInput.addEventListener("input", applyFilter);
    applyFilter();
});
 