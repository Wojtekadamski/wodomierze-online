const summaryForm = document.getElementById('summary-form');
        const tableContainer = document.getElementById('tableContainer');

        summaryForm.addEventListener('submit', async (event) => {
            event.preventDefault();

            const formData = new FormData(summaryForm);
            const address = formData.get('address');
            const startDate = formData.get('startDate');
            const endDate = formData.get('endDate');

            // Fetch data based on user's selections and display the result
            const response = await fetch(`/get_summary_results?address=${address}&startDate=${startDate}&endDate=${endDate}`);
            const data = await response.json();

            // Generate table HTML
            let tableHTML = '<table>';
            tableHTML += '<tr><th>Adres</th><th>Nr Radiowy Licznika</th>';
            // Add header cells for each month in the date range
            let currentDate = new Date(startDate);
            while (currentDate <= new Date(endDate)) {
                const monthYear = `${currentDate.getMonth() + 1}/${currentDate.getFullYear()}`;
                tableHTML += `<th>${monthYear}</th>`;
                currentDate.setMonth(currentDate.getMonth() + 1);
            }
            tableHTML += '</tr>';

            // Add rows and cells for measurements
            data.forEach(entry => {
                tableHTML += '<tr>';
                tableHTML += `<td>${entry.address}</td>`;
                tableHTML += `<td>${entry.radio_number}</td>`;
                // Add measurement cells for each month in the date range
                currentDate = new Date(startDate);
                while (currentDate <= new Date(endDate)) {
                    const monthYear = `${currentDate.getMonth() + 1}/${currentDate.getFullYear()}`;
                    const measurement = entry.measurements[monthYear] || '';
                    tableHTML += `<td>${measurement}</td>`;
                    currentDate.setMonth(currentDate.getMonth() + 1);
                }
                tableHTML += '</tr>';
            });

            tableHTML += '</table>';
            tableContainer.innerHTML = tableHTML;
        });