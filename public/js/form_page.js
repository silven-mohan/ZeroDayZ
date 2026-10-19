/* ZeroDayZ – student feedback / suggestions: small enhancements.
   The forms work fully without this script. */
(function () {
  'use strict';

  var form = document.querySelector('.form');
  if (!form) return;

  // Live character counts: <textarea> + <p> containing [data-count]
  form.querySelectorAll('textarea').forEach(function (area) {
    var out = form.querySelector('#' + area.id + '-count [data-count]');
    if (!out) return;
    var update = function () { out.textContent = area.value.length; };
    area.addEventListener('input', update);
    update();
  });

  // Prevent double submits and give feedback
  var button = form.querySelector('.btn');
  var label = button ? button.textContent : '';
  form.addEventListener('submit', function () {
    if (!button) return;
    button.disabled = true;
    button.textContent = 'Sending…';
  });
  window.addEventListener('pageshow', function () {
    if (button) { button.disabled = false; button.textContent = label; }
  });

  // After a failed server-side check, move focus to the error summary
  var summary = document.getElementById('form-errors');
  if (summary) summary.focus();
})();