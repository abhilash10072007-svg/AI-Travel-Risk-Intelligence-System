document.addEventListener('DOMContentLoaded', () => {
  // Initialize Lucide Icons
  if (window.lucide) {
    lucide.createIcons();
  }

  let currentScreen = 'page-dashboard';
  let isOffline = true;
  let leafletMapInstance = null;
  let routeLayers = {};

  const screenMetadata = {
    'page-dashboard': { index: '01', title: 'Dashboard' },
    'page-time-analysis': { index: '02', title: 'Time Analysis' },
    'page-route-map': { index: '03', title: 'Route Map' },
    'page-offline-center': { index: '04', title: 'Offline Center' },
    'page-history': { index: '05', title: 'History' },
    'page-settings': { index: '06', title: 'Settings' }
  };

  const navItems = document.querySelectorAll('.sidebar-nav .nav-item');
  const screenViews = document.querySelectorAll('.screen-view');
  const screenIndexEl = document.getElementById('currentScreenIndex');
  const screenHeadingEl = document.getElementById('currentScreenHeading');
  const mobileMenuToggle = document.getElementById('mobileMenuToggle');
  const sidebar = document.getElementById('appSidebar');

  const notificationBtn = document.getElementById('notificationBtn');
  const notificationDropdown = document.getElementById('notificationDropdown');
  const modalBackdrop = document.getElementById('offlineModalBackdrop');
  const modalTitle = document.getElementById('offlineModalTitle');
  const modalBody = document.getElementById('offlineModalBody');
  const closeModalBtn = document.getElementById('closeModalBtn');
  const modalActionBtn = document.getElementById('modalActionBtn');

  function navigateToScreen(screenId) {
    if (!screenMetadata[screenId]) return;
    currentScreen = screenId;

    navItems.forEach(item => {
      item.classList.toggle('active', item.getAttribute('data-page') === screenId);
    });

    const headerTitleWrapper = document.getElementById('headerTitleWrapper');
    if (screenId === 'page-dashboard') {
      if (headerTitleWrapper) headerTitleWrapper.style.visibility = 'hidden';
    } else {
      if (headerTitleWrapper) headerTitleWrapper.style.visibility = 'visible';
      screenIndexEl.textContent = screenMetadata[screenId].index;
      screenHeadingEl.textContent = screenMetadata[screenId].title;
    }

    screenViews.forEach(view => {
      view.classList.toggle('active', view.id === screenId);
    });

    if (sidebar.classList.contains('mobile-open')) {
      sidebar.classList.remove('mobile-open');
    }

    window.scrollTo({ top: 0, behavior: 'smooth' });

    if (screenId === 'page-route-map') {
      setTimeout(initRouteMap, 100);
    }
  }

  window.navigateToScreen = navigateToScreen;

  navItems.forEach(item => {
    item.addEventListener('click', () => {
      navigateToScreen(item.getAttribute('data-page'));
    });
  });

  if (mobileMenuToggle) {
    mobileMenuToggle.addEventListener('click', () => {
      sidebar.classList.toggle('mobile-open');
    });
  }

  document.querySelectorAll('.quick-feature-card, .feature-card-clean').forEach(card => {
    card.addEventListener('click', () => {
      const target = card.getAttribute('data-target');
      if (target) navigateToScreen(target);
    });
  });

  notificationBtn.addEventListener('click', (e) => {
    e.stopPropagation();
    notificationDropdown.classList.toggle('show');
  });

  document.addEventListener('click', (e) => {
    if (!notificationDropdown.contains(e.target) && !notificationBtn.contains(e.target)) {
      notificationDropdown.classList.remove('show');
    }
    const layerMenu = document.getElementById('layerMenu');
    const layerBtn = document.getElementById('mapLayersDropdownBtn');
    if (layerMenu && layerBtn && !layerMenu.contains(e.target) && !layerBtn.contains(e.target)) {
      layerMenu.classList.remove('show');
    }
  });

  const analyzeRiskBtn = document.getElementById('analyzeRiskBtn');
  if (analyzeRiskBtn) {
    analyzeRiskBtn.addEventListener('click', () => {
      const origin = document.getElementById('originInput').value || 'Coimbatore';
      const dest = document.getElementById('destInput').value || 'Palakkad';
      showToast(`Analyzing real-time hazards between ${origin} and ${dest}...`);
      setTimeout(() => {
        navigateToScreen('page-route-map');
        showToast(`Route analysis complete. Route 1 recommended.`);
      }, 600);
    });
  }

  const dismissAlertBtn = document.getElementById('dismissAlertBtn');
  const liveAlertBanner = document.getElementById('liveAlertBanner');
  if (dismissAlertBtn && liveAlertBanner) {
    dismissAlertBtn.addEventListener('click', () => {
      liveAlertBanner.style.display = 'none';
      showToast('Live alert dismissed.');
    });
  }

  const viewAlternateRoutesBtn = document.getElementById('viewAlternateRoutesBtn');
  if (viewAlternateRoutesBtn) {
    viewAlternateRoutesBtn.addEventListener('click', () => {
      navigateToScreen('page-route-map');
      selectRoute(1);
    });
  }

  const howThisWorksBtn = document.getElementById('howThisWorksBtn');
  if (howThisWorksBtn) {
    howThisWorksBtn.addEventListener('click', () => {
      openOfflineModal('how-it-works');
    });
  }

  const timeLearnMoreBtn = document.getElementById('timeLearnMoreBtn');
  if (timeLearnMoreBtn) {
    timeLearnMoreBtn.addEventListener('click', () => {
      openOfflineModal('time-windows');
    });
  }

  function initRouteMap() {
    const mapEl = document.getElementById('leafletMap');
    if (!mapEl) return;

    if (leafletMapInstance) {
      leafletMapInstance.invalidateSize();
      return;
    }

    leafletMapInstance = L.map('leafletMap', {
      zoomControl: true,
      attributionControl: false
    }).setView([10.9100, 76.8100], 10);

    L.tileLayer('https://{s}.basemaps.cartocdn.com/rastertiles/voyager/{z}/{x}/{y}{r}.png', {
      maxZoom: 19
    }).addTo(leafletMapInstance);

    const route1Coords = [
      [11.0168, 76.9558], [11.0800, 77.0200], [10.9800, 77.0100],
      [10.6600, 77.0050], [10.7200, 76.8200], [10.7867, 76.6548]
    ];
    const route2Coords = [
      [11.0168, 76.9558], [10.9200, 76.9100], [10.8400, 76.8500],
      [10.8000, 76.7300], [10.7867, 76.6548]
    ];
    const route3Coords = [
      [11.0168, 76.9558], [10.8900, 76.9800], [10.6800, 76.9200],
      [10.6200, 76.7800], [10.7100, 76.6900], [10.7867, 76.6548]
    ];

    routeLayers[1] = L.polyline(route1Coords, { color: '#10B981', weight: 6, opacity: 0.9 }).addTo(leafletMapInstance);
    routeLayers[2] = L.polyline(route2Coords, { color: '#F59E0B', weight: 4.5, opacity: 0.8, dashArray: '4, 6' }).addTo(leafletMapInstance);
    routeLayers[3] = L.polyline(route3Coords, { color: '#EF4444', weight: 4.5, opacity: 0.8, dashArray: '3, 6' }).addTo(leafletMapInstance);

    const createCustomIcon = (label, color) => L.divIcon({
      className: 'custom-map-pin',
      html: `<div style="background: ${color}; color: white; padding: 4px 10px; border-radius: 12px; font-weight: 800; font-size: 11px; border: 2px solid white; box-shadow: 0 2px 8px rgba(0,0,0,0.25); white-space: nowrap;">${label}</div>`,
      iconSize: [80, 24],
      iconAnchor: [40, 12]
    });

    L.marker([11.0168, 76.9558], { icon: createCustomIcon('Coimbatore', '#4F46E5') }).addTo(leafletMapInstance);
    L.marker([10.7867, 76.6548], { icon: createCustomIcon('Palakkad', '#059669') }).addTo(leafletMapInstance);
    L.marker([10.6600, 77.0050], { icon: createCustomIcon('Pollachi', '#475569') }).addTo(leafletMapInstance);
    L.marker([10.8400, 76.8500], { icon: createCustomIcon('Walayar', '#475569') }).addTo(leafletMapInstance);

    const hazardIcon = L.divIcon({
      className: 'hazard-map-pin',
      html: `<div style="background: #EF4444; color: white; padding: 6px 12px; border-radius: 8px; font-weight: 800; font-size: 11px; border: 2px solid white; display: flex; align-items: center; gap: 4px; animation: pulseGlow 2s infinite;">⚠️ Zone C Hazard</div>`,
      iconSize: [120, 28],
      iconAnchor: [60, 14]
    });
    L.marker([10.6200, 76.7800], { icon: hazardIcon }).addTo(leafletMapInstance);

    leafletMapInstance.fitBounds(routeLayers[1].getBounds(), { padding: [40, 40] });
  }

  function selectRoute(routeId) {
    const cards = [document.getElementById('routeCard1'), document.getElementById('routeCard2'), document.getElementById('routeCard3')];
    cards.forEach((card, idx) => {
      if (card) card.classList.toggle('active', idx + 1 === routeId);
    });

    if (leafletMapInstance && routeLayers[routeId]) {
      [1, 2, 3].forEach(id => {
        if (routeLayers[id]) {
          if (id === routeId) {
            routeLayers[id].setStyle({ weight: 7, opacity: 1 });
            routeLayers[id].bringToFront();
          } else {
            routeLayers[id].setStyle({ weight: 3.5, opacity: 0.5 });
          }
        }
      });
      leafletMapInstance.fitBounds(routeLayers[routeId].getBounds(), { padding: [50, 50] });
    }
    showToast(`Selected Route ${routeId}`);
  }

  window.selectRoute = selectRoute;

  const mapLayersDropdownBtn = document.getElementById('mapLayersDropdownBtn');
  const layerMenu = document.getElementById('layerMenu');
  if (mapLayersDropdownBtn && layerMenu) {
    mapLayersDropdownBtn.addEventListener('click', (e) => {
      e.stopPropagation();
      layerMenu.classList.toggle('show');
    });
  }

  const toggleOfflineSimBtn = document.getElementById('toggleOfflineSimBtn');
  if (toggleOfflineSimBtn) {
    toggleOfflineSimBtn.addEventListener('click', () => {
      isOffline = !isOffline;
      if (isOffline) {
        toggleOfflineSimBtn.innerHTML = '<i data-lucide="wifi"></i><span>Simulate Reconnect</span>';
        showToast('Offline Mode Active. Cached safety data loaded.');
      } else {
        toggleOfflineSimBtn.innerHTML = '<i data-lucide="wifi-off"></i><span>Simulate Offline</span>';
        showToast('Online connection restored! hazard feeds synced.');
      }
      if (window.lucide) lucide.createIcons();
    });
  }

  const refreshDataBtn = document.getElementById('refreshDataBtn');
  if (refreshDataBtn) {
    refreshDataBtn.addEventListener('click', () => {
      showToast('Refreshing offline datasets...');
    });
  }

  const modalContents = {
    'safety': {
      title: 'Offline Safety Guide',
      content: '<h4 style="font-weight:700; color:#1E1B4B; margin-bottom:8px;">Monsoon Road Safety Rules:</h4><p>Avoid ghat sections during peak rains, keep emergency contacts cached, and seek safe havens in Zone C.</p>'
    },
    'weather': {
      title: 'Weather Snapshot',
      content: '<p>Western Ghats: Doppler radar signals active rainfall (60-90 mm) over ghat segments. Clearing predicted by late evening.</p>'
    },
    'legend': {
      title: 'Risk Index Legend',
      content: '<p><strong>Green</strong>: Standard conditions. <strong>Amber</strong>: Reduce speeds. <strong>Red</strong>: Landslide caution on Ghat corridors.</p>'
    },
    'action': {
      title: 'Action Checklist',
      content: '<p>1. Park vehicle in a safe zone.<br/>2. Avoid crossing water streams.<br/>3. Call Obstacle Helpdesk: 1077.</p>'
    },
    'advisory': {
      title: 'Disaster Advisories',
      content: '<p>KSDMA: Strict warnings issued for mountainous passes. Heavy commercial vehicles redirected.</p>'
    },
    'download': {
      title: 'Downloads Manager',
      content: '<p>Contour Elevation Map (24 MB) - Completed.<br/>Sensor network configs (12 MB) - Completed.</p>'
    },
    'how-it-works': {
      title: 'Machine Learning ETAs',
      content: '<p>Synchronizes your departure ETA with weather radar to predict risk intervals accurately.</p>'
    },
    'time-windows': {
      title: 'Time Window Strategy',
      content: '<p>Shifting departure by 3 hours significantly reduces exposure to monsoon storm cells.</p>'
    },
    'roadmap': {
      title: '30-Day Development Roadmap',
      content: '<p>Aggregating 15,000 incident points, training susceptibility factors (70/30 split), and deploying offline mesh alerts.</p>'
    }
  };

  function openOfflineModal(type) {
    const data = modalContents[type] || { title: 'Info', content: 'Details unavailable.' };
    modalTitle.textContent = data.title;
    modalBody.innerHTML = data.content;
    modalBackdrop.classList.add('show');
  }

  window.openOfflineModal = openOfflineModal;

  if (closeModalBtn) closeModalBtn.addEventListener('click', () => modalBackdrop.classList.remove('show'));
  if (modalActionBtn) modalActionBtn.addEventListener('click', () => modalBackdrop.classList.remove('show'));
  modalBackdrop.addEventListener('click', (e) => { if (e.target === modalBackdrop) modalBackdrop.classList.remove('show'); });

  const viewFullRoadmapBtn = document.getElementById('viewFullRoadmapBtn');
  if (viewFullRoadmapBtn) viewFullRoadmapBtn.addEventListener('click', () => openOfflineModal('roadmap'));

  const historySearchInput = document.getElementById('historySearchInput');
  const historyTableRows = document.querySelectorAll('#historyTable tbody tr');
  if (historySearchInput) {
    historySearchInput.addEventListener('input', (e) => {
      const query = e.target.value.toLowerCase();
      historyTableRows.forEach(row => {
        row.style.display = row.textContent.toLowerCase().includes(query) ? '' : 'none';
      });
    });
  }

  const filterDateBtn = document.getElementById('filterDateBtn');
  if (filterDateBtn) {
    filterDateBtn.addEventListener('click', () => {
      showToast('Filtered records for last 30 days.');
    });
  }

  // Settings subnav tabs smooth scrolling & active class tracking
  const settingsNavItems = document.querySelectorAll('.settings-nav-item');
  const settingsContentContainer = document.getElementById('settingsContentContainer');
  const settingsSections = document.querySelectorAll('.settings-group-section');

  settingsNavItems.forEach(item => {
    item.addEventListener('click', () => {
      settingsNavItems.forEach(n => n.classList.remove('active'));
      item.classList.add('active');
      const targetId = item.getAttribute('data-target');
      const targetSection = document.getElementById(targetId);
      if (targetSection && settingsContentContainer) {
        const targetTop = targetSection.offsetTop - settingsContentContainer.offsetTop;
        settingsContentContainer.scrollTo({
          top: targetTop,
          behavior: 'smooth'
        });
        showToast(`Navigated to: ${item.querySelector('span').textContent}`);
      }
    });
  });

  if (settingsContentContainer) {
    settingsContentContainer.addEventListener('scroll', () => {
      let currentActiveId = '';
      settingsSections.forEach(section => {
        const top = section.offsetTop - settingsContentContainer.offsetTop;
        if (settingsContentContainer.scrollTop >= top - 60) {
          currentActiveId = section.id;
        }
      });

      if (currentActiveId) {
        settingsNavItems.forEach(item => {
          item.classList.toggle('active', item.getAttribute('data-target') === currentActiveId);
        });
      }
    });
  }

  const confidenceSlider = document.getElementById('confidenceSlider');
  const confidenceValDisplay = document.getElementById('confidenceValDisplay');
  if (confidenceSlider && confidenceValDisplay) {
    confidenceSlider.addEventListener('input', (e) => {
      confidenceValDisplay.textContent = `${e.target.value}%`;
    });
  }

  function showToast(message) {
    const toastContainer = document.getElementById('toastContainer');
    if (!toastContainer) return;
    const toast = document.createElement('div');
    toast.className = 'toast-message';
    toast.innerHTML = `<i data-lucide="info" style="width:16px; height:16px; color:#818CF8; flex-shrink:0;"></i> <span>${message}</span>`;
    toastContainer.appendChild(toast);
    if (window.lucide) lucide.createIcons();
    setTimeout(() => {
      toast.style.opacity = '0';
      setTimeout(() => toast.remove(), 300);
    }, 3000);
  }
  window.showToast = showToast;
});