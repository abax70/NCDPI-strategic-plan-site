/* Scoped strategic-plan dashboard script — do not edit directly.
   Generated from source; page = 'landing'. */
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
   Chart.js integration for the Strategic Plan dashboard.
   Reads data/measures.json and renders a bar chart for the
   currently selected measure. Replaces the static HTML bars.
   ============================================================ */

// --- Style-guide colors (NCDPI Data Visualization Style Guide) ---
const COLORS = {
  baseline:  '#003A70',   // Highlighted Bar/Line (navy)
  target:    '#B7B9BB',   // Neutral Bar/Line (gray)
  meets:     '#077890',   // Bar/Line is Best (teal)
  below:     '#B33A12',   // Bar/Line is Worst (rust)
  refLine:   '#003A70',   // Reference Lines
  dataLabel: '#000000',   // Data Labels
  axisValue: '#212529',   // Axis Values — matches dpi.nc.gov body text
  gridline:  '#DEDEDE'    // Gridlines
};

// --- Diagonal hatch pattern for target bars ---
// Creates a canvas pattern with thin diagonal lines to signal "projected" data.
let _hatchPattern = null; // cleared on reload; pattern is cached after first call
function getHatchPattern() {
  if (_hatchPattern) return _hatchPattern;
  const size = 8;  // pattern tile size in px
  const c = document.createElement('canvas');
  c.width = size;
  c.height = size;
  const ctx = c.getContext('2d');
  // White background
  ctx.fillStyle = '#FFFFFF';
  ctx.fillRect(0, 0, size, size);
  // Navy diagonal stripe at 50% opacity
  ctx.strokeStyle = 'rgba(0, 58, 112, 0.5)';
  ctx.lineWidth = 1.5;
  ctx.beginPath();
  ctx.moveTo(0, size);
  ctx.lineTo(size, 0);
  ctx.stroke();
  // Wrap-around stripe for seamless tiling
  ctx.beginPath();
  ctx.moveTo(-2, 2);
  ctx.lineTo(2, -2);
  ctx.stroke();
  ctx.beginPath();
  ctx.moveTo(size - 2, size + 2);
  ctx.lineTo(size + 2, size - 2);
  ctx.stroke();
  _hatchPattern = ctx.createPattern(c, 'repeat');
  return _hatchPattern;
}

// --- Value formatting ---
function formatValue(value, fmt) {
  if (value == null) return '';
  switch (fmt) {
    case '#.#%':
      return value.toFixed(1) + '%';
    case '#.#':
      return value.toFixed(1);
    case '#,###':
      return Math.round(value).toLocaleString('en-US');
    case '#':
      return Math.round(value).toString();
    default:
      return value.toString();
  }
}

// --- Determine the display value and color for each data point ---
function getBarValue(d) {
  // Priority: actual (future reported) > baseline (historical)
  if (d.actual != null) return d.actual;
  if (d.baseline != null) return d.baseline;
  if (d.target != null) return d.target;
  return null;
}

function getBarColor(d) {
  if (d.actual != null) {
    // Future year with reported data — compare to target
    return (d.target != null && d.actual >= d.target) ? COLORS.meets : COLORS.below;
  }
  if (d.baseline != null) return COLORS.baseline;
  if (d.target != null) return getHatchPattern();
  return 'transparent';
}

function getBarBorder(d) {
  // Only target-only bars get a visible border
  if (d.baseline == null && d.actual == null && d.target != null) {
    return { width: 1.5, color: COLORS.baseline };
  }
  return { width: 0, color: 'transparent' };
}

// --- Render the chart ---
let currentChart = null;

