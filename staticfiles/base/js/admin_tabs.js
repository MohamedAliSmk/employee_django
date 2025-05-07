document.addEventListener("DOMContentLoaded", function () {
    let adminForm = document.querySelector("#content-main form");
    if (!adminForm) return; // Stop if no form is found
    
    // Ensure this script runs only on the change/edit page
    if (!window.location.pathname.includes("/change/")) {
        return;
    }

    // Create the tab container
    let tabContainer = document.createElement("div");
    tabContainer.className = "admin-tabs-container";
    tabContainer.innerHTML = `
        <ul class="admin-tabs">
            <li class="tab-link active"><a href="#personal-info">البيانات الشخصية</a></li>
            <li class="tab-link"><a href="#employment-info">البيانات الوظيفية</a></li>
            <li class="tab-link"><a href="#employer-info">جهات العمل</a></li>
            <li class="tab-link"><a href="#employeevacation_set-group">الإجازات</a></li>
            <li class="tab-link"><a href="#course_set-group">الدورات والفرق التدريبية</a></li>
            <li class="tab-link"><a href="#penalties-group">الجزاءات</a></li>
            <li class="tab-link"><a href="#secretreport_set-group">التقارير السرية</a></li>
            <li class="tab-link"><a href="#employeeattendance_set-group">الحضور</a></li>
        </ul>
    `;

    // Insert the tabs **before** the form
    adminForm.parentNode.insertBefore(tabContainer, adminForm);

    // Ensure fieldsets have correct IDs
    document.querySelectorAll("fieldset").forEach(fieldset => {
        let classList = fieldset.classList;
        if (classList.contains("personal-info")) fieldset.setAttribute("id", "personal-info");
        else if (classList.contains("employment-info")) fieldset.setAttribute("id", "employment-info");
        else if (classList.contains("employer-info")) fieldset.setAttribute("id", "employer-info");
        else if (classList.contains("leaves-info")) fieldset.setAttribute("id", "employeevacation_set-group");
        else if (classList.contains("course_set-group")) fieldset.setAttribute("id", "course_set-group");
        else if (classList.contains("penalties-group")) fieldset.setAttribute("id", "penalties-group");
        else if (classList.contains("reports-info")) fieldset.setAttribute("id", "secretreport_set-group");
        else if (classList.contains("employeeattendance_set-group")) fieldset.setAttribute("id", "employeeattendance_set-group");
    });

    // Move inline tables inside respective tabs
    let inlines = document.querySelectorAll(".inline-group");
    inlines.forEach(inline => {
        let title = inline.querySelector("h2").innerText.trim();
        if (title.includes("Employment History")) {
            document.getElementById("employer-info").appendChild(inline);
        } else if (title.includes("Course")) {
            document.getElementById("course_set-group").appendChild(inline);
        } else if (title.includes("Penalty")) {
            document.getElementById("penalties-group").appendChild(inline);
        } else if (title.includes("Secret Report")) {
            document.getElementById("secretreport_set-group").appendChild(inline);
        } else if (title.includes("Vacation") || title.includes("إجازة")) {
            document.getElementById("employeevacation_set-group").appendChild(inline);
        }
    });

    // Smooth scroll effect when clicking a tab
    document.querySelectorAll(".tab-link a").forEach(link => {
        link.addEventListener("click", function (event) {
            event.preventDefault();
            let targetId = this.getAttribute("href").substring(1);
            let targetElement = document.getElementById(targetId);
            if (targetElement) {
                window.scrollTo({
                    top: targetElement.offsetTop - 20,
                    behavior: "smooth"
                });
            }
        });
    });
});
