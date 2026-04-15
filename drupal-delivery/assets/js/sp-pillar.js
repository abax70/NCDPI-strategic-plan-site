/* Scoped strategic-plan dashboard script — do not edit directly.
   Generated from source; page = 'pillar'. */
(function () {
  'use strict';

  /* SP_CONFIG: defaults merged with any page-level override set
     BEFORE this script is loaded. See README for the shape. */
  var SP_CONFIG_DEFAULTS = {
    basePath: '/sites/default/files/strategic-plan/',
    pillarPageUrl: '/strategic-plan/pillar',
    landingPageUrl: '/strategic-plan'
  };
  var userCfg = (typeof window !== 'undefined' && window.SP_CONFIG) || {};
  var SP_CONFIG = {
    basePath: userCfg.basePath != null ? userCfg.basePath : SP_CONFIG_DEFAULTS.basePath,
    pillarPageUrl: userCfg.pillarPageUrl != null ? userCfg.pillarPageUrl : SP_CONFIG_DEFAULTS.pillarPageUrl,
    landingPageUrl: userCfg.landingPageUrl != null ? userCfg.landingPageUrl : SP_CONFIG_DEFAULTS.landingPageUrl
  };
  /* Ensure basePath ends with '/' so string concatenation builds clean URLs. */
  if (SP_CONFIG.basePath && SP_CONFIG.basePath.slice(-1) !== '/') {
    SP_CONFIG.basePath += '/';
  }

  /* Resolve the wrapper element once. All DOM work is scoped to it. */
  var SP_ROOT = document.querySelector('.sp-dashboard');
  if (!SP_ROOT) {
    console.warn('[sp-dashboard] .sp-dashboard wrapper not found; script will not initialize.');
    return;
  }

  /* Page-local state that used to live on window.* */
  var allMeasures = null;          /* landing */
  var currentMeasureIndex = 0;     /* landing */
  var pillarData = null;           /* pillar */

  /* Rewrite hardcoded pillar.html / index.html links AND bare `images/`
     src paths inside the wrapper so they resolve to the configured
     SP_CONFIG values. Drupal serves our page at an arbitrary alias,
     so the static HTML fragment's relative paths must be rewritten at
     mount time and after every dynamic render. A data-sp-rewritten
     flag guards against the MutationObserver re-processing nodes. */
  function rewriteLocalLinks(root) {
    if (!root || root.nodeType !== 1) root = SP_ROOT;
    /* Handle the root node itself if it's an <a> or <img> — our
       MutationObserver hands us individual added nodes, and those
       may BE anchors or images rather than containers. */
    if (root.tagName === 'A') _fixBareHref(root);
    if (root.tagName === 'IMG') {
      var rs = root.getAttribute('data-sp-src');
      if (rs && !root.getAttribute('data-sp-rewritten')) {
        root.setAttribute('src', SP_CONFIG.basePath + rs);
        root.setAttribute('data-sp-rewritten', '1');
      } else if (!root.getAttribute('data-sp-rewritten')) {
        var rs2 = root.getAttribute('src');
        if (rs2 && rs2.indexOf('images/') === 0) {
          root.setAttribute('src', SP_CONFIG.basePath + rs2);
        }
        root.setAttribute('data-sp-rewritten', '1');
      }
    }
    var anchors = root.querySelectorAll
      ? root.querySelectorAll('a[href]:not([data-sp-rewritten])')
      : [];
    for (var i = 0; i < anchors.length; i++) {
      var a = anchors[i];
      var href = a.getAttribute('href');
      if (href) {
        var nextHref = null;
        if (href.indexOf('pillar.html') === 0) {
          nextHref = href.replace('pillar.html', SP_CONFIG.pillarPageUrl);
        } else if (href === 'index.html') {
          nextHref = SP_CONFIG.landingPageUrl;
        }
        if (nextHref != null && nextHref !== href) a.setAttribute('href', nextHref);
      }
      a.setAttribute('data-sp-rewritten', '1');
    }
    /* Static images use data-sp-src so the browser doesn't fire a
       404 against the page's own URL before JS runs. We copy the
       real path into src prefixed with SP_CONFIG.basePath. */
    var imgs = root.querySelectorAll
      ? root.querySelectorAll('img[data-sp-src]:not([data-sp-rewritten])')
      : [];
    for (var j = 0; j < imgs.length; j++) {
      var im = imgs[j];
      var dp = im.getAttribute('data-sp-src');
      if (dp) im.setAttribute('src', SP_CONFIG.basePath + dp);
      im.setAttribute('data-sp-rewritten', '1');
    }
    /* Also catch any img[src] that JS might have built with a raw
       `images/...` path. (Shouldn't happen — our transforms prefix
       with SP_CONFIG.basePath — but this is a safety net.) */
    var stragglers = root.querySelectorAll
      ? root.querySelectorAll('img[src]:not([data-sp-rewritten])')
      : [];
    for (var s = 0; s < stragglers.length; s++) {
      var im2 = stragglers[s];
      var src2 = im2.getAttribute('src');
      if (src2 && src2.indexOf('images/') === 0) {
        im2.setAttribute('src', SP_CONFIG.basePath + src2);
      }
      im2.setAttribute('data-sp-rewritten', '1');
    }
  }
  rewriteLocalLinks(SP_ROOT);
  /* Catch anchors/images added by JS renders (switchMeasure, switchPillar
     build action cards, motion cards, etc.) AND bare `images/` src
     assignments that existing code does like `headerIcon.src = m.iconUrl`.
     The data-sp-rewritten flag prevents re-processing; we also clear
     the flag off an <img> when its src is REassigned by our own code,
     so consecutive renders with new paths still get prefixed. */
  function _fixBareImg(el) {
    if (!el || el.tagName !== 'IMG') return;
    var s = el.getAttribute('src');
    if (!s || s.indexOf('images/') !== 0) return;
    var next = SP_CONFIG.basePath + s;
    if (next !== s) el.setAttribute('src', next);
  }
  function _fixBareHref(a) {
    if (!a || a.tagName !== 'A') return;
    var h = a.getAttribute('href');
    if (!h) return;
    var next = null;
    if (h.indexOf('pillar.html') === 0) {
      next = h.replace('pillar.html', SP_CONFIG.pillarPageUrl);
    } else if (h === 'index.html') {
      next = SP_CONFIG.landingPageUrl;
    }
    /* Only rewrite if the new value actually differs — prevents an
       infinite loop when SP_CONFIG.pillarPageUrl happens to equal
       the string 'pillar.html' (e.g. during local testing where the
       webmaster hasn't configured a real Drupal alias yet). */
    if (next != null && next !== h) a.setAttribute('href', next);
  }
  var _mo = new MutationObserver(function (mutations) {
    for (var m = 0; m < mutations.length; m++) {
      var mut = mutations[m];
      if (mut.type === 'childList') {
        for (var k = 0; k < mut.addedNodes.length; k++) {
          if (mut.addedNodes[k].nodeType === 1) rewriteLocalLinks(mut.addedNodes[k]);
        }
      } else if (mut.type === 'attributes' && mut.attributeName === 'src') {
        _fixBareImg(mut.target);
      } else if (mut.type === 'attributes' && mut.attributeName === 'href') {
        _fixBareHref(mut.target);
      }
    }
  });
  _mo.observe(SP_ROOT, {
    childList: true,
    subtree: true,
    attributes: true,
    attributeFilter: ['src', 'href']
  });

/* ============================================================
   Pillar Dashboard — JavaScript
   Reads data/pillar-data.json and renders focus areas, actions,
   and stories for the selected pillar. Single fetch enables
   instant pillar switching without reloads.
   ============================================================ */

// --- Pillar icon lookup (matches the sidebar image file names) ---
const PILLAR_ICONS = {
  1: SP_CONFIG.basePath + 'images/pillar-icons/Pillar-1-Icon-Students.png',
  2: SP_CONFIG.basePath + 'images/pillar-icons/Pillar-2-Icon-Educators.png',
  3: SP_CONFIG.basePath + 'images/pillar-icons/Pillar-3-Icon-Community.png',
  4: SP_CONFIG.basePath + 'images/pillar-icons/Pillar-4-Icon-HealthySafe.png',
  5: SP_CONFIG.basePath + 'images/pillar-icons/Pillar-5-Icon-Operational.png',
  6: SP_CONFIG.basePath + 'images/pillar-icons/Pillar-6-Icon-Transformative.png',
  7: SP_CONFIG.basePath + 'images/pillar-icons/Pillar-7-Icon-Celebrate.png',
  8: SP_CONFIG.basePath + 'images/pillar-icons/Pillar-8-Icon-Champions.png'
};

// Contrast-safe text colors for pillar-branded elements (WCAG 4.5:1 on white)
const PILLAR_TEXT = {
  1: '#003A70', 2: '#6E1360', 3: '#097A93', 4: '#CB5277',
  5: '#39813F', 6: '#6B6F71', 7: '#0063A2', 8: '#801323'
};

// --- DOM references ---
var pillarSelect   = SP_ROOT.querySelector('#pillarSelect');
var pillarCounter  = SP_ROOT.querySelector('#pillarCounter');
var prevBtn        = SP_ROOT.querySelector('#prevPillar');
var nextBtn        = SP_ROOT.querySelector('#nextPillar');
var heroIcon       = SP_ROOT.querySelector('#heroIcon');
var heroLabel      = SP_ROOT.querySelector('#heroLabel');
var heroTitle      = SP_ROOT.querySelector('#heroTitle');
var pillarHero     = SP_ROOT.querySelector('#pillarHero');
var pillarLinks    = SP_ROOT.querySelectorAll('.pillar-link[data-pillar]');
var tabBtns        = SP_ROOT.querySelectorAll('.tab-btn');
var tabPanels      = SP_ROOT.querySelectorAll('.tab-panel');

// Track active state
var currentPillarIndex = 0;  // 0-based index into pillarData.pillars
var activeFocusArea = { actions: 0, stories: 0 };  // track per-tab
var activeTab = 'actions';

// --- Build the pillar dropdown from JSON ---
function buildPillarDropdown(pillars) {
  pillarSelect.innerHTML = '';
  pillars.forEach(function(p, i) {
    var o = document.createElement('option');
    o.value = i;
    o.textContent = 'Pillar ' + p.pillarNum + ': ' + p.pillarName;
    pillarSelect.appendChild(o);
  });
}

// ============================================================
// switchPillar — Master function: updates everything for a pillar
// ============================================================
function switchPillar(index) {
  var pillars = pillarData.pillars;
  var total = pillars.length;

  // Wrap around
  if (index < 0) index = total - 1;
  if (index >= total) index = 0;

  currentPillarIndex = index;
  var p = pillars[index];
  var n = p.pillarNum;

  // 1. Update dropdown + counter
  pillarSelect.value = index;
  pillarCounter.textContent = 'Pillar ' + n + ' of ' + total;

  // 2. Update page title
  document.title = 'Pillar ' + n + ': ' + p.pillarName + ' | NCDPI Strategic Plan';

  // 3. Update hero
  heroIcon.src = PILLAR_ICONS[n] || '';
  heroIcon.alt = 'Pillar ' + n + ': ' + p.pillarName + ' icon';
  heroLabel.textContent = 'PILLAR ' + n;
  heroTitle.textContent = p.pillarName;

  // 4. Update CSS custom properties for pillar colors
  var root = SP_ROOT;
  root.style.setProperty('--pcolor', 'var(--pillar' + n + ')');
  root.style.setProperty('--pbg', 'var(--pillar' + n + '-bg)');
  root.style.setProperty('--ptext', 'var(--pillar' + n + '-text)');

  // 5. Update sidebar active state
  pillarLinks.forEach(function(link) {
    var linkPillar = link.getAttribute('data-pillar');
    if (linkPillar == n) {
      link.classList.add('active');
      link.setAttribute('aria-current', 'page');
    } else {
      link.classList.remove('active');
      link.removeAttribute('aria-current');
    }
  });

  // 6. Update URL without adding history entry
  var url = new URL(window.location);
  url.searchParams.set('p', n);
  history.replaceState(null, '', url);

  // 7. Reset focus area selection for both tabs
  activeFocusArea.actions = 0;
  activeFocusArea.stories = 0;

  // 8. Build focus area lists and render content for the active tab
  buildActionsFocusAreas(p);
  buildStoriesFocusAreas(p);
  buildResultsTab(p);

  // 9. Update active tab styling (re-apply pillar color to active tab)
  updateTabColors();
}

// ============================================================
// Tab switching
// ============================================================
function switchTab(tabName) {
  activeTab = tabName;

  tabBtns.forEach(function(btn) {
    var isActive = btn.id === 'tab-' + tabName;
    btn.classList.toggle('active', isActive);
    btn.setAttribute('aria-selected', isActive ? 'true' : 'false');
    // Roving tabindex: only the active tab is focusable
    btn.setAttribute('tabindex', isActive ? '0' : '-1');
  });

  tabPanels.forEach(function(panel) {
    var isActive = panel.id === 'panel-' + tabName;
    panel.classList.toggle('active', isActive);
  });

  // When switching to Stories, carry over the focus area selection from Actions
  // (but only if Stories has that same focus area available and it has stories)
  if (tabName === 'stories') {
    var p = pillarData.pillars[currentPillarIndex];
    var actionsFAIndex = activeFocusArea.actions;
    // Check if the stories focus area list has that index and it has stories
    if (actionsFAIndex < p.focusAreas.length && p.focusAreas[actionsFAIndex].stories.length > 0) {
      activeFocusArea.stories = actionsFAIndex;
    } else {
      // Find the first focus area with stories
      var firstWithStories = p.focusAreas.findIndex(function(fa) { return fa.stories.length > 0; });
      activeFocusArea.stories = firstWithStories >= 0 ? firstWithStories : 0;
    }
    highlightFocusArea('stories', activeFocusArea.stories);
    renderStories(p.focusAreas[activeFocusArea.stories]);
  }

  updateTabColors();
}

function updateTabColors() {
  // Ensure the active tab uses the pillar color
  tabBtns.forEach(function(btn) {
    if (btn.classList.contains('active')) {
      btn.style.color = '';  // let CSS handle it via var(--pcolor)
      btn.style.borderBottomColor = '';
    }
  });
}

// ============================================================
// Actions Tab
// ============================================================
function buildActionsFocusAreas(pillar) {
  // #actionsFA now targets just the listbox (items container). The heading
  // lives outside it as a sibling, so a simple wipe is enough.
  var container = SP_ROOT.querySelector('#actionsFA');
  container.innerHTML = '';

  pillar.focusAreas.forEach(function(fa, i) {
    var item = document.createElement('div');
    item.className = 'fa-item' + (i === activeFocusArea.actions ? ' active' : '');
    item.setAttribute('role', 'option');
    item.setAttribute('aria-selected', i === activeFocusArea.actions ? 'true' : 'false');
    item.setAttribute('tabindex', '0');

    // Count action statuses
    var inProgress = fa.actions.filter(function(a) { return a.hasStarted; }).length;
    var total = fa.actions.length;
    var metaText;
    if (inProgress === 0) {
      metaText = total + ' action' + (total !== 1 ? 's' : '') + ' \u00b7 Not yet started';
    } else if (inProgress === total) {
      metaText = total + ' action' + (total !== 1 ? 's' : '') + ' \u00b7 All in progress';
    } else {
      metaText = inProgress + ' of ' + total + ' in progress';
    }

    item.innerHTML =
      '<span class="action-id-badge" style="font-size:10px; margin-bottom:3px; display:inline-block;">' + fa.focusAreaId + '</span>' +
      '<div class="fa-item-name">' + fa.focusAreaName + '</div>' +
      '<div class="fa-item-meta">' + metaText + '</div>';

    item.addEventListener('click', function() {
      activeFocusArea.actions = i;
      highlightFocusArea('actions', i);
      renderActions(fa);
    });
    item.addEventListener('keydown', function(e) {
      if (e.key === 'Enter' || e.key === ' ') {
        e.preventDefault();
        activeFocusArea.actions = i;
        highlightFocusArea('actions', i);
        renderActions(fa);
      } else if (e.key === 'ArrowDown') {
        e.preventDefault();
        var nextIndex = Math.min(i + 1, pillar.focusAreas.length - 1);
        var nextItem = container.querySelectorAll('.fa-item')[nextIndex];
        if (nextItem) { nextItem.focus(); nextItem.click(); }
      } else if (e.key === 'ArrowUp') {
        e.preventDefault();
        var prevIndex = Math.max(i - 1, 0);
        var prevItem = container.querySelectorAll('.fa-item')[prevIndex];
        if (prevItem) { prevItem.focus(); prevItem.click(); }
      }
    });

    container.appendChild(item);
  });

  // Render actions for the active focus area
  if (pillar.focusAreas.length > 0) {
    renderActions(pillar.focusAreas[activeFocusArea.actions]);
  }
}

function renderActions(focusArea) {
  var container = SP_ROOT.querySelector('#actionsDetail');
  container.innerHTML = '';

  // Header
  var header = document.createElement('div');
  header.className = 'detail-header';
  header.innerHTML =
    '<h3>' + focusArea.focusAreaName + '</h3>' +
    '<span class="count-badge">' + focusArea.actions.length + ' action' + (focusArea.actions.length !== 1 ? 's' : '') + '</span>';
  container.appendChild(header);

  // Action cards
  if (focusArea.actions.length === 0) {
    var empty = document.createElement('div');
    empty.className = 'empty-state';
    empty.innerHTML = '<i class="bi bi-clipboard-check" aria-hidden="true"></i>No actions defined for this focus area yet.';
    container.appendChild(empty);
    return;
  }

  focusArea.actions.forEach(function(action) {
    var card = document.createElement('div');
    card.className = 'action-card';

    // Status line
    var statusClass, statusIcon, statusText;
    if (action.hasStarted) {
      statusClass = 'in-progress';
      statusIcon = 'bi-arrow-repeat';
      statusText = action.status || 'In Progress';
    } else {
      statusClass = 'not-started';
      statusIcon = 'bi-clock';
      statusText = action.launchText || 'Not yet started';
    }

    card.innerHTML =
      '<div class="action-card-top">' +
        '<span class="action-id-badge">' + action.actionId + '</span>' +
        '<span class="action-card-title">' + action.actionName + '</span>' +
      '</div>' +
      (action.actionDesc ? '<div class="action-card-desc">' + action.actionDesc + '</div>' : '') +
      '<div class="action-status ' + statusClass + '">' +
        '<i class="bi ' + statusIcon + '" aria-hidden="true"></i> ' + statusText +
      '</div>';

    container.appendChild(card);
  });
}

// ============================================================
// Stories Tab
// ============================================================
function buildStoriesFocusAreas(pillar) {
  // #storiesFA now targets just the listbox (items container); heading is a sibling.
  var container = SP_ROOT.querySelector('#storiesFA');
  container.innerHTML = '';

  pillar.focusAreas.forEach(function(fa, i) {
    var storyCount = fa.stories.length;
    var isDisabled = storyCount === 0;

    var item = document.createElement('div');
    item.className = 'fa-item' + (i === activeFocusArea.stories ? ' active' : '') + (isDisabled ? ' disabled' : '');
    item.setAttribute('role', 'option');
    item.setAttribute('aria-selected', i === activeFocusArea.stories ? 'true' : 'false');
    if (!isDisabled) item.setAttribute('tabindex', '0');

    var metaText = storyCount === 0 ? 'No stories yet' : storyCount + ' stor' + (storyCount === 1 ? 'y' : 'ies');

    item.innerHTML =
      '<span class="action-id-badge" style="font-size:10px; margin-bottom:3px; display:inline-block;">' + fa.focusAreaId + '</span>' +
      '<div class="fa-item-name">' + fa.focusAreaName + '</div>' +
      '<div class="fa-item-meta">' + metaText + '</div>';

    if (!isDisabled) {
      item.addEventListener('click', function() {
        activeFocusArea.stories = i;
        highlightFocusArea('stories', i);
        renderStories(fa);
      });
      item.addEventListener('keydown', function(e) {
        if (e.key === 'Enter' || e.key === ' ') {
          e.preventDefault();
          activeFocusArea.stories = i;
          highlightFocusArea('stories', i);
          renderStories(fa);
        } else if (e.key === 'ArrowDown') {
          // Mirror the Actions-tab arrow-key navigation so the keyboard UX
          // is consistent across both listboxes. Disabled items (no stories)
          // have no tabindex, so they're naturally skipped.
          e.preventDefault();
          var enabled = container.querySelectorAll('.fa-item:not(.disabled)');
          var currentIdx = Array.prototype.indexOf.call(enabled, item);
          var next = enabled[Math.min(currentIdx + 1, enabled.length - 1)];
          if (next) { next.focus(); next.click(); }
        } else if (e.key === 'ArrowUp') {
          e.preventDefault();
          var enabledUp = container.querySelectorAll('.fa-item:not(.disabled)');
          var currentIdxUp = Array.prototype.indexOf.call(enabledUp, item);
          var prev = enabledUp[Math.max(currentIdxUp - 1, 0)];
          if (prev) { prev.focus(); prev.click(); }
        }
      });
    }

    container.appendChild(item);
  });

  // Render stories for the active focus area
  if (pillar.focusAreas.length > 0) {
    renderStories(pillar.focusAreas[activeFocusArea.stories]);
  }
}

function renderStories(focusArea) {
  var container = SP_ROOT.querySelector('#storiesDetail');
  container.innerHTML = '';

  // Header
  var header = document.createElement('div');
  header.className = 'detail-header';
  header.innerHTML =
    '<h3>' + focusArea.focusAreaName + '</h3>' +
    '<span class="count-badge">' + focusArea.stories.length + ' stor' + (focusArea.stories.length === 1 ? 'y' : 'ies') + '</span>';
  container.appendChild(header);

  // Empty state
  if (focusArea.stories.length === 0) {
    var empty = document.createElement('div');
    empty.className = 'empty-state';
    empty.innerHTML = '<i class="bi bi-newspaper" aria-hidden="true"></i>No stories from the field have been linked to this focus area yet.';
    container.appendChild(empty);
    return;
  }

  // Story cards
  focusArea.stories.forEach(function(story) {
    var card = document.createElement('div');
    card.className = 'story-card';

    var metaParts = [];
    if (story.publishDate) metaParts.push(story.publishDate);
    if (story.county) metaParts.push(story.county);

    card.innerHTML =
      '<div class="story-card-title">' +
        '<a href="' + story.url + '" target="_blank" rel="noopener">' + story.title + '</a>' +
        '<i class="bi bi-box-arrow-up-right" aria-hidden="true"></i>' +
      '</div>' +
      (metaParts.length > 0 ? '<div class="story-card-meta">' + metaParts.join(' &nbsp;|&nbsp; ') + '</div>' : '') +
      (story.rationale ? '<div class="story-card-rationale">Connected because: ' + story.rationale + '</div>' : '');

    container.appendChild(card);
  });

  // Help note
  var note = document.createElement('div');
  note.className = 'stories-help';
  note.textContent = 'Stories may appear under multiple focus areas when they relate to more than one area of work.';
  container.appendChild(note);
}

// ============================================================
// Results Tab (placeholder)
// ============================================================
function buildResultsTab(pillar) {
  var container = SP_ROOT.querySelector('#resultsContent');
  container.innerHTML =
    '<i class="bi bi-bar-chart-line" aria-hidden="true"></i>' +
    '<p>Pillar-level results for <strong>' + pillar.pillarName + '</strong> will be available as data is collected and reported.</p>' +
    '<a href="index.html">&larr; View the Best in the Nation measures</a>';
}

// ============================================================
// Utility: Highlight active focus area in a tab's list
// ============================================================
function highlightFocusArea(tabName, index) {
  var containerId = tabName === 'actions' ? 'actionsFA' : 'storiesFA';
  var items = document.getElementById(containerId).querySelectorAll('.fa-item');
  items.forEach(function(item, i) {
    item.classList.toggle('active', i === index);
    item.setAttribute('aria-selected', i === index ? 'true' : 'false');
  });
}

// ============================================================
// Event listeners
// ============================================================

// Pillar switcher dropdown
pillarSelect.addEventListener('change', function() {
  switchPillar(+pillarSelect.value);
});

// Prev/Next buttons
prevBtn.addEventListener('click', function() {
  switchPillar(currentPillarIndex - 1);
});
nextBtn.addEventListener('click', function() {
  switchPillar(currentPillarIndex + 1);
});

// Keyboard: left/right arrows on pillar switcher
SP_ROOT.querySelector('.pillar-switcher').addEventListener('keydown', function(e) {
  if (e.key === 'ArrowLeft') {
    e.preventDefault();
    switchPillar(currentPillarIndex - 1);
  } else if (e.key === 'ArrowRight') {
    e.preventDefault();
    switchPillar(currentPillarIndex + 1);
  }
});

// Tab switching
tabBtns.forEach(function(btn) {
  btn.addEventListener('click', function() {
    var tabName = btn.id.replace('tab-', '');
    switchTab(tabName);
  });
  btn.addEventListener('keydown', function(e) {
    // Arrow keys cycle through tabs per ARIA tabs pattern
    var tabNames = ['actions', 'stories', 'results'];
    var currentIndex = tabNames.indexOf(btn.id.replace('tab-', ''));
    if (e.key === 'ArrowRight') {
      e.preventDefault();
      var nextTab = tabNames[(currentIndex + 1) % tabNames.length];
      document.getElementById('tab-' + nextTab).focus();
      switchTab(nextTab);
    } else if (e.key === 'ArrowLeft') {
      e.preventDefault();
      var prevTab = tabNames[(currentIndex - 1 + tabNames.length) % tabNames.length];
      document.getElementById('tab-' + prevTab).focus();
      switchTab(prevTab);
    }
  });
});

// ============================================================
// Initialize: load JSON, parse URL, render
// ============================================================
document.fonts.ready.then(function() {
  fetch(SP_CONFIG.basePath + 'data/pillar-data.json')
    .then(function(resp) { return resp.json(); })
    .then(function(data) {
      pillarData = data;

      // Build the dropdown
      buildPillarDropdown(data.pillars);

      // Parse URL parameter ?p=N (default to 1)
      var params = new URLSearchParams(window.location.search);
      var requestedPillar = parseInt(params.get('p')) || 1;

      // Find the index for the requested pillar number
      var startIndex = data.pillars.findIndex(function(p) {
        return p.pillarNum === requestedPillar;
      });
      if (startIndex < 0) startIndex = 0;

      // Render
      switchPillar(startIndex);
    })
    .catch(function(err) {
      console.error('Failed to load pillar-data.json:', err);
      SP_ROOT.querySelector('.pillar-content').innerHTML =
        '<div class="empty-state"><i class="bi bi-exclamation-triangle"></i>Failed to load pillar data. Please refresh.</div>';
    });
});

// ============================================================
// Mobile nav drawer (shared pattern with index.html)
// Shows/hides the left sidebar on screens <=768px.
// ============================================================
(function () {
  var navToggle = SP_ROOT.querySelector('#navToggle');
  var sidebar   = SP_ROOT.querySelector('#sidebarLeft');
  var backdrop  = SP_ROOT.querySelector('#drawerBackdrop');
  if (!navToggle || !sidebar || !backdrop) return;

  function openDrawer() {
    sidebar.classList.add('open');
    backdrop.classList.add('open');
    document.body.style.overflow = 'hidden'; /* scroll lock */
    navToggle.setAttribute('aria-expanded', 'true');
    navToggle.setAttribute('aria-label', 'Close navigation menu');
    var icon = navToggle.querySelector('i');
    if (icon) { icon.className = 'bi bi-x-lg'; }
  }

  function closeDrawer() {
    sidebar.classList.remove('open');
    backdrop.classList.remove('open');
    document.body.style.overflow = ''; /* scroll unlock */
    navToggle.setAttribute('aria-expanded', 'false');
    navToggle.setAttribute('aria-label', 'Open navigation menu');
    var icon = navToggle.querySelector('i');
    if (icon) { icon.className = 'bi bi-list'; }
    navToggle.focus();
  }

  navToggle.addEventListener('click', function () {
    if (sidebar.classList.contains('open')) closeDrawer();
    else openDrawer();
  });
  backdrop.addEventListener('click', closeDrawer);
  document.addEventListener('keydown', function (e) {
    if (e.key === 'Escape' && sidebar.classList.contains('open')) closeDrawer();
  });
  // Reset drawer state when viewport grows past 768px
  window.addEventListener('resize', function () {
    if (window.innerWidth > 768 && sidebar.classList.contains('open')) {
      sidebar.classList.remove('open');
      backdrop.classList.remove('open');
      document.body.style.overflow = ''; /* scroll unlock */
      navToggle.setAttribute('aria-expanded', 'false');
      var icon = navToggle.querySelector('i');
      if (icon) { icon.className = 'bi bi-list'; }
    }
  });
})();

})();
