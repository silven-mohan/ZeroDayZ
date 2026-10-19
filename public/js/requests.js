/* ZeroDayZ – requests page: stop double taps on Accept / Decline.
   The page works fully without this script. */
(function () {
  'use strict';

  var forms = document.querySelectorAll('.ticket');
  forms.forEach(function (form) {
    form.addEventListener('submit', function () {
      var buttons = form.querySelectorAll('.act');
      // wait a tick so the browser still sends the button that was pressed
      setTimeout(function () {
        buttons.forEach(function (b) { b.disabled = true; });
      }, 0);
    });
  });

  // Re-enable the buttons if the person comes back with the browser's back button
  window.addEventListener('pageshow', function () {
    document.querySelectorAll('.act').forEach(function (b) { b.disabled = false; });
  });
})();