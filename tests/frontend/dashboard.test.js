import {JSDOM} from 'jsdom';
import fs from 'fs';

const html=fs.readFileSync('app/templates/pages/index.html','utf8');

jest.spyOn(global,'fetch');

beforeEach(()=>{
  fetch.mockResolvedValue({ok:true,json:async()=>[]});
  document.body.innerHTML=new JSDOM(html).window.document.body.innerHTML;
  // insert basic week selector options
  const sel=document.getElementById('week-selector');
  sel.innerHTML='<option value="2025-W01">2025-W01</option>';
});

test('changing week selector calls API',async()=>{
  await import('../../app/static/js/dashboard.js');
  const sel=document.getElementById('week-selector');
  sel.value='2025-W01';
  sel.dispatchEvent(new Event('change'));
  expect(fetch).toHaveBeenCalledWith('/metrics/behavior/trips?week=2025-W01');
});

test('table updates from response',async()=>{
  fetch.mockResolvedValueOnce({ok:true,json:async()=>[{tripId:'t1',driverId:'d1',week:'2025-W01',totalUnsafeCount:1,distanceKm:10,ubpk:0.1}]});
  await import('../../app/static/js/dashboard.js');
  const row=document.querySelector('#trips-tbody tr');
  expect(row.querySelector('td').textContent).toBe('t1');
});
