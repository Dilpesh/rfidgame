// PNG per card at 300 dpi (CR80 54 x 85.6 mm = 638 x 1011 px), a contact sheet, and the A4 print page.
const { chromium } = require('playwright');
const path = require('path'), fs = require('fs');
(async () => {
  const dir = __dirname, out = path.join(dir, 'png'); fs.mkdirSync(out, { recursive: true });
  const b = await chromium.launch();
  const p = await b.newPage({ viewport: { width: 900, height: 900 }, deviceScaleFactor: 3.126 });
  await p.goto('file://' + path.join(dir, 'bobo-cards.html'));
  await p.addStyleTag({ content: '.howto{display:none}' });
  await p.waitForTimeout(300);
  const ids = await p.$$eval('.label', els => els.map(e => e.dataset.card));
  for (const id of ids) await (await p.$(`.label[data-card="${id}"]`)).screenshot({ path: path.join(out, id + '.png') });
  await p.setViewportSize({ width: 760, height: 900 });
  await (await p.$('.sheet')).screenshot({ path: path.join(out, 'contact-sheet.png') });
  await p.pdf({ path: path.join(out, 'bobo-cards-a4.pdf'), format: 'A4', printBackground: true, preferCSSPageSize: true });
  await b.close(); console.log('rendered', ids.join(', '));
})();
