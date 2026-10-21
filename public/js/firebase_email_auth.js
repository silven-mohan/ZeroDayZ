(function () {
  'use strict';

  var form = document.querySelector('.form');
  var configElement = document.getElementById('firebase-config');
  var tokenInput = document.getElementById('firebase_id_token');
  var errorElement = document.getElementById('firebase-error');
  var verifyButton = document.getElementById('verify-email-button');
  var button = form && form.querySelector('.btn');
  if (!form || !configElement || !tokenInput || !errorElement || !verifyButton) return;

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
      'auth/email-already-in-use': 'That email already has a Firebase account. Use its password or reset it.',
      'auth/invalid-email': 'Enter a valid email address.',
      'auth/weak-password': 'Use a stronger password.',
      'auth/too-many-requests': 'Too many attempts. Wait and try again later.'
    };
    return messages[code] || (error && error.message) || 'Firebase email verification failed.';
  }

  function sendVerification(auth, email, password) {
    return auth.createUserWithEmailAndPassword(email, password)
      .then(function (result) { return result.user; })
      .catch(function (error) {
        if (error.code !== 'auth/email-already-in-use') throw error;
        return auth.signInWithEmailAndPassword(email, password).then(function (result) {
          return result.user;
        });
      })
      .then(function (user) {
        if (user.emailVerified) return user;
        return user.sendEmailVerification().then(function () { return user; });
      });
  }

  function sendVerificationEmail() {
    errorElement.hidden = true;
    var email = document.getElementById('email').value.trim().toLowerCase();
    var password = document.getElementById('password').value;
    if (!email || !document.getElementById('email').checkValidity()) {
      showError('Enter a valid email address first.');
      return;
    }
    if (password.length < 8) {
      showError('Create a password of at least 8 characters before verifying your email.');
      return;
    }
    var auth;
    try { auth = initialize(); } catch (error) { showError(firebaseErrorMessage(error)); return; }
    if (!auth) return;
    setButton('Waiting for email verification...', true);
    verifyButton.disabled = true;
    sendVerification(auth, email, password)
      .then(function (user) {
        verificationSent = true;
        verifyButton.textContent = user.emailVerified ? 'Email already verified' : 'Verification email sent';
        showError('Open the verification link in your email, then press Create account.');
        setButton('Create account', false);
      })
      .catch(function (error) {
        verifyButton.disabled = false;
        setButton('Create account', false);
        showError(firebaseErrorMessage(error));
      });
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

    if (!verificationSent) { sendVerificationEmail(); return; }

    var auth = initialize();
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

  verifyButton.addEventListener('click', sendVerificationEmail);
})();
