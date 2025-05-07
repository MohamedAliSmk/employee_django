document.addEventListener('DOMContentLoaded', function () {
    // Check if we are on the Employee change page
    if (!window.location.pathname.includes('/admin/base/employee/')) {
        return; // exit if we're not on the Employee admin page
    }

    // Delay to make sure Django has rendered calendar elements
    setTimeout(function () {
        // Hide the "Today" link (Arabic and English)
        document.querySelectorAll('.datetimeshortcuts a').forEach(function (link) {
            if (link.innerText.trim() === "اليوم" || link.innerText.trim() === "Today") {
                link.style.display = 'none';
            }
        });

        // Hide the calendar icons (calendarlink...)
        document.querySelectorAll('.datetimeshortcuts .date-icon').forEach(function (icon) {
            icon.style.display = 'none';
        });

        // Optional: hide the entire date shortcuts section
        // document.querySelectorAll('.datetimeshortcuts').forEach(function (shortcut) {
        //     shortcut.style.display = 'none';
        // });

    }, 500);
});
