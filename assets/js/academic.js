// Highlights the nav item for the section currently in view.
(function () {
  var links = Array.prototype.slice.call(
    document.querySelectorAll('.site-header nav a[href^="#"]')
  );
  if (!links.length || !('IntersectionObserver' in window)) return;

  var byId = {};
  var targets = [];
  links.forEach(function (link) {
    var id = link.getAttribute('href').slice(1);
    var el = document.getElementById(id);
    if (el) {
      byId[id] = link;
      targets.push(el);
    }
  });
  if (!targets.length) return;

  function setCurrent(id) {
    links.forEach(function (l) { l.removeAttribute('aria-current'); });
    if (byId[id]) byId[id].setAttribute('aria-current', 'true');
  }

  var visible = {};

  var observer = new IntersectionObserver(
    function (entries) {
      entries.forEach(function (entry) {
        visible[entry.target.id] = entry.isIntersecting ? entry.intersectionRatio : 0;
      });

      var best = null;
      var bestRatio = 0;
      targets.forEach(function (el) {
        var ratio = visible[el.id] || 0;
        if (ratio > bestRatio) {
          bestRatio = ratio;
          best = el.id;
        }
      });

      if (!best) {
        best = targets[0].id;
        targets.forEach(function (el) {
          if (el.getBoundingClientRect().top <= 120) best = el.id;
        });
      }
      setCurrent(best);
    },
    { rootMargin: '-96px 0px -55% 0px', threshold: [0, 0.1, 0.25, 0.5, 1] }
  );

  targets.forEach(function (el) { observer.observe(el); });
  setCurrent(targets[0].id);
})();
