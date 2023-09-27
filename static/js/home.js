const searchInput = document.getElementById('search-input');
        const assignedMetersList = document.getElementById('assigned-meters-list');

        searchInput.addEventListener('input', function() {
            const searchQuery = searchInput.value.toLowerCase();
            const assignedMeters = document.querySelectorAll('.assigned-meter');

            assignedMeters.forEach(function(meter) {
                const meterText = meter.textContent.toLowerCase();
                if (meterText.includes(searchQuery)) {
                    meter.style.display = 'block';
                } else {
                    meter.style.display = 'none';
                }
            });
        });