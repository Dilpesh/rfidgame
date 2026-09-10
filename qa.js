const { chromium } = require('playwright');
const path = require('path');

(async () => {
  const browser = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium-1194/chrome-linux/chrome' });
  const errors = [];
  const page = await browser.newPage({ viewport: { width: 420, height: 860 } });
  page.on('console', (msg) => { if (msg.type() === 'error') errors.push(msg.text()); });
  page.on('pageerror', (err) => errors.push('pageerror: ' + err.message));

  const fileUrl = 'file://' + path.resolve(__dirname, 'find-and-tap.built.html');
  await page.goto(fileUrl);
  await page.waitForTimeout(300);
  await page.screenshot({ path: 'shot_1_home.png' });

  // choose developer mode
  await page.click('.mode-card.dev');
  await page.waitForTimeout(150);
  await page.screenshot({ path: 'shot_2_dashboard.png' });

  // go to setup
  await page.click('#goSetupBtn');
  await page.waitForTimeout(150);
  await page.screenshot({ path: 'shot_3_setup.png' });

  // map all 8 cards using the dev tag input
  const ids = ['red', 'blue', 'yellow', 'green', 'circle', 'square', 'triangle', 'star'];
  for (let i = 0; i < ids.length; i++) {
    await page.click(`[data-scan-for="${ids[i]}"]`);
    await page.fill('#tagInput', 'TAG' + (1000 + i));
    await page.press('#tagInput', 'Enter');
    await page.waitForTimeout(80);
  }
  await page.waitForTimeout(150);
  await page.screenshot({ path: 'shot_4_setup_mapped.png' });

  const mappingCount = await page.evaluate(() => {
    const raw = localStorage.getItem('findAndTap.mapping.v1');
    return raw ? Object.keys(JSON.parse(raw)).length : 0;
  });
  console.log('mapped count in localStorage:', mappingCount);

  // export code round-trip check
  const code = await page.evaluate(() => {
    document.getElementById('copyCodeBtn').click();
    return document.getElementById('codeOut').value;
  });
  console.log('export code length:', code.length);

  await page.click('#setupDoneBtn');
  await page.waitForTimeout(150);
  await page.screenshot({ path: 'shot_5_dashboard_ready.png' });

  const startDisabled = await page.$eval('#startGameBtn', (b) => b.disabled);
  console.log('start button disabled (should be false):', startDisabled);

  // start the game (intro line is ~9.1s; safety-net timer is duration+1.5s)
  await page.click('#startGameBtn');
  await page.waitForTimeout(11000);
  await page.screenshot({ path: 'shot_6_play.png' });

  // play through all 8 by reading the dev "waiting for" panel and typing the right tag
  for (let i = 0; i < 8; i++) {
    const expectedLabel = await page.$eval('#dcExpected', (el) => el.textContent);
    const tagSuffix = expectedLabel.match(/…(\w+)\)/);
    let tagToSend = null;
    if (tagSuffix) {
      const suffix = tagSuffix[1];
      const full = ids.map((id, i2) => 'TAG' + (1000 + i2)).find((t) => t.endsWith(suffix));
      tagToSend = full;
    }
    console.log('iter', i, 'expectedLabel=', JSON.stringify(expectedLabel), 'tagToSend=', tagToSend);
    if (!tagToSend) { console.log('could not resolve expected tag for', expectedLabel); break; }
    await page.fill('#tagInput', tagToSend);
    await page.press('#tagInput', 'Enter');
    await page.waitForTimeout(7500);
    const dcLog = await page.$eval('#dcLog', (el) => el.textContent);
    console.log('  dcLog now:', dcLog);
  }
  await page.waitForTimeout(400);
  await page.screenshot({ path: 'shot_7_complete.png' });

  const completeVisible = await page.$eval('#view-complete', (el) => !el.hidden);
  console.log('reached complete view:', completeVisible);
  const stats = await page.$eval('#completeStats', (el) => el.textContent);
  console.log('complete stats text:', stats);

  console.log('console/page errors:', errors);

  // ---- extra check: mapping should survive a reload (persists per phone) ----
  await page.reload();
  await page.waitForTimeout(200);
  await page.click('.mode-card.prod'); // switch mode to prod this time
  await page.waitForTimeout(150);
  const dashCountAfterReload = await page.$eval('#dashRingCount', (el) => el.textContent);
  const startDisabledAfterReload = await page.$eval('#startGameBtn', (b) => b.disabled);
  console.log('after reload — dashCount:', dashCountAfterReload, 'startDisabled:', startDisabledAfterReload);

  // ---- extra check: a wrong scan gently retries without advancing ----
  await page.click('#startGameBtn');
  await page.waitForTimeout(6300);
  const beforeWrong = await page.$eval('#dcExpected', (el) => el.textContent).catch(() => '(dev console hidden in prod mode, expected)');
  console.log('prod mode dev console dcExpected (should be hidden/empty):', beforeWrong);
  const dot0Class = await page.$eval('#playDots .dot', (el) => el.className);
  await page.fill('#tagInput', 'NOT-A-REAL-TAG'); // prod mode: input is present but visually hidden; still focusable
  await page.press('#tagInput', 'Enter');
  await page.waitForTimeout(500);
  const dot0ClassAfterWrong = await page.$eval('#playDots .dot', (el) => el.className);
  console.log('dot state before wrong scan:', dot0Class, '| after wrong scan (should be unchanged):', dot0ClassAfterWrong);

  await browser.close();
})();
