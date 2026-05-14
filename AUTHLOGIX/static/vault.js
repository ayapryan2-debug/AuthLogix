  document.addEventListener('DOMContentLoaded', () => {
    const navLinks = document.querySelectorAll('#nav-bar a');
    const tabContents = document.querySelectorAll('.tab-content');

    navLinks.forEach(link => {
      link.addEventListener('click', () => {
        const targetId = link.getAttribute('data-target');

        navLinks.forEach(nav => nav.classList.remove('active-nav'));
        link.classList.add('active-nav');

        tabContents.forEach(content => {
          content.classList.remove('active-view');
          if (content.id === targetId) {
            content.classList.add('active-view');
          }
        });
        
        console.log(`Cloud 4: Switched view to "${targetId}"`);
      });
    });

    console.log("Cloud 4 Portal Active and Listening for Navigation.");
  });