(function(){
  try {
    const saved = localStorage.getItem('theme');
    const prefersDark = window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches;
    if (saved === 'dark' || (!saved && prefersDark)) {
      document.documentElement.classList.add('dark');
      document.addEventListener('DOMContentLoaded', function(){ document.body.classList.add('dark'); });
    }
  } catch(e) {}
})();