function renderChart(measure) {
  const wrap = SP_ROOT.querySelector('#chartWrap');
  const canvas = SP_ROOT.querySelector('#measureChart');
  const legendEl = SP_ROOT.querySelector('#chartLegend');

  // Handle measures with no data
  if (!measure.dataSeries || measure.dataSeries.length === 0) {
    canvas.style.display = 'none';
    legendEl.style.display = 'none';
    targetCallout.style.display = 'none';
    // Add "no data" message if not already present
    if (!wrap.querySelector('.chart-no-data')) {
      const msg = document.createElement('div');
      msg.className = 'chart-no-data';
      msg.textContent = 'No data available yet.';
      wrap.appendChild(msg);
    }
    return;
  }

  // Remove any "no data" message and restore canvas
  const noData = wrap.querySelector('.chart-no-data');
  if (noData) noData.remove();
  canvas.style.display = '';
  legendEl.style.display = '';

  // Destroy previous chart instance
  if (currentChart) {
    currentChart.destroy();
    currentChart = null;
  }

  // Build arrays from dataSeries
  const labels = measure.dataSeries.map(d => d.year);
  const values = measure.dataSeries.map(d => getBarValue(d));
  const bgColors = measure.dataSeries.map(d => getBarColor(d));
  const borderColors = measure.dataSeries.map(d => getBarBorder(d).color);
  const borderWidths = measure.dataSeries.map(d => getBarBorder(d).width);

  // Find the 2030 target for the annotation line
  const finalTarget = measure.dataSeries.reduce((last, d) => {
    return d.target != null ? d : last;
  }, null);

  // Build annotation config
  const annotations = {};
  if (finalTarget) {
    annotations.targetLine = {
      type: 'line',
      yMin: finalTarget.target,
      yMax: finalTarget.target,
      borderColor: COLORS.refLine,
      borderWidth: 2,
      borderDash: [6, 4]
    };
  }

  // Update the HTML target callout
  if (finalTarget) {
    targetCallout.style.display = '';
    targetCalloutText.textContent = finalTarget.year + ' Target: ' + formatValue(finalTarget.target, measure.valueFormat);
  } else {
    targetCallout.style.display = 'none';
  }

  // Inline plugin: draw value labels above each bar
  const valueLabelsPlugin = {
    id: 'valueLabels',
    afterDatasetsDraw(chart) {
      const ctx = chart.ctx;
      const meta = chart.getDatasetMeta(0);
      ctx.save();
      // Smaller label font on mobile to keep bars from being overrun
      // by their own values when the chart is scaled down.
      const labelFontSize = window.innerWidth <= 768 ? 11 : 13;
      ctx.font = "600 " + labelFontSize + "px 'Source Sans Pro', sans-serif";
      ctx.textAlign = 'center';
      meta.data.forEach((bar, i) => {
        const val = chart.data.datasets[0].data[i];
        if (val == null) return;
        const formatted = formatValue(val, measure.valueFormat);
        const x = bar.x;
        const y = bar.y - 8;
        // White background pad — erases any reference line behind the label
        const textWidth = ctx.measureText(formatted).width;
        const padX = 4, padY = 2;
        ctx.fillStyle = '#FFFFFF';
        ctx.fillRect(x - textWidth / 2 - padX, y - 11 - padY, textWidth + padX * 2, 14 + padY * 2);
        // Draw the label text
        ctx.fillStyle = COLORS.dataLabel;
        ctx.fillText(formatted, x, y);
      });
      ctx.restore();
    }
  };

  // Create the chart
  const ctx = canvas.getContext('2d');
  currentChart = new Chart(ctx, {
    type: 'bar',
    data: {
      labels: labels,
      datasets: [{
        data: values,
        backgroundColor: bgColors,
        borderColor: borderColors,
        borderWidth: borderWidths,
        borderRadius: { topLeft: 4, topRight: 4 },
        borderSkipped: 'bottom',
        maxBarThickness: 56
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      layout: {
        padding: { top: 28 }   // room for value labels above bars
      },
      scales: {
        y: {
          display: false,
          beginAtZero: true,
          max: measure.yAxisMax || undefined
        },
        x: {
          grid: { display: false },
          ticks: {
            color: COLORS.axisValue,
            // Smaller ticks and angled labels on mobile; otherwise the
            // year labels crowd together or overflow the canvas.
            font: {
              size: window.innerWidth <= 768 ? 11 : 13,
              weight: '600'
            },
            maxTicksLimit: window.innerWidth <= 768 ? 6 : undefined,
            maxRotation: window.innerWidth <= 480 ? 45 : 0,
            minRotation: 0,
            autoSkip: true
          }
        }
      },
      plugins: {
        legend: { display: false },
        tooltip: { enabled: false },
        annotation: {
          drawTime: 'beforeDatasetsDraw',
          annotations: annotations
        }
      }
    },
    plugins: [valueLabelsPlugin]
  });

  // Update the canvas aria-label
  canvas.setAttribute('aria-label',
    'Bar chart showing ' + measure.name + ' progress toward ' +
    (finalTarget ? finalTarget.year + ' target of ' + formatValue(finalTarget.target, measure.valueFormat) : 'target'));

  // Update the legend to reflect which bar types are present
  updateLegend(measure, legendEl);
}

// --- Update the HTML legend based on which bar types appear ---
function updateLegend(measure, legendEl) {
  const hasBaseline = measure.dataSeries.some(d => d.baseline != null);
  const hasTarget = measure.dataSeries.some(d => d.baseline == null && d.actual == null && d.target != null);
  const hasMeets = measure.dataSeries.some(d => d.actual != null && d.target != null && d.actual >= d.target);
  const hasBelow = measure.dataSeries.some(d => d.actual != null && (d.target == null || d.actual < d.target));

  let html = '';
  if (hasBaseline) html += '<span><span class="swatch baseline"></span> Actual</span>';
  if (hasTarget)   html += '<span><span class="swatch target"></span> Target</span>';
  if (hasMeets)    html += '<span><span class="swatch meets"></span> Meets Target</span>';
  if (hasBelow)    html += '<span><span class="swatch below"></span> Below Target</span>';
  legendEl.innerHTML = html;
}

// ============================================================
// Carousel interactivity — wires dropdown, arrows, and keyboard
// to switchMeasure(), which updates every section from JSON.
// ============================================================

// --- DOM references (stable — these elements never get replaced) ---
const selectEl      = SP_ROOT.querySelector('.carousel-select');
const counterEl     = SP_ROOT.querySelector('.carousel-counter');
const prevBtn       = SP_ROOT.querySelector('.carousel-btn[aria-label="Previous measure"]');
const nextBtn       = SP_ROOT.querySelector('.carousel-btn[aria-label="Next measure"]');
const measureHeader = SP_ROOT.querySelector('.measure-header');
const headerIcon    = measureHeader.querySelector('img');
const headerTitle   = measureHeader.querySelector('h2');
const headerGoal    = measureHeader.querySelector('.goal');
const statusPill    = measureHeader.querySelector('.status-pill');
const bigNumber     = SP_ROOT.querySelector('.current-value .big-number');
const contextText   = SP_ROOT.querySelector('.current-value .context');
const notesSection  = SP_ROOT.querySelector('.notes-section');
const targetCallout     = SP_ROOT.querySelector('#targetCallout');
const targetCalloutText = SP_ROOT.querySelector('#targetCalloutText');
const sidebarRight  = SP_ROOT.querySelector('.sidebar-right');
const pillarLinks   = SP_ROOT.querySelectorAll('.pillar-link');

// Star SVG used in the status pill for record-high measures
const STAR_SVG = '<svg width="14" height="14" viewBox="0 0 24 24" fill="#C5960C" aria-hidden="true"><path d="M12 2L15.09 8.26L22 9.27L17 14.14L18.18 21.02L12 17.77L5.82 21.02L7 14.14L2 9.27L8.91 8.26L12 2Z"/></svg>';

// --- Build the dropdown from JSON — flat list under a single header ---
function buildDropdown(measures) {
  selectEl.innerHTML = '';
  var og = document.createElement('optgroup');
  og.label = 'Best in the Nation Measures';
  measures.forEach(function(m, i) {
    var o = document.createElement('option');
    o.value = i;
    o.textContent = m.name;
    og.appendChild(o);
  });
  selectEl.appendChild(og);
}

// --- Core: switch to measure at the given index ---
function switchMeasure(index) {
  var measures = allMeasures;
  var total = measures.length;

  // Wrap around
  if (index < 0) index = total - 1;
  if (index >= total) index = 0;

  currentMeasureIndex = index;
  var m = measures[index];

  // 1. Sync dropdown + counter
  selectEl.value = index;
  counterEl.textContent = 'Measure ' + (index + 1) + ' of ' + total;

  // 2. Measure header — icon, title, goal, status pill
  headerIcon.src = m.iconUrl || '';
  headerIcon.alt = m.name + ' icon';
  headerTitle.textContent = m.name;
  headerGoal.textContent = m.goal;

  if (m.statusType === 'record-high') {
    statusPill.style.display = '';
    statusPill.className = 'status-pill';
    statusPill.innerHTML = STAR_SVG + ' Record High';
  } else {
    // Baseline measures: hide the pill entirely
    statusPill.style.display = 'none';
  }

  // 3. Big-number callout
  bigNumber.textContent = m.currentValue || '\u2014';
  contextText.textContent = m.currentDescription || '';

  // 4. Chart (renderChart already handles destroy + no-data state)
  renderChart(m);

  // 5. Notes section — definition, next update, source
  var notesHTML = '';
  if (m.definition) {
    notesHTML += '<p><strong>Definition:</strong> ' + m.definition + '</p>';
  }
  if (m.nextUpdate) {
    notesHTML += '<p><strong>Next update:</strong> ' + m.nextUpdate + '</p>';
  }
  if (m.sourceLabel && m.sourceUrl) {
    notesHTML += '<p><strong>Source:</strong> <a href="' + m.sourceUrl + '" target="_blank">' + m.sourceLabel + '</a></p>';
  } else if (m.sourceLabel) {
    notesHTML += '<p><strong>Source:</strong> ' + m.sourceLabel + '</p>';
  }
  notesSection.innerHTML = notesHTML;

  // 6. Right sidebar — badge
  var badgeDiv = sidebarRight.querySelector('.record-badge');
  if (m.badgeImageUrl) {
    badgeDiv.style.display = '';
    badgeDiv.innerHTML = '<img src="' + m.badgeImageUrl + '" alt="' + (m.badgeAltText || '') + '">';
  } else {
    badgeDiv.style.display = 'none';
  }

  // 7. Right sidebar — Why It Counts
  var whyPanel = sidebarRight.querySelector('.why-panel p');
  whyPanel.textContent = m.whyItCounts || '';

  // 8. Right sidebar — What's in Motion cards
  var motionContainer = sidebarRight.querySelectorAll('.sidebar-panel')[1]; // 2nd panel
  // Remove existing motion cards
  var oldCards = motionContainer.querySelectorAll('.motion-card');
  oldCards.forEach(function(card) { card.remove(); });
  // Build new cards from data
  if (m.whatsInMotion && m.whatsInMotion.length > 0) {
    m.whatsInMotion.forEach(function(item) {
      var card = document.createElement('div');
      card.className = 'motion-card';
      // Per-card pillar coloring: parse pillar number from planRef (e.g., "P2.F2.A2" → 2)
      var cardPillar = (item.planRef && parseInt(item.planRef.charAt(1))) || m.pillarNumber;
      card.style.setProperty('--pcolor', 'var(--pillar' + cardPillar + ')');
      card.style.setProperty('--pbg', 'var(--pillar' + cardPillar + '-bg)');
      card.style.setProperty('--ptext', 'var(--pillar' + cardPillar + '-text)');
      card.innerHTML =
        // h3 to keep heading hierarchy (h1 page, h2 measure, h3 panel cards).
        '<h3>' + item.title + '</h3>' +
        '<p>' + item.description + '</p>' +
        '<a href="' + (item.linkUrl || '#') + '">' + (item.linkText || 'See Pillar ' + m.pillarNumber + ' \u2192') + '</a>';
      motionContainer.appendChild(card);
    });
  }

  // 9. Right sidebar — More Data link
  var moreDataPanel = sidebarRight.querySelectorAll('.sidebar-panel')[2]; // 3rd panel
  if (m.moreDataUrl) {
    moreDataPanel.style.display = '';
    var moreLink = moreDataPanel.querySelector('.more-data-link');
    moreLink.href = m.moreDataUrl;
    moreLink.textContent = (m.moreDataText || 'Explore data') + ' \u2192';
  } else {
    moreDataPanel.style.display = 'none';
  }

  // 10. Pillar color switching — update --pcolor/--pbg on sidebar
  var n = m.pillarNumber;
  sidebarRight.style.setProperty('--pcolor', 'var(--pillar' + n + ')');
  sidebarRight.style.setProperty('--pbg', 'var(--pillar' + n + '-bg)');

  // 11. Left sidebar — highlight the active pillar
  pillarLinks.forEach(function(link, i) {
    if (i === n - 1) {
      link.classList.add('active');
      link.setAttribute('aria-current', 'page');
    } else {
      link.classList.remove('active');
      link.removeAttribute('aria-current');
    }
  });
}

// --- Event listeners ---
selectEl.addEventListener('change', function() {
  switchMeasure(+selectEl.value);
});

prevBtn.addEventListener('click', function() {
  switchMeasure(currentMeasureIndex - 1);
});

nextBtn.addEventListener('click', function() {
  switchMeasure(currentMeasureIndex + 1);
});

// Keyboard: left/right arrows when carousel header or main content has focus
SP_ROOT.querySelector('.carousel-header').addEventListener('keydown', function(e) {
  if (e.key === 'ArrowLeft') {
    e.preventDefault();
    switchMeasure(currentMeasureIndex - 1);
  } else if (e.key === 'ArrowRight') {
    e.preventDefault();
    switchMeasure(currentMeasureIndex + 1);
  }
});

// --- Initialize: load JSON, build dropdown, render first measure ---
document.fonts.ready.then(function() {
  fetch(SP_CONFIG.basePath + 'data/measures.json')
    .then(function(resp) { return resp.json(); })
    .then(function(measures) {
      allMeasures = measures;
      currentMeasureIndex = 0;
      buildDropdown(measures);
      switchMeasure(0);
    })
    .catch(function(err) {
      console.error('Failed to load measures.json:', err);
    });
});

// ============================================================
// Mobile nav drawer
// Shows/hides the left sidebar on screens <=768px. Clicking the
// backdrop or pressing Escape closes the drawer. Body scroll is
// locked while open so the fixed drawer is scrollable on its own.
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
    // Swap icon to an X while open
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
    // Return focus to the toggle button (accessibility)
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
  // If the viewport grows past 768px while the drawer is open, reset state
  // so the sidebar appears normally on desktop without the "open" override.
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

// ============================================================
// Right-sidebar accordion (mobile only)
// At <=768px each .sidebar-panel-title becomes a clickable toggle
// that collapses/expands the panel body. On desktop these titles
// are plain headings — this behavior only triggers below 768px.
// ============================================================
(function () {
  var sidebarRight = SP_ROOT.querySelector('.sidebar-right');
  if (!sidebarRight) return;

  function isMobile() { return window.innerWidth <= 768; }

  // Delegate click handler on the right sidebar
  sidebarRight.addEventListener('click', function (e) {
    if (!isMobile()) return;
    var title = e.target.closest('.sidebar-panel-title');
    if (!title) return;
    var panel = title.closest('.sidebar-panel');
    if (!panel) return;
    panel.classList.toggle('collapsed');
    // Update aria-expanded on the title for screen readers
    var expanded = !panel.classList.contains('collapsed');
    title.setAttribute('aria-expanded', expanded ? 'true' : 'false');
  });

  // Initialize ARIA roles on the panel titles for mobile context.
  // Buttons would be more semantically correct, but these are existing
  // .sidebar-panel-title divs — we augment with role=button + tabindex.
  SP_ROOT.querySelectorAll('.sidebar-panel-title').forEach(function (t) {
    t.setAttribute('role', 'button');
    t.setAttribute('tabindex', '0');
    t.setAttribute('aria-expanded', 'true');
    // Keyboard support: Enter/Space trigger the same click handler
    t.addEventListener('keydown', function (e) {
      if (!isMobile()) return;
      if (e.key === 'Enter' || e.key === ' ') {
        e.preventDefault();
        t.click();
      }
    });
  });

  // On resize past desktop, remove any collapsed state so panels
  // don't mysteriously hide sections when the layout reverts.
  window.addEventListener('resize', function () {
    if (!isMobile()) {
      SP_ROOT.querySelectorAll('.sidebar-panel.collapsed').forEach(function (p) {
        p.classList.remove('collapsed');
        var t = p.querySelector('.sidebar-panel-title');
        if (t) t.setAttribute('aria-expanded', 'true');
      });
    }
  });
})();

// ============================================================
// Chart responsiveness — re-render on viewport change
// Chart.js handles its own canvas resize, but tick font size and
// rotation are pinned at creation. We debounce a resize handler
// to re-render the current measure when the viewport crosses a
// breakpoint so labels stay legible.
// ============================================================
(function () {
  var resizeTimer = null;
  var lastBreakpoint = getBreakpoint();

  function getBreakpoint() {
    var w = window.innerWidth;
    if (w <= 480) return 'xs';
    if (w <= 768) return 'sm';
    if (w <= 1024) return 'md';
    return 'lg';
  }

  window.addEventListener('resize', function () {
    if (resizeTimer) clearTimeout(resizeTimer);
    resizeTimer = setTimeout(function () {
      var bp = getBreakpoint();
      if (bp !== lastBreakpoint) {
        lastBreakpoint = bp;
        // Re-render only if measures are loaded. switchMeasure() rebuilds
        // the chart with the current viewport's tick/font settings.
        if (allMeasures && currentMeasureIndex != null) {
          switchMeasure(currentMeasureIndex);
        }
      }
    }, 200);
  });
})();

})();
