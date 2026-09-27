function normalizeSearch(text) {
  return text.normalize('NFKD').replace(/\p{M}/gu, '').toLocaleLowerCase();
}

function matchesRestaurant(card, query, region, category) {
  const words = normalizeSearch(query).trim().split(/\s+/).filter(Boolean);
  return (!region || card.region === region) && (!category || card.category === category)
    && words.every(word => normalizeSearch(card.text).includes(word));
}

function languageTarget(href, hash) {
  return href.split('#')[0] + hash;
}

if (typeof module !== 'undefined') module.exports = { matchesRestaurant, languageTarget };

if (typeof document !== 'undefined') {
  const search = document.getElementById('food-search');
  const region = document.getElementById('food-region');
  const category = document.getElementById('food-category');
  const count = document.getElementById('food-count');
  const groups = [...document.querySelectorAll('#food-options .food-group')];
  const cards = [...document.querySelectorAll('article.restaurant')].map(element => ({
    element, text: element.textContent + ' ' + (element.dataset.search || ''),
    region: element.dataset.region, category: element.dataset.category
  }));
  let savedOpen = null;

  function filterRestaurants() {
    const active = Boolean(search.value.trim() || region.value || category.value);
    if (active && !savedOpen) savedOpen = groups.map(group => group.open);
    let visible = 0;
    for (const card of cards) {
      card.element.hidden = !matchesRestaurant(card, search.value, region.value, category.value);
      if (!card.element.hidden) visible++;
    }
    groups.forEach((group, index) => {
      group.hidden = !cards.some(card => group.contains(card.element) && !card.element.hidden);
      if (active && !group.hidden) group.open = true;
      if (!active && savedOpen) group.open = savedOpen[index];
    });
    if (!active) savedOpen = null;
    count.textContent = document.documentElement.lang === 'ja'
      ? visible + ' / ' + cards.length + ' 件' + (visible ? '' : ' · 条件を変えてください')
      : visible + ' / ' + cards.length + '곳' + (visible ? '' : ' · 검색 조건을 바꿔 주세요');
  }

  function resetFilters() {
    search.value = region.value = category.value = '';
    filterRestaurants();
  }

  search.addEventListener('input', filterRestaurants);
  region.addEventListener('change', filterRestaurants);
  category.addEventListener('change', filterRestaurants);
  document.getElementById('food-reset').addEventListener('click', resetFilters);
  document.getElementById('food-filters').hidden = false;
  filterRestaurants();

  function revealHash() {
    let id;
    try { id = decodeURIComponent(location.hash.slice(1)); } catch { return; }
    const target = document.getElementById(id);
    if (!target) return;
    if (target.closest('#food-options') && target.id !== 'food-options') resetFilters();
    if (target.tagName === 'DETAILS') target.open = true;
    for (let parent = target.parentElement; parent; parent = parent.parentElement) {
      if (parent.tagName === 'DETAILS') parent.open = true;
    }
    requestAnimationFrame(() => target.scrollIntoView({ block: 'start' }));
  }
  window.addEventListener('hashchange', revealHash);
  document.addEventListener('click', event => {
    const anchor = event.target.closest('a[href^="#"]');
    if (anchor && anchor.hash === location.hash) revealHash();
  });
  if (location.hash) revealHash();

  document.querySelectorAll('.language-switch a').forEach(anchor => {
    anchor.addEventListener('click', () => {
      // Keep the visible section; a stale hash can point to a section already scrolled past.
      const sections = [...document.querySelectorAll('main section[id], main .section-intro[id]')];
      const visible = sections.find(section => {
        const rect = section.getBoundingClientRect();
        return rect.top <= 110 && rect.bottom > 110;
      }) || sections.find(section => section.getBoundingClientRect().top > 0);
      const inHero = document.querySelector('.hero').getBoundingClientRect().bottom > 110;
      anchor.href = languageTarget(anchor.getAttribute('href'), inHero ? '' : visible ? '#' + visible.id : location.hash);
    });
  });
}
