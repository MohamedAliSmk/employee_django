
document.addEventListener('DOMContentLoaded', function () {
    const birthGovernorateField = document.getElementById('id_birthGovernorateFF');
    const birthDivisionField = document.getElementById('id_birthDivisionFF');

    const addressGovernorateField = document.getElementById('id_addressGovernorateFF');
    const addressDivisionField = document.getElementById('id_addressDivisionFF');

    birthGovernorateField.addEventListener('change', function () {
        const govId = birthGovernorateField.value;

        fetch(`/divisions/${govId}/`)
            .then(response => response.json())
            .then(data => {
                console.log('dataXXXXXXX', data);
                birthDivisionField.innerHTML = '';
                data.forEach(div => {
                    const option = document.createElement('option');
                    option.value = div.id;
                    option.textContent = div.name;
                    birthDivisionField.appendChild(option);
                });
            });
    });

    addressGovernorateField.addEventListener('change', function () {
        const govId = addressGovernorateField.value;

        fetch(`/divisions/${govId}/`)
            .then(response => response.json())
            .then(data => {
                addressDivisionField.innerHTML = '';
                data.forEach(div => {
                    const option = document.createElement('option');
                    option.value = div.id;
                    option.textContent = div.name;
                    addressDivisionField.appendChild(option);
                });
            });
    });
});
