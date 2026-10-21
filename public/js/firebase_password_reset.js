(function () {
  'use strict';
  var form = document.getElementById('reset-form');
  var configElement = document.getElementById('firebase-config');
  var error = document.getElementById('reset-error');
  var message = document.getElementById('reset-message');
  if (!form || !configElement) return;
  form.addEventListener('submit', function (event) {
    event.preventDefault();
    error.hidden = true;
    message.hidden = true;
    var config = JSON.parse(configElement.textContent);
    try {
      if (!firebase.apps.length) firebase.initializeApp(config);
      firebase.auth().sendPasswordResetEmail(document.getElementById('email').value.trim().toLowerCase())
        .then(function () {
          message.textContent = 'If the account exists, a reset link has been sent.';
          message.hidden = false;
        })
        .catch(function () {
          message.textContent = 'If the account exists, a reset link has been sent.';
          message.hidden = false;
        });
    } catch (exception) {
      error.textContent = 'Firebase is not configured.';
      error.hidden = false;
    }
  });
})();
