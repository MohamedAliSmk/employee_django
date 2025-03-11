document.addEventListener("DOMContentLoaded", function () {
    const employerField = document.querySelector("#id_currentEmployerFF");
    const sectionField = document.querySelector("#id_currentEmployerSectionFF");

    if (employerField) {
        employerField.addEventListener("change", function () {
            const employerId = employerField.value;
            console.log("Employer selected:", employerId);  // Debugging

            fetch(`/admin/api/get_sections/?employer_id=${employerId}`)
                .then(response => response.json())
                .then(data => {
                    console.log("Received Sections:", data);  // Debugging

                    sectionField.innerHTML = ""; // Clear previous options
                    data.sections.forEach(section => {
                        const option = new Option(section.name, section.id);
                        sectionField.add(option);
                    });
                })
                .catch(error => console.error("Error fetching sections:", error));
        });
    }
});
