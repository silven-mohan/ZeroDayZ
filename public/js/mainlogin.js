/* ZeroDayZ – main login: remember which account was used last.
   The page works fully without this script. */
(function () {
  'use strict';

  var KEY = 'zerodayz:lastRole';
  var doors = Array.prototype.slice.call(document.querySelectorAll('.door[data-role]'));
  if (!doors.length) return;

  // Mark the account used last time
  try {
    var last = window.localStorage.getItem(KEY);
    doors.forEach(function (door) {
      if (door.dataset.role === last) {
        var badge = document.createElement('span');
        badge.className = 'door__badge';
        badge.textContent = 'Last used';
        door.querySelector('.door__leaf').appendChild(badge);
      }
    });
  } catch (e) { /* storage unavailable: skip */ }

  // Remember the choice
  doors.forEach(function (door) {
    door.addEventListener('click', function () {
      try { window.localStorage.setItem(KEY, door.dataset.role); } catch (e) { /* ignore */ }
    });
  });
})();