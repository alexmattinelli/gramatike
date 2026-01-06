'use strict';
(function(){
  // Register Service Worker
  if ('serviceWorker' in navigator) {
    window.addEventListener('load', function(){
      try { navigator.serviceWorker.register('/static/sw.js'); } catch(e) {}
    });
  }

  // PWA Splash Screen - shows when app is launched from home screen
  function showSplashScreen() {
    // Check if running as standalone PWA
    var isStandalone = window.matchMedia('(display-mode: standalone)').matches ||
                       window.navigator.standalone === true ||
                       document.referrer.includes('android-app://');
    
    // Only show splash for standalone mode and if not already shown this session
    if (!isStandalone) return;
    if (sessionStorage.getItem('splashShown')) return;
    
    sessionStorage.setItem('splashShown', 'true');

    // Create splash screen element
    var splash = document.createElement('div');
    splash.id = 'pwa-splash';
    splash.innerHTML = [
      '<div class="splash-content">',
      '  <div class="splash-logo">',
      '    <img src="/static/img/icons/icon-192.png" alt="Gramátike" class="splash-icon">',
      '  </div>',
      '  <h1 class="splash-title">Gramátike</h1>',
      '  <p class="splash-tagline">Língua Viva e de Todes</p>',
      '  <div class="splash-loader">',
      '    <div class="loader-dot"></div>',
      '    <div class="loader-dot"></div>',
      '    <div class="loader-dot"></div>',
      '  </div>',
      '</div>'
    ].join('');
    
    // Add styles
    var style = document.createElement('style');
    style.textContent = [
      '#pwa-splash {',
      '  position: fixed;',
      '  top: 0; left: 0; right: 0; bottom: 0;',
      '  background: linear-gradient(135deg, #9B5DE5 0%, #7B4BC4 50%, #5E35A1 100%);',
      '  display: flex;',
      '  align-items: center;',
      '  justify-content: center;',
      '  z-index: 99999;',
      '  opacity: 1;',
      '  transition: opacity 0.5s ease-out;',
      '}',
      '#pwa-splash.fade-out { opacity: 0; pointer-events: none; }',
      '.splash-content {',
      '  text-align: center;',
      '  animation: splashFadeIn 0.6s ease-out;',
      '}',
      '@keyframes splashFadeIn {',
      '  from { opacity: 0; transform: scale(0.9) translateY(20px); }',
      '  to { opacity: 1; transform: scale(1) translateY(0); }',
      '}',
      '.splash-logo {',
      '  margin-bottom: 1.5rem;',
      '  animation: splashPulse 1.5s ease-in-out infinite;',
      '}',
      '@keyframes splashPulse {',
      '  0%, 100% { transform: scale(1); }',
      '  50% { transform: scale(1.05); }',
      '}',
      '.splash-icon {',
      '  width: 120px;',
      '  height: 120px;',
      '  border-radius: 28px;',
      '  box-shadow: 0 20px 60px rgba(0,0,0,0.3);',
      '}',
      '.splash-title {',
      '  font-family: "Mansalva", cursive;',
      '  font-size: 3rem;',
      '  color: #fff;',
      '  margin: 0 0 0.5rem;',
      '  letter-spacing: 2px;',
      '  text-shadow: 0 4px 20px rgba(0,0,0,0.2);',
      '}',
      '.splash-tagline {',
      '  font-family: "Nunito", sans-serif;',
      '  font-size: 1rem;',
      '  color: rgba(255,255,255,0.9);',
      '  margin: 0 0 2rem;',
      '  font-weight: 600;',
      '  letter-spacing: 0.5px;',
      '}',
      '.splash-loader {',
      '  display: flex;',
      '  justify-content: center;',
      '  gap: 8px;',
      '}',
      '.loader-dot {',
      '  width: 12px;',
      '  height: 12px;',
      '  background: rgba(255,255,255,0.8);',
      '  border-radius: 50%;',
      '  animation: loaderBounce 1.2s ease-in-out infinite;',
      '}',
      '.loader-dot:nth-child(2) { animation-delay: 0.2s; }',
      '.loader-dot:nth-child(3) { animation-delay: 0.4s; }',
      '@keyframes loaderBounce {',
      '  0%, 80%, 100% { transform: scale(0.6); opacity: 0.5; }',
      '  40% { transform: scale(1); opacity: 1; }',
      '}'
    ].join('\n');

    document.head.appendChild(style);
    document.body.appendChild(splash);

    // Hide splash after content loads
    function hideSplash() {
      setTimeout(function() {
        splash.classList.add('fade-out');
        setTimeout(function() {
          if (splash.parentNode) {
            splash.parentNode.removeChild(splash);
          }
        }, 500);
      }, 1200); // Show for at least 1.2 seconds
    }

    if (document.readyState === 'complete') {
      hideSplash();
    } else {
      window.addEventListener('load', hideSplash);
    }
  }

  // Show splash screen immediately
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', showSplashScreen);
  } else {
    showSplashScreen();
  }
})();
