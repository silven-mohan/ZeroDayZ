/* ZeroDayZ – login pages: small enhancements.
   The form works fully without this script. */
(function () {
  'use strict';

  var form = document.querySelector('.form');
  if (!form) return;

  // Show / hide password
  var password = form.querySelector('#password');
  var toggle = form.querySelector('.field__toggle');
  if (password && toggle) {
    toggle.hidden = false;
    toggle.addEventListener('click', function () {
      var show = password.type === 'password';
      password.type = show ? 'text' : 'password';
      toggle.textContent = show ? 'Hide' : 'Show';
      toggle.setAttribute('aria-pressed', String(show));
      password.focus();
    });
  }

  // Prevent double submits and give feedback
  var button = form.querySelector('.btn');
  var label = button ? button.textContent : '';
  form.addEventListener('submit', function () {
    if (!button) return;
    button.disabled = true;
    button.textContent = 'Signing in…';
  });
  // Restore the button if the person comes back with the browser's back button
  window.addEventListener('pageshow', function () {
    if (button) { button.disabled = false; button.textContent = label; }
  });

  // After a failed server-side check, move focus to the error summary
  var summary = document.getElementById('form-errors');
  if (summary) summary.focus();
})();