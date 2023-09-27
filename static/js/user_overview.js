
        function showPasswordInput() {
            const deleteUserForm = document.getElementById('deleteUserForm');
            deleteUserForm.style.display = 'block';
        }

    const searchMeterInputAssigned = document.getElementById('search-meter-input-assigned');
    const meterListAssigned = document.getElementById('meter-list-assigned');
    const meterItemsAssigned = meterListAssigned.querySelectorAll('.meter-item');

    searchMeterInputAssigned.addEventListener('input', function() {
        const searchTermAssigned = searchMeterInputAssigned.value.toLowerCase();

        meterItemsAssigned.forEach(function(item) {
            const meterNumberAssigned = item.textContent.trim().toLowerCase();
            if (meterNumberAssigned.includes(searchTermAssigned)) {
                item.style.display = 'block';
            } else {
                item.style.display = 'none';
            }
        });
    });

    const searchMeterInput2 = document.getElementById('search-meter-input-2');
    const meterList2 = document.getElementById('meter-list-2');
    const meterItems2 = meterList2.querySelectorAll('.meter-item');

    searchMeterInput2.addEventListener('input', function() {
        const searchTerm2 = searchMeterInput2.value.toLowerCase();

        meterItems2.forEach(function(item) {
            const meterNumber2 = item.textContent.trim().toLowerCase();
            if (meterNumber2.includes(searchTerm2)) {
                item.style.display = 'block';
            } else {
                item.style.display = 'none';
            }
        });
    });

function confirmDelete(meterId) {
    if (confirm("Czy chcesz usunąć ten licznik?")) {
        window.location.href = '/remove_meter/' + meterId;
    }
}

    document.addEventListener('DOMContentLoaded', function () {
        const editNotesButton = document.getElementById('edit-notes-button');
        const notesEditField = document.getElementById('notes-edit-field');

        editNotesButton.addEventListener('click', function () {
            if (notesEditField.style.display === 'none') {
                notesEditField.style.display = 'block';
            } else {
                notesEditField.style.display = 'none';
            }
        });
    });
