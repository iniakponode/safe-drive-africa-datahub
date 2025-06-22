import {JSDOM} from 'jsdom';
import fs from 'fs';

const html=fs.readFileSync('app/templates/pages/driver_analysis.html','utf8');

jest.spyOn(global,'fetch');

beforeEach(()=>{
  fetch.mockResolvedValue({ok:true,json:async()=>({ubpkValues:[],numTrips:1,meanUBPK:0.1})});
  document.body.innerHTML=new JSDOM(html).window.document.body.innerHTML;
  document.body.innerHTML+=`<script>const driverId='d1';</script>`;
  const sel=document.getElementById('week-select');
  sel.innerHTML='<option value="2025-W01">2025-W01</option>';
});

test('shows improvement numbers',async()=>{
  fetch
    .mockResolvedValueOnce({ok:true,json:async()=>({ubpkValues:[0.1,0.2]})})
    .mockResolvedValueOnce({ok:true,json:async()=>({pValue:0.05,meanDifference:-0.1})});
  await import('../../app/static/js/driver_analysis.js');
  const text=document.getElementById('p-value').textContent;
  expect(text).toContain('0.05');
});
