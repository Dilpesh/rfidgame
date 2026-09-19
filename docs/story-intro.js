/* story-intro.js — the screen a grown-up sees before pressing Start.
 *
 * Two jobs, both for the parent rather than the child:
 *   1. Which cards this story needs, so they can be found before it begins
 *      rather than hunted for mid-scene with a child waiting.
 *   2. What the story will ask the child to physically do — so nobody starts a
 *      jumping game in a waiting room, or at bedtime, or on a full stomach.
 *
 * StoryIntro.show({ title, cards:[{icon,label,note}], activities:[...],
 *                   minutes, onStart })
 * StoryIntro.seen(key) / StoryIntro.forget(key)
 */
window.StoryIntro = (function () {
  const k = (key) => 'storyIntro:' + key;
  const seen = (key) => { try { return localStorage.getItem(k(key)) === '1'; } catch { return false; } };
  const remember = (key) => { try { localStorage.setItem(k(key), '1'); } catch {} };

  function show(o) {
    const cards = o.cards || [], acts = o.activities || [];
    const el = document.createElement('div');
    el.id = 'storyIntro';
    el.innerHTML =
      '<div class="si-box">' +
        '<h2 style="margin:0 0 2px;font-size:22px">' + (o.title || 'Before you start') + '</h2>' +
        (o.minutes ? '<p style="margin:0 0 16px;color:#6b7a85;font-size:14px">About ' +
          o.minutes + ' minutes · ' + cards.length + ' cards</p>' : '') +

        '<h3 style="margin:14px 0 8px;font-size:14px;letter-spacing:.08em;' +
          'text-transform:uppercase;color:#8c9aa4">Cards you will need</h3>' +
        '<div class="si-cards">' +
          cards.map(c =>
            '<div class="si-card"><span class="si-ico">' + c.icon + '</span>' +
            '<b>' + c.label + '</b>' +
            (c.note ? '<i>' + c.note + '</i>' : '') + '</div>').join('') +
        '</div>' +

        (acts.length ?
        '<div class="si-move">' +
          '<h3 style="margin:0 0 6px;font-size:15px">🤸 This story gets them moving</h3>' +
          '<p style="margin:0 0 8px;color:#4a5a66;font-size:14px">Along the way the story will ask your ' +
          'child to:</p>' +
          '<ul style="margin:0 0 10px;padding-left:20px;color:#2c3a45">' +
            acts.map(a => '<li style="margin:3px 0">' + a + '</li>').join('') +
          '</ul>' +
          '<p style="margin:0;color:#6b7a85;font-size:13px">Best played with room to move and something to ' +
          'drink nearby. If your child is unwell, just after a meal, or settling down for the night, this ' +
          'one is better saved for later.</p>' +
        '</div>' : '') +

        '<button id="si-go">Start the story</button>' +
        '<button id="si-skip">Don\'t show this again</button>' +
      '</div>';

    Object.assign(el.style, { position: 'fixed', inset: '0', zIndex: '9997', display: 'flex',
      alignItems: 'center', justifyContent: 'center', padding: '16px',
      background: 'rgba(12,16,20,.66)', backdropFilter: 'blur(3px)',
      font: '15px/1.55 system-ui,-apple-system,sans-serif' });

    const css = document.createElement('style');
    css.textContent =
      '#storyIntro .si-box{background:#fff;color:#16202a;border-radius:22px;padding:24px 22px;' +
        'max-width:440px;width:100%;max-height:88vh;overflow-y:auto;box-shadow:0 24px 60px rgba(0,0,0,.3)}' +
      '#storyIntro .si-cards{display:grid;grid-template-columns:repeat(auto-fit,minmax(92px,1fr));gap:8px}' +
      '#storyIntro .si-card{background:#f4f7f5;border-radius:14px;padding:10px 6px;text-align:center}' +
      '#storyIntro .si-ico{display:block;font-size:30px;line-height:1.1}' +
      '#storyIntro .si-card b{display:block;font-size:12.5px;margin-top:4px;letter-spacing:.03em}' +
      '#storyIntro .si-card i{display:block;font-size:11px;font-style:normal;color:#7d8c97;margin-top:2px}' +
      '#storyIntro .si-move{margin-top:18px;background:#fff7e8;border:1px solid #f0dcb8;' +
        'border-radius:16px;padding:14px 16px}' +
      '#storyIntro button{width:100%;border:0;border-radius:14px;font:inherit;cursor:pointer}' +
      '#storyIntro #si-go{margin-top:18px;padding:16px;font-size:17px;font-weight:800;' +
        'background:#173f28;color:#fff}' +
      '#storyIntro #si-skip{margin-top:8px;padding:10px;font-size:13px;background:none;color:#8c9aa4;' +
        'text-decoration:underline}';
    el.appendChild(css);
    document.body.appendChild(el);

    const go = (forget) => { if (forget && o.key) remember(o.key); el.remove(); (o.onStart || (() => {}))(); };
    el.querySelector('#si-go').onclick = () => go(false);
    el.querySelector('#si-skip').onclick = () => go(true);
  }

  return { show, seen, forget: (key) => { try { localStorage.removeItem(k(key)); } catch {} } };
})();
