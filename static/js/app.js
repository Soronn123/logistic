document.addEventListener('DOMContentLoaded', function() {
  // Theme toggle
  const themeToggle = document.getElementById('theme-toggle');
  const html = document.documentElement;

  function setTheme(theme) {
    if (theme === 'dark') {
      html.classList.add('dark');
      document.body.classList.add('dark');
    } else {
      html.classList.remove('dark');
      document.body.classList.remove('dark');
    }
    localStorage.setItem('theme', theme);
    document.cookie = 'theme=' + theme + ';path=/;max-age=31536000';
  }

  const savedTheme = localStorage.getItem('theme') || 'light';
  setTheme(savedTheme);

  if (themeToggle) {
    themeToggle.addEventListener('click', function() {
      const current = html.classList.contains('dark') ? 'dark' : 'light';
      setTheme(current === 'dark' ? 'light' : 'dark');
    });
  }

  // Mobile menu toggle
  const menuToggle = document.getElementById('mobile-menu-toggle');
  const mobileMenu = document.getElementById('mobile-menu');

  if (menuToggle && mobileMenu) {
    menuToggle.addEventListener('click', function() {
      const isOpen = mobileMenu.classList.contains('translate-x-0');
      if (isOpen) {
        mobileMenu.classList.remove('translate-x-0');
        mobileMenu.classList.add('-translate-x-full');
        document.body.classList.remove('mobile-menu-open');
      } else {
        mobileMenu.classList.remove('-translate-x-full');
        mobileMenu.classList.add('translate-x-0');
        document.body.classList.add('mobile-menu-open');
      }
    });

    // Close mobile menu on link click
    mobileMenu.querySelectorAll('a').forEach(function(link) {
      link.addEventListener('click', function() {
        mobileMenu.classList.remove('translate-x-0');
        mobileMenu.classList.add('-translate-x-full');
        document.body.classList.remove('mobile-menu-open');
      });
    });
  }

  // Mobile submenu toggles
  document.querySelectorAll('.mobile-submenu-toggle').forEach(function(btn) {
    btn.addEventListener('click', function() {
      const submenu = this.nextElementSibling;
      if (submenu) {
        submenu.classList.toggle('hidden');
        this.querySelector('svg').classList.toggle('rotate-180');
      }
    });
  });

  // Counter animation on scroll
  const counters = document.querySelectorAll('.counter-number');
  if (counters.length > 0) {
    const observer = new IntersectionObserver(function(entries) {
      entries.forEach(function(entry) {
        if (entry.isIntersecting) {
          const el = entry.target;
          const target = parseInt(el.dataset.target);
          if (!el.classList.contains('counted')) {
            el.classList.add('counted');
            animateCounter(el, target);
          }
        }
      });
    }, { threshold: 0.5 });

    counters.forEach(function(c) { observer.observe(c); });
  }

  function animateCounter(el, target) {
    let current = 0;
    const increment = Math.ceil(target / 60);
    const timer = setInterval(function() {
      current += increment;
      if (current >= target) {
        current = target;
        clearInterval(timer);
      }
      el.textContent = current.toLocaleString('ru-RU');
      el.classList.add('visible');
    }, 25);
  }

  // Scroll animations
  document.querySelectorAll('.animate-on-scroll').forEach(function(el) {
    const observer = new IntersectionObserver(function(entries) {
      entries.forEach(function(entry) {
        if (entry.isIntersecting) {
          el.classList.add('animate-fade-in');
          observer.unobserve(el);
        }
      });
    }, { threshold: 0.1 });
    observer.observe(el);
  });

  // Language switcher
  document.querySelectorAll('.lang-switcher a').forEach(function(link) {
    link.addEventListener('click', function(e) {
      e.preventDefault();
      const lang = this.dataset.lang;
      const currentPath = window.location.pathname;
      const newPath = currentPath.replace(/^\/(ru|en)\//, '/' + lang + '/');
      window.location.href = newPath;
    });
  });
});

// HTMX after-swap handler
document.addEventListener('htmx:afterSwap', function() {
  // Re-initialize any needed bindings
});
