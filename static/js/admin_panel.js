
        const searchMeterInput = document.getElementById('search-meter-input');
        const meterList = document.getElementById('meter-list');

        searchMeterInput.addEventListener('input', function() {
            const searchTerm = searchMeterInput.value.toLowerCase();
            const meterItems = meterList.querySelectorAll('.meter-item');

            meterItems.forEach(function(item) {
                const meterNumber = item.textContent.trim().toLowerCase();
                if (meterNumber.includes(searchTerm)) {
                    item.style.display = 'block';
                } else {
                    item.style.display = 'none';
                }
            });
        });

        const showUserFormBtn = document.getElementById("showUserForm");
        const hideUserFormBtn = document.getElementById("hideUserForm");
        const userForm = document.getElementById("userForm");

        showUserFormBtn.addEventListener("click", function () {
            userForm.style.display = "block";
            this.style.display = "none";
            hideUserFormBtn.style.display = "block";
        });

        hideUserFormBtn.addEventListener("click", function () {
            userForm.style.display = "none";
            this.style.display = "none";
            showUserFormBtn.style.display = "block";
        });

    const searchUserInput = document.getElementById('search-user-input');
    const userList = document.getElementById('user-list');

    searchUserInput.addEventListener('input', function() {
        const searchTerm = searchUserInput.value.toLowerCase();
        const userItems = userList.querySelectorAll('.user-item');

        userItems.forEach(function(item) {
            const userEmail = item.textContent.trim().toLowerCase();
            if (userEmail.includes(searchTerm)) {
                item.style.display = 'block';
            } else {
                item.style.display = 'none';
            }
        });
    });
