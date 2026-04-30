document.addEventListener('DOMContentLoaded', function () {

  const phoneInput = document.getElementById('phone');
  if (phoneInput) {
    phoneInput.addEventListener('input', function (e) {
      let val = e.target.value.replace(/\D/g, '');
      if (val.length > 11) val = val.substring(0, 11);
      let formatted = '8(';
      if (val.length > 0) formatted += val.substring(1, 4);
      if (val.length >= 4) formatted += ')' + val.substring(4, 7);
      if (val.length >= 7) formatted += '-' + val.substring(7, 9);
      if (val.length >= 9) formatted += '-' + val.substring(9, 11);
      e.target.value = formatted;
    });
  }

  const statusForms = document.querySelectorAll('.status-form');
  statusForms.forEach(function (form) {
    form.addEventListener('submit', function (e) {
      const select = form.querySelector('select');
      const newStatus = select.options[select.selectedIndex].text;
      const confirmed = confirm('Сменить статус на "' + newStatus + '"?');
      if (!confirmed) e.preventDefault();
    });
  });

  const errorEl = document.querySelector('.error');
  if (errorEl) {
    setTimeout(function () {
      errorEl.style.transition = 'opacity 0.5s';
      errorEl.style.opacity = '0';
      setTimeout(function () { errorEl.remove(); }, 500);
    }, 5000);
  }
});