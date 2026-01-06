// Dark mode temporarily disabled
(function(){
  try {
    // Force light mode by removing any dark classes
    document.documentElement.classList.remove('dark');
    document.addEventListener('DOMContentLoaded', function(){ 
      document.body.classList.remove('dark'); 
    });
  } catch(e) {}
})();
