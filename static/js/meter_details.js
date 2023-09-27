
    var readings = {{ readings|tojson }};

    var readingsList = readings.map(function(reading) {
        return { date: new Date(reading.date), reading: reading.reading };
    });

    readingsList.sort(function(a, b) {
        return a.date - b.date;
    });

    var dates = readingsList.map(function(reading) { return reading.date; });
var values = readingsList.map(function(reading) { return reading.reading; });


    var lineTrace = {
        x: readingsList.map(function(reading) { return reading.date; }),
        y: readingsList.map(function(reading) { return reading.reading; }),
        mode: 'lines+markers',
        type: 'scatter'
    };

    var barTrace = {
        x: readingsList.map(function(reading) { return reading.date; }),
        y: readingsList.map(function(reading) { return reading.reading; }),
        type: 'bar'
    };

    var layout = {
        xaxis: {
            title: 'Data',
            rangeselector: {
                buttons: [
                    {count: 1, label: '1D', step: 'day', stepmode: 'backward'},
                    {count: 1, label: '1M', step: 'month', stepmode: 'backward'},
                    {count: 6, label: '6M', step: 'month', stepmode: 'backward'},
                    {count: 1, label: '1R', step: 'year', stepmode: 'backward'},
                    {step: 'all'}
                ]
            },
            rangeslider: {},
            type: 'date'
        },
        yaxis: {
            title: {% if meter.type == "water" %}'Objętość [m³]'{% elif meter.type == "heat" %}'Energia [GJ]'{% endif %}
        }
    };

    var lineData = [lineTrace];
    var barData = [barTrace];

    var chartContainer = document.getElementById('chart-container');
    var tableContainer = document.getElementById('table-container');

    var selectedStartDate = null;
    var selectedEndDate = null;

    function updateChartAndTable() {
    const startDate = new Date(startDateInput.value);
    const endDate = new Date(endDateInput.value);
    selectedStartDate = startDate;
    selectedEndDate = endDate;

    updateChart(startDate, endDate);
    updateTable();
}

function updateChart(startDate, endDate) {
    const filteredReadings = readingsList.filter(function(reading) {
        return reading.date >= startDate && reading.date <= endDate;
    });

    const updatedDates = filteredReadings.map(function(reading) { return reading.date; });
    const updatedValues = filteredReadings.map(function(reading) { return reading.reading; });

    const updatedLineTrace = {
        x: updatedDates,
        y: updatedValues,
        mode: 'lines+markers',
        type: 'scatter'
    };

    const updatedBarTrace = {
        x: updatedDates,
        y: updatedValues,
        type: 'bar'
    };



    const updatedLineData = [updatedLineTrace];
    const updatedBarData = [updatedBarTrace];

    Plotly.react(chartContainer, updatedLineData, layout);
}

function updateTable() {
    var filteredReadings = readingsList;

    if (selectedStartDate && selectedEndDate) {
        filteredReadings = readingsList.filter(function(reading) {
            return reading.date >= selectedStartDate && reading.date <= selectedEndDate;
        });
    }

    var tableHTML = '<table class="table"><thead><tr><th>Data</th><th>' + getReadingUnit() + '</th></tr></thead><tbody>';
    filteredReadings.forEach(function(reading) {
        tableHTML += '<tr><td>' + formatDateForTable(reading.date) + '</td><td>' + reading.reading + '</td></tr>';
    });
    tableHTML += '</tbody></table>';
    tableContainer.innerHTML = tableHTML;
}

    function formatDateForTable(date) {
        var options = { year: 'numeric', month: 'long', day: '2-digit', hour: '2-digit', minute: '2-digit' };
        return date.toLocaleString('pl-PL', options);
    }

    function getReadingUnit() {
        return {% if meter.type == "water" %}'Objętość [m³]'{% elif meter.type == "heat" %}'Energia [GJ]'{% endif %};
    }

    // Dodaj wykres liniowy i tabelę
    Plotly.newPlot(chartContainer, [lineTrace], layout);
    updateTable(readingsList);

    var rangeslider = document.querySelector('.rangeslider');
if (rangeslider) {
    rangeslider.classList.add('no-print');
}

    // Obsługa suwaka zakresu
    const startDateInput = document.getElementById('start-date');
    const endDateInput = document.getElementById('end-date');
    const updateButton = document.getElementById('update-chart');
    const lineChartButton = document.getElementById('line-chart-button');
    const barChartButton = document.getElementById('bar-chart-button');
    const tableButton = document.getElementById('table-button');
    const updateTableButton = document.getElementById('update-table-button');

    startDateInput.addEventListener('change', function() {
        selectedStartDate = new Date(startDateInput.value);
        updateChartAndTable();
    });

    endDateInput.addEventListener('change', function() {
        selectedEndDate = new Date(endDateInput.value);
        updateChartAndTable();
    });

    updateButton.addEventListener('click', updateChartAndTable);

    lineChartButton.addEventListener('click', function() {
        Plotly.react(chartContainer, lineData, layout);
        updateTable(readingsList);
    });

    barChartButton.addEventListener('click', function() {
        Plotly.react(chartContainer, barData, layout);
        updateTable(readingsList);
    });

    tableButton.addEventListener('click', function() {
        updateTable(readingsList);
        Plotly.purge(chartContainer);
    });

    updateTableButton.addEventListener('click', function() {
        updateChartAndTable();
    });



    // Wywołaj funkcję po załadowaniu strony


        document.addEventListener("DOMContentLoaded", function () {
            const meterName = document.getElementById("meter-name");
            const editForm = document.getElementById("edit-form");
            const editButton = document.getElementById("edit-button");

            editButton.addEventListener("click", function () {
                meterName.classList.add("hidden");
                editForm.classList.remove("hidden");
            });
        });


        function goBack() {
            window.history.back();
        }

        // Dodany przycisk "Wyeksportuj do CSV"

    function formatDateForCSV(date) {
        var day = ('0' + date.getDate()).slice(-2);
        var month = ('0' + (date.getMonth() + 1)).slice(-2);
        var year = date.getFullYear();
        var hours = ('0' + date.getHours()).slice(-2);
        var minutes = ('0' + date.getMinutes()).slice(-2);
        return day + '-' + month + '-' + year + ' ' + hours + ':' + minutes;
    }

        const exportCsvButton = document.getElementById('export-csv-button');

        exportCsvButton.addEventListener('click', function() {
        exportToCsv(readingsList);
    });

        function exportToCsv(readingsList) {
        var csvContent = "data:text/csv;charset=utf-8," +
            "Date,Reading\n" +
            readingsList.map(reading => `${formatDateForCSV(reading.date)},${reading.reading}`).join("\n");

        var encodedUri = encodeURI(csvContent);
        var link = document.createElement("a");
        link.setAttribute("href", encodedUri);
        link.setAttribute("download", "readings.csv");
        document.body.appendChild(link); // Required for Firefox
        link.click();
        document.body.removeChild(link);
    }

    const addAddressButton = document.getElementById('add-address-button');
    const editAddressButton = document.getElementById('edit-address-button');
    const addressForm = document.getElementById('address-form');

    addAddressButton.addEventListener('click', function () {
        addressForm.classList.remove('hidden');
        addAddressButton.classList.add('hidden');
    });

    editAddressButton.addEventListener('click', function () {
        addressForm.classList.remove('hidden');
    });
