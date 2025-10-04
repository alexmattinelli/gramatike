'use strict';
(function(){
  if ('serviceWorker' in navigator) {
    window.addEventListener('load', function(){
      try { navigator.serviceWorker.register('/static/sw.js'); } catch(e) {}
    });
  }
})();
