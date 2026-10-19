/* ZeroDayZ – new complaint: small enhancements. The form works fully without this script. */
(function () {
  'use strict';

  var form = document.querySelector('.form');
  if (!form) return;

  var MAX_BYTES = 5 * 1024 * 1024;
  var TYPES = ['image/jpeg', 'image/png', 'image/webp'];

  // Mobile number: keep digits only
  var mobile = form.querySelector('#mobile');
  if (mobile) {
    mobile.addEventListener('input', function () {
      mobile.value = mobile.value.replace(/[^\d+ ]/g, '');
    });
  }

  // Description character count
  var desc = form.querySelector('#description');
  var count = form.querySelector('[data-count]');
  if (desc && count) {
    desc.addEventListener('input', function () { count.textContent = desc.value.length; });
  }

  // Photo: preview, drag and drop, remove
  var box = form.querySelector('[data-upload]');
  if (box) {
    var input = box.querySelector('input[type="file"]');
    var empty = box.querySelector('[data-empty]');
    var preview = box.querySelector('[data-preview]');
    var img = box.querySelector('[data-preview-img]');
    var remove = box.querySelector('[data-remove]');
    var problem = form.querySelector('#photo-js-error');
    var url = null;

    var say = function (text) {
      problem.textContent = text;
      problem.hidden = !text;
    };
    var clear = function () {
      input.value = '';
      if (url) { URL.revokeObjectURL(url); url = null; }
      img.removeAttribute('src');
      preview.hidden = true;
      empty.hidden = false;
      box.classList.remove('has-photo');
    };
    var show = function (file) {
      if (url) URL.revokeObjectURL(url);
      url = URL.createObjectURL(file);
      img.src = url;
      preview.hidden = false;
      empty.hidden = true;
      box.classList.add('has-photo');
    };
    var check = function () {
      var file = input.files && input.files[0];
      say('');
      if (!file) { clear(); return; }
      if (TYPES.indexOf(file.type) === -1) { clear(); say('Choose a JPG, PNG or WebP photo.'); return; }
      if (file.size > MAX_BYTES) { clear(); say('That photo is larger than 5 MB. Choose a smaller one.'); return; }
      show(file);
    };

    input.addEventListener('change', check);
    remove.addEventListener('click', function () { clear(); say(''); input.focus(); });

    ['dragenter', 'dragover'].forEach(function (name) {
      box.addEventListener(name, function (e) { e.preventDefault(); box.classList.add('is-over'); });
    });
    ['dragleave', 'drop'].forEach(function (name) {
      box.addEventListener(name, function () { box.classList.remove('is-over'); });
    });
    box.addEventListener('drop', function (e) {
      e.preventDefault();
      if (e.dataTransfer && e.dataTransfer.files.length) {
        input.files = e.dataTransfer.files;
        check();
      }
    });
  }

  // Prevent double submits and give feedback
  var button = form.querySelector('.btn');
  var label = button ? button.textContent : '';
  form.addEventListener('submit', function () {
    if (!button) return;
    button.disabled = true;
    button.textContent = 'Submitting…';
  });
  window.addEventListener('pageshow', function () {
    if (button) { button.disabled = false; button.textContent = label; }
  });

  // After a failed server-side check, move focus to the error summary
  var summary = document.getElementById('form-errors');
  if (summary) summary.focus();
})();