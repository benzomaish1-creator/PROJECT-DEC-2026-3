/* ADMIN THEME helper — only decorates the page (brand, labels, icons).
   It never touches forms, links' targets or any data. */
document.addEventListener('DOMContentLoaded', function () {
  var body = document.body;
  if (!body.classList.contains('admin-theme')) return;

  var side = document.querySelector('.col-md-3.mb-4');
  var list = side && side.querySelector('.list-group');
  if (side && list) {
    // wrap each link's text in a <span> so it can be hidden when collapsed
    list.querySelectorAll('.list-group-item').forEach(function (a) {
      Array.prototype.slice.call(a.childNodes).forEach(function (n) {
        if (n.nodeType === 3 && n.textContent.trim()) {
          var s = document.createElement('span');
          s.textContent = n.textContent.trim();
          a.replaceChild(s, n);
        }
      });
    });

    var brand = document.createElement('div');
    brand.className = 'a-brand';
    brand.innerHTML =
      '<div class="a-brand-logo">&gt;_</div>' +
      '<div class="a-brand-name">DocConnect<small>ADMIN PANEL</small></div>';
    var label = document.createElement('div');
    label.className = 'a-side-label';
    label.textContent = 'MANAGEMENT';
    side.insertBefore(label, list);
    side.insertBefore(brand, label);

    var logout = document.querySelector('a[href*="admin_logout"]');
    var user = document.createElement('div');
    user.className = 'a-user';
    user.innerHTML =
      '<div class="a-avatar">AD</div>' +
      '<div class="a-user-name">Admin<small>Administrator</small></div>' +
      (logout ? '<a href="' + logout.getAttribute('href') + '" title="Logout" aria-label="Logout"><i class="bi bi-box-arrow-right"></i></a>' : '');
    side.appendChild(user);

    var toggle = document.createElement('button');
    toggle.type = 'button';
    toggle.className = 'a-toggle';
    toggle.setAttribute('aria-label', 'Collapse sidebar');
    toggle.innerHTML = '<span aria-hidden="true">&#8249;</span>';
    toggle.addEventListener('click', function () {
      body.classList.toggle('sb-collapsed');
      try { localStorage.setItem('adminSidebarCollapsed', body.classList.contains('sb-collapsed') ? '1' : '0'); } catch (e) {}
    });
    document.body.appendChild(toggle);
    try { if (localStorage.getItem('adminSidebarCollapsed') === '1') body.classList.add('sb-collapsed'); } catch (e) {}
  }

  // dashboard: icon on each headline-number card + a short subtitle
  var icons = ['bi-person-badge', 'bi-people', 'bi-calendar-check', 'bi-arrow-left-right'];
  document.querySelectorAll('.row > .col-md-3.mb-3 .card').forEach(function (card, i) {
    var ic = document.createElement('div');
    ic.className = 'a-stat-icon';
    ic.innerHTML = '<i class="bi ' + (icons[i] || 'bi-activity') + '"></i>';
    card.appendChild(ic);
  });
  var h3 = document.querySelector('body.admin-theme .col-md-9 > h3');
  if (h3 && /Admin Dashboard/i.test(h3.textContent)) {
    var sub = document.createElement('p');
    sub.className = 'a-subtitle';
    sub.textContent = 'Real-time overview of doctors, patients, appointments and referrals';
    h3.parentNode.insertBefore(sub, h3.nextSibling);
  }
});
