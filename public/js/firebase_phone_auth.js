(function () {
  'use strict';

  var form = document.querySelector('.form');
  var configElement = document.getElementById('firebase-config');
  var otpField = document.getElementById('otp-field');
  var otpInput = document.getElementById('otp');
  var tokenInput = document.getElementById('firebase_id_token');
  var otpError = document.getElementById('otp-error');
  var button = form && form.querySelector('.btn');
  if (!form || !configElement || !otpField || !otpInput || !tokenInput) return;

  var confirmationResult = null;
  var verified = false;
  var config = JSON.parse(configElement.textContent);

  function showError(message) {
    otpError.textContent = message;
    otpError.hidden = false;
  }

  function clearError() {
    otpError.textContent = '';
    otpError.hidden = true;
  }

  function normalizePhone(value) {
    var digits = value.replace(/\D/g, '');
    return digits.length === 10 ? '+91' + digits : value.trim();
  }

  function setButton(text, disabled) {
    if (button) {
      button.textContent = text;
      button.disabled = disabled;
    }
  }

  form.addEventListener('submit', function (event) {
    if (verified || confirmationResult) return;
    event.preventDefault();
    clearError();

    if (!config.apiKey || !config.projectId) {
      showError('Firebase is not configured. Add the Firebase web settings first.');
      return;
    }
    if (!form.checkValidity()) {
      form.reportValidity();
      return;
    }

    var phone = normalizePhone(document.getElementById('mobile_number').value);
    if (!/^\+[1-9]\d{7,14}$/.test(phone)) {
      showError('Enter a valid international mobile number.');
      return;
    }

    try {
      if (!firebase.apps.length) firebase.initializeApp(config);
      var auth = firebase.auth();
      if (!window.recaptchaVerifier) {
        window.recaptchaVerifier = new firebase.auth.RecaptchaVerifier('recaptcha-container', {
          size: 'invisible',
          callback: function () {}
        });
      }
      setButton('Sending code...', true);
      auth.signInWithPhoneNumber(phone, window.recaptchaVerifier)
        .then(function (result) {
          confirmationResult = result;
          otpField.hidden = false;
          otpInput.required = true;
          otpInput.focus();
          setButton('Verify number and create account', false);
        })
        .catch(function (error) {
          showError(error.message || 'Firebase could not send the verification code.');
          setButton('Create account', false);
          if (window.recaptchaVerifier) window.recaptchaVerifier.render();
        });
    } catch (error) {
      showError('Firebase could not start phone verification.');
      setButton('Create account', false);
    }
  });

  otpInput.addEventListener('input', function () {
    otpInput.value = otpInput.value.replace(/\D/g, '').slice(0, 6);
    clearError();
  });

  otpInput.form.addEventListener('submit', function (event) {
    if (verified || !confirmationResult || otpInput.value.length !== 6) return;
    event.preventDefault();
    setButton('Verifying...', true);
    confirmationResult.confirm(otpInput.value)
      .then(function (result) {
        return result.user.getIdToken();
      })
      .then(function (token) {
        tokenInput.value = token;
        verified = true;
        form.submit();
      })
      .catch(function () {
        showError('That Firebase code is invalid or expired.');
        setButton('Verify number and create account', false);
      });
  });
})();
