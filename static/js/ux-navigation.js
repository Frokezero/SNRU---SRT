document.addEventListener('DOMContentLoaded', () => {
    // Keep the existing role-controlled actions and their event handlers intact.
    const groups = document.querySelector('.btn-groups-container');
    if (groups) {
        const navigation = document.createElement('aside');
        navigation.className = 'ux-admin-navigation';
        navigation.setAttribute('aria-label', 'เมนูผู้ดูแล');
        const heading = document.createElement('h2');
        heading.textContent = 'เมนูจัดการ';
        navigation.append(heading, groups);
        document.body.prepend(navigation);
        document.body.classList.add('ux-admin-layout');
    }
    document.querySelectorAll('input, select, textarea').forEach(input => {
        if (!input.id || input.type === 'hidden') return;
        const group = input.closest('.form-group, .filter-item');
        const label = group?.querySelector('label');
        if (label && !label.htmlFor && group.querySelectorAll('input,select,textarea').length === 1) label.htmlFor = input.id;
    });
    document.querySelectorAll('button[title]').forEach(button => {
        if (!button.textContent.trim()) button.setAttribute('aria-label', button.title);
    });
    const dialogs = [...document.querySelectorAll('.modal, .modal-overlay')];
    const previousFocus = new WeakMap();
    const visible = el => el.getClientRects().length > 0 && getComputedStyle(el).visibility !== 'hidden';
    dialogs.forEach(dialog => {
        dialog.setAttribute('role', 'dialog');
        dialog.setAttribute('aria-modal', 'true');
        const title = dialog.querySelector('h2, h3');
        if (title) { title.id ||= dialog.id + '-heading'; dialog.setAttribute('aria-labelledby', title.id); }
        let wasOpen = visible(dialog);
        new MutationObserver(() => {
            const isOpen = visible(dialog);
            if (isOpen && !wasOpen) {
                previousFocus.set(dialog, document.activeElement);
                dialog.tabIndex = -1;
                dialog.focus();
            } else if (!isOpen && wasOpen) previousFocus.get(dialog)?.focus();
            wasOpen = isOpen;
        }).observe(dialog, { attributes:true, attributeFilter:['class', 'style'] });
        dialog.addEventListener('keydown', event => {
            if (event.key !== 'Tab') return;
            const targets = [...dialog.querySelectorAll('button:not(:disabled), a[href], input:not(:disabled), select:not(:disabled), textarea:not(:disabled), [tabindex="0"]')].filter(visible);
            const first = targets[0], last = targets.at(-1);
            if (!first) { event.preventDefault(); return; }
            if (event.shiftKey && (document.activeElement === first || document.activeElement === dialog)) { event.preventDefault(); last.focus(); }
            else if (!event.shiftKey && (document.activeElement === last || document.activeElement === dialog)) { event.preventDefault(); first.focus(); }
        });
    });
    document.querySelectorAll('#toast-container, #msg-toast').forEach(el => {
        el.setAttribute('role', 'status');
        el.setAttribute('aria-live', 'polite');
    });
});
