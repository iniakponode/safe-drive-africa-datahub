import {JSDOM} from 'jsdom';
import fs from 'fs';

const html = fs.readFileSync('app/templates/base.html','utf8');

beforeEach(() => {
  const dom = new JSDOM(html);
  global.document = dom.window.document;
  global.window = dom.window;
});

test('populates week selector immediately when DOM already loaded', async () => {
  // simulate DOM already loaded state
  document.readyState = 'complete';
  await import('../../app/static/js/main.js');
  const options = document.querySelectorAll('#week-selector option');
  expect(options.length).toBeGreaterThan(0);
});
