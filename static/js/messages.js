const senderFilter = document.getElementById('sender-filter');
    const subjectFilter = document.getElementById('subject-filter');
    const senderList = document.getElementById('sender-list');
    const messages = document.querySelectorAll('tbody tr');

    senderFilter.addEventListener('input', function() {
      filterMessages();
    });

    subjectFilter.addEventListener('input', function() {
      filterMessages();
    });

    function filterMessages() {
      const senderValue = senderFilter.value.toLowerCase();
      const subjectValue = subjectFilter.value.toLowerCase();

      messages.forEach(message => {
        const sender = message.querySelector('td:nth-child(1)').textContent.toLowerCase();
        const subject = message.querySelector('td:nth-child(2)').textContent.toLowerCase();
        const senderCheckbox = senderList.querySelector(`#sender-${sender}`);

        if (sender.includes(senderValue) && subject.includes(subjectValue)) {
          message.style.display = 'table-row';
          senderCheckbox.style.display = 'block';
        } else {
          message.style.display = 'none';
          senderCheckbox.style.display = 'none';
        }
      });
    }