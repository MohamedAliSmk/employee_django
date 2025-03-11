document.addEventListener("DOMContentLoaded", function () {
    function togglePlaceFields() {
        var typeField = document.querySelector("#id_type") || document.querySelector("#id_status") ;
        var placeTextField = document.querySelector("#id_place_text").closest(".form-row");
        var placeLinkField = document.querySelector("#id_place_link").closest(".form-row");
        var placeLinkSectionField = document.querySelector("#id_section_place_link").closest(".form-row");

        if (!typeField || !placeTextField || !placeLinkField || !placeLinkSectionField) return;

        // Get the selected value
        var selectedValue = typeField.value;

        // Hide both fields initially
        placeTextField.style.display = "none";
        placeLinkField.style.display = "none";
        placeLinkSectionField.style.display = "none";

        // Show the relevant field based on selection
        if (selectedValue === "Outside Mission" || selectedValue ==="OMS") {
            placeTextField.style.display = "block";
        } else if (selectedValue === "Inside Mission" || selectedValue ==="IMS") {
            placeLinkField.style.display = "block";
            placeLinkSectionField.style.display = "block";
        }
    }

    // Run on page load
    togglePlaceFields();

    // Listen for changes in the "type" dropdown
    var typeField = document.querySelector("#id_type") || document.querySelector("#id_status");
    if (typeField) {
        typeField.addEventListener("change", togglePlaceFields);
    }
});
