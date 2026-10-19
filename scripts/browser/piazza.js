// 1) On https://piazza.com/class/muomkq9jzdj104 : list feed (compare with state/piazza_seen.json)
if (location.origin !== 'https://piazza.com' || /login|signup/.test(location.pathname)) throw 'LOGIN_EXPIRED:' + location.href;
[...document.querySelectorAll('li[data-id="post_group_item"]')].map(e=>({cid:e.id.replace('_item',''),unread:e.className.includes('unread'),
  label:(e.querySelector('[role=link]')||e).getAttribute('aria-label')}))
// 2) For one post: navigate to /class/muomkq9jzdj104/post/<cid>, then run:
// for(let i=0;i<20 && document.querySelector('main').innerText.includes('Rendering markdown');i++) await new Promise(r=>setTimeout(r,500));
// document.querySelector('main').innerText
// NOTE: opening a post marks it read on Piazza. Never post/reply.
