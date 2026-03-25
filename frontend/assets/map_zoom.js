/**
 * Faster scroll / trackpad zoom on Plotly Mapbox maps (Dash dcc.Graph).
 * Mapbox default wheel rate is 1/450; lower divisor = more zoom per wheel notch.
 */
(function () {
  "use strict";

  var WHEEL_ZOOM_RATE = 1 / 140;
  var TRACKPAD_ZOOM_RATE = 1 / 28;

  function graphDiv() {
    var root = document.getElementById("map-graph");
    if (!root) return null;
    return root.querySelector(".js-plotly-plot") || root;
  }

  function mapboxMapFromGd(gd) {
    if (!gd || !gd._fullLayout) return null;
    var box = gd._fullLayout.mapbox;
    if (!box || !box._subplot) return null;
    var sp = box._subplot;
    return sp.map || sp._map || null;
  }

  function patchMapScrollZoom(map) {
    if (!map || !map.scrollZoom || map.__ambulatoryZoomTuned) return;
    try {
      if (typeof map.scrollZoom.setWheelZoomRate === "function") {
        map.scrollZoom.setWheelZoomRate(WHEEL_ZOOM_RATE);
      }
      if (typeof map.scrollZoom.setZoomRate === "function") {
        map.scrollZoom.setZoomRate(TRACKPAD_ZOOM_RATE);
      }
      map.__ambulatoryZoomTuned = true;
    } catch (e) {
      console.warn("[map_zoom] could not tune scroll zoom:", e);
    }
  }

  function hookGraph(gd) {
    if (!gd || gd.__ambulatoryPlotlyHooked) return;
    gd.__ambulatoryPlotlyHooked = true;
    gd.on("plotly_afterplot", function () {
      patchMapScrollZoom(mapboxMapFromGd(gd));
    });
    patchMapScrollZoom(mapboxMapFromGd(gd));
  }

  function tryHook() {
    if (typeof window.Plotly === "undefined") return;
    var gd = graphDiv();
    if (gd && gd._fullLayout && gd._fullLayout.mapbox) {
      hookGraph(gd);
    }
  }

  var obs = new MutationObserver(function () {
    tryHook();
  });
  obs.observe(document.documentElement, { childList: true, subtree: true });

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", tryHook);
  } else {
    tryHook();
  }
})();
