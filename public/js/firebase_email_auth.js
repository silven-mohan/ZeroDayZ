(function () {
  'use strict';

  var form = document.querySelector('.form');
  var configElement = document.getElementById('firebase-config');
  var tokenInput = document.getElementById('firebase_id_token');
  var errorElement = document.getElementById('firebase-error');
  var button = form && form.querySelector('.btn');
  if (!form || !configElement || !tokenInput || !errorElement) return;

  var verified = false;
  var verificationSent = false;
  var config = JSON.parse(configElement.textContent);

  function showError(message) {
    errorElement.textContent = message;
    errorElement.hidden = false;
  }

  function setButton(text, disabled) {
    if (button) {
      button.textContent = text;
      button.disabled = disabled;
    }
  }

  function firebaseErrorMessage(error) {
    var code = error && error.code ? error.code : '';
    var messages = {
      'auth/operation-not-allowed': 'Enable Email/Password sign-in in Firebase Authentication.',
      'auth/email-already-in-use': 'That email is already registered.',
      'auth/invalid-email': 'Enter a valid email address.',
      'auth/weak-password': 'Use a stronger password.',
      'auth/too-many-requests': 'Too many attempts. Wait and try again later.'
    };
    return messages[code] || (error && error.message) || 'Firebase email verification failed.';
  }

  function initialize() {
    if (!config.apiKey || !config.projectId) {
      showError('Firebase is not configured. Add the Firebase web settings first.');
      return null;
    }
    if (!firebase.apps.length) firebase.initializeApp(config);
    return firebase.auth();
  }

  form.addEventListener('submit', function (event) {
    if (verified) return;
    event.preventDefault();
    errorElement.hidden = true;

    if (!form.checkValidity()) {
      form.reportValidity();
      return;
    }

    var auth;
    try {
      auth = initialize();
      if (!auth) return;
    } catch (error) {
      showError(firebaseErrorMessage(error));
      return;
    }

    var email = document.getElementById('email').value.trim().toLowerCase();
    var password = document.getElementById('password').value;
    setButton(verificationSent ? 'Checking verification...' : 'Sending verification email...', true);

    if (!verificationSent) {
      auth.createUserWithEmailAndPassword(email, password)
        .then(function (result) {
          return result.user.sendEmailVerification();
        })
        .then(function () {
          verificationSent = true;
          setButton('I verified my email', false);
          showError('Check your email, click the verification link, then press this button.');
        })
        .catch(function (error) {
          setButton('Create account', false);
          showError(firebaseErrorMessage(error));
        });
      return;
    }

    var user = auth.currentUser;
    if (!user) {
      showError('Restart registration and create the Firebase account again.');
      setButton('Create account', false);
      return;
    }
    user.reload()
      .then(function () {
        if (!user.emailVerified) {
          throw new Error('Email is not verified yet. Open the link sent to your email first.');
        }
        return user.getIdToken(true);
      })
      .then(function (token) {
        tokenInput.value = token;
        verified = true;
        form.submit();
      })
      .catch(function (error) {
        setButton('I verified my email', false);
        showError(error.message || 'Email is not verified yet.');
      });
  });
})();
