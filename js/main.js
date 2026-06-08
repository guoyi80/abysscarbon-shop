// AbyssCarbon — E-commerce JS
document.addEventListener('DOMContentLoaded', () => {

    // ── Hamburger Menu ──
    const nav = document.querySelector('.nav');
    const navLinks = document.querySelector('.nav-links');
    if (nav && navLinks) {
        // Create hamburger button
        const hamburger = document.createElement('button');
        hamburger.className = 'hamburger';
        hamburger.setAttribute('aria-label', 'Toggle navigation');
        hamburger.innerHTML = '<span></span><span></span><span></span>';

        // Create overlay
        const overlay = document.createElement('div');
        overlay.className = 'nav-overlay';

        // Clone nav links into overlay
        const clonedLinks = navLinks.cloneNode(true);
        overlay.appendChild(clonedLinks);

        // Insert into DOM
        nav.appendChild(hamburger);
        document.body.appendChild(overlay);

        // Toggle function
        function openMenu() {
            hamburger.classList.add('open');
            overlay.classList.add('active');
            document.body.style.overflow = 'hidden';
        }
        function closeMenu() {
            hamburger.classList.remove('open');
            overlay.classList.remove('active');
            document.body.style.overflow = '';
        }

        hamburger.addEventListener('click', () => {
            if (hamburger.classList.contains('open')) { closeMenu(); }
            else { openMenu(); }
        });

        // Close on overlay link click
        overlay.querySelectorAll('a').forEach(link => {
            link.addEventListener('click', () => closeMenu());
        });

        // Close on Escape
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape' && overlay.classList.contains('active')) {
                closeMenu();
            }
        });
    }

    // Smooth scroll
    document.querySelectorAll('a[href^="#"]').forEach(link => {
        link.addEventListener('click', (e) => {
            e.preventDefault();
            const target = document.querySelector(link.getAttribute('href'));
            if (target) {
                target.scrollIntoView({ behavior: 'smooth', block: 'start' });
            }
        });
    });

    // Contact form
    const form = document.querySelector('.contact-form');
    if (form) {
        form.addEventListener('submit', (e) => {
            e.preventDefault();
            const btn = form.querySelector('button');
            const orig = btn.textContent;
            btn.textContent = 'Sending...';
            btn.style.background = 'var(--accent-dim)';
            btn.style.borderColor = 'var(--accent-dim)';

            fetch(form.action, {
                method: 'POST',
                body: new FormData(form),
                headers: { 'Accept': 'application/json' }
            }).then(() => {
                btn.textContent = 'Sent — Thank You';
                btn.style.background = 'var(--green)';
                btn.style.borderColor = 'var(--green)';
                form.reset();
                setTimeout(() => {
                    btn.textContent = orig;
                    btn.style.background = 'transparent';
                    btn.style.borderColor = 'var(--accent)';
                }, 3000);
            }).catch(() => {
                btn.textContent = orig;
                btn.style.background = 'transparent';
                btn.style.borderColor = 'var(--accent)';
            });
        });
    }

    // Optimize status
    const statusEl = document.getElementById('optimize-status');
    if (statusEl) {
        const d = new Date();
        statusEl.textContent = `Last optimized: ${d.toISOString().slice(0,19).replace('T',' ')} UTC`;
    }

    // Fade-in on scroll
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.style.opacity = '1';
                entry.target.style.transform = 'translateY(0)';
            }
        });
    }, { threshold: 0.1 });

    document.querySelectorAll('.product-card, .about-text, .stat').forEach(el => {
        el.style.opacity = '0';
        el.style.transform = 'translateY(20px)';
        el.style.transition = 'all 0.6s ease';
        observer.observe(el);
    });

    setTimeout(() => {
        document.querySelectorAll('.product-card, .about-text, .stat').forEach(el => {
            el.style.opacity = '1';
            el.style.transform = 'translateY(0)';
        });
    }, 200);

    if (window.Snipcart) {
        document.addEventListener('snipcart.ready', () => {
            console.log('[AbyssCarbon] Snipcart ready');
        });
    }
});