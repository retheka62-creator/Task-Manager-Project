// Dark/light mode toggle using localStorage + theme switch
function setTheme(dark) {
    const root = document.getElementById("main-root") || document.body;
    if (dark) {
        root.classList.add('dark');
        document.documentElement.classList.add('dark');
        localStorage.setItem('theme', 'dark');
        document.getElementById('theme-icon') && (document.getElementById('theme-icon').innerHTML = '🌞');
    } else {
        root.classList.remove('dark');
        document.documentElement.classList.remove('dark');
        localStorage.setItem('theme', 'light');
        document.getElementById('theme-icon') && (document.getElementById('theme-icon').innerHTML = '🌙');
    }
}
// Load saved theme
(function(){
    let preferred = (localStorage.getItem('theme') || "light") === "dark";
    setTheme(preferred);
})();
document.addEventListener("DOMContentLoaded", function() {
    var themeBtn = document.getElementById('theme-toggle');
    if (themeBtn) {
        themeBtn.onclick = function() {
            let dark = !(document.getElementById("main-root")?.classList.contains('dark'));
            setTheme(dark);
        };
    }

    // Filtering/search
    const table = document.getElementById("tasks-table");
    if (table) {
        function filterTable() {
            let q = (document.getElementById("task-search").value || "").toLowerCase();
            let status = document.getElementById("status-filter").value;
            let priority = document.getElementById("priority-filter").value;
            Array.from(table.querySelectorAll("tbody tr")).forEach(tr => {
                let show = true;
                let title = (tr.getAttribute("data-title") || "");
                let desc = (tr.getAttribute("data-desc") || "");
                let taskStatus = tr.getAttribute("data-status");
                let taskPrio = tr.getAttribute("data-priority");
                // Search
                if (q && !(title.includes(q) || desc.includes(q)))
                    show = false;
                // Status
                if (status !== "all" && taskStatus !== status)
                    show = false;
                // Priority
                if (priority !== "all" && taskPrio !== priority)
                    show = false;
                tr.style.display = show ? "" : "none";
            });
        }
        document.getElementById("apply-filters").onclick = filterTable;
        document.getElementById("status-filter").onchange = filterTable;
        document.getElementById("priority-filter").onchange = filterTable;
        document.getElementById("task-search").oninput = function(e) { if (e.target.value === "") filterTable(); };
        // Autofilter at page load for prefilled status
        filterTable();
    }
});