document.addEventListener("DOMContentLoaded", function () {
    const sectionIds = [
        "personal-info",
        "employment-info",
        "employer-info",
        "course_set-group",
        "employeevacation_set-group",
        "penalties-group",
        "secretreport_set-group",
        "employeeattendance_set-group"
    ];

    sectionIds.forEach(id => {
        const section = document.getElementById(id);
        if (section) {
            const printContainer = document.createElement("div");
            printContainer.style.marginBottom = "10px";

            // إضافة الفلاتر فقط للإجازات والحضور
            if (["employeevacation_set-group", "employeeattendance_set-group"].includes(id)) {
                const fromWrapper = document.createElement("div");
                fromWrapper.style.display = "inline-block";
                fromWrapper.style.marginRight = "10px";
                fromWrapper.style.textAlign = "right";
            
                const fromLabel = document.createElement("label");
                fromLabel.innerText = "من تاريخ";
                fromLabel.style.display = "block";
                fromLabel.style.fontSize = "13px";
                fromLabel.style.marginBottom = "2px";
            
                const fromDate = document.createElement("input");
                fromDate.type = "date";
                fromDate.className = "print-filter";
                fromDate.style.cssText = `
                    padding: 6px 10px;
                    border: 1px solid #ccc;
                    border-radius: 4px;
                    font-size: 14px;
                `;
            
                fromWrapper.appendChild(fromLabel);
                fromWrapper.appendChild(fromDate);
            
                const toWrapper = document.createElement("div");
                toWrapper.style.display = "inline-block";
                toWrapper.style.marginRight = "10px";
                toWrapper.style.textAlign = "right";
            
                const toLabel = document.createElement("label");
                toLabel.innerText = "إلى تاريخ";
                toLabel.style.display = "block";
                toLabel.style.fontSize = "13px";
                toLabel.style.marginBottom = "2px";
            
                const toDate = document.createElement("input");
                toDate.type = "date";
                toDate.className = "print-filter";
                toDate.style.cssText = `
                    padding: 6px 10px;
                    border: 1px solid #ccc;
                    border-radius: 4px;
                    font-size: 14px;
                `;
            
                toWrapper.appendChild(toLabel);
                toWrapper.appendChild(toDate);
            
                printContainer.appendChild(fromWrapper);
                printContainer.appendChild(toWrapper);
            }
            
            

            const printBtn = document.createElement("button");
            printBtn.innerText = "🖨️ طباعة";
            printBtn.className = "print-section-btn";
            printBtn.style.cssText = `
                background-color: #007bff;
                color: white;
                border: none;
                padding: 6px 12px;
                border-radius: 4px;
                cursor: pointer;
            `;

            printBtn.onclick = function (e) {
                e.preventDefault();
                const employeeId = window.location.pathname.split("/").filter(Boolean).slice(-2, -1)[0];

                const sectionKeyMap = {
                    "personal-info": "personal",
                    "employment-info": "employment",
                    "employer-info": "employer",
                    "course_set-group": "course_set",
                    "employeevacation_set-group": "employeevacation_set",
                    "penalties-group": "penalties",
                    "secretreport_set-group": "secretreport_set",
                    "employeeattendance_set-group": "employeeattendance_set"
                };

                const sectionKey = sectionKeyMap[id];
                if (!sectionKey) return alert("No print format for this section");

                // جمع بيانات الفلاتر إن وجدت
                const filters = section.querySelectorAll(".print-filter");
                const params = new URLSearchParams();
                if (filters.length === 2) {
                    if (filters[0].value) params.append("from_date", filters[0].value);
                    if (filters[1].value) params.append("to_date", filters[1].value);
                }

                openCustomPrint(employeeId, sectionKey, params.toString());
            };

            printContainer.appendChild(printBtn);
            section.insertBefore(printContainer, section.firstChild);
        }
    });

    function openCustomPrint(employeeId, section, queryString = "") {
        let url = `/employee/${employeeId}/print/${section}/`;
        if (queryString) {
            url += `?${queryString}`;
        }
        window.open(url, '_blank');
    }
});