// AbyssCarbon — E-commerce JS
document.addEventListener('DOMContentLoaded', () => {

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