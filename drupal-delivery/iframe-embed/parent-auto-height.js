/*
 * ===========================================================
 * NCDPI Strategic Plan — iframe auto-height listener
 * ===========================================================
 *
 * Put this on the host page (e.g. a Drupal page on dpi.nc.gov)
 * that contains an <iframe class="sp-dashboard-iframe" ...> of
 * the Strategic Plan dashboard.
 *
 * Listens for postMessage events from the iframe and resizes
 * any matching iframe to match the dashboard's content height,
 * so the page shows no whitespace or double scrollbars.
 *
 * Usage:
 *   <script src="/path/to/parent-auto-height.js"></script>
 *
 * or paste the contents inline inside a <script> tag on the
 * host page. The file is self-contained and IIFE-wrapped —
 * nothing is exposed globally.
 *
 * Safe to include even on pages WITHOUT the iframe; the
 * listener only activates when a matching message arrives.
 * ===========================================================
 */
(function () {
  'use strict';

  window.addEventListener('message', function (e) {
    var d = e.data;
    if (!d || d.type !== 'sp-dashboard-height') return;
    if (typeof d.height !== 'number' || d.height < 200) return;

    var iframes = document.querySelectorAll('iframe.sp-dashboard-iframe');
    for (var i = 0; i < iframes.length; i++) {
      /* Only resize the iframe whose contentWindow sent the
         message — important when multiple Strategic-Plan iframes
         share a page (e.g. landing + a specific pillar). */
      if (iframes[i].contentWindow === e.source) {
        iframes[i].style.height = d.height + 'px';
        break;
      }
    }
  });
})();
