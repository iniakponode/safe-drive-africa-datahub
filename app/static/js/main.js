function initWeekSelector(){
  const select = document.getElementById('week-selector');
  if (!select) return;
  const now = new Date();
  function isoWeekString(d){
    const dt = new Date(Date.UTC(d.getFullYear(), d.getMonth(), d.getDate()));
    const dayNum = dt.getUTCDay() || 7;
    dt.setUTCDate(dt.getUTCDate() + 4 - dayNum);
    const yearStart = new Date(Date.UTC(dt.getUTCFullYear(),0,1));
    const weekNo = Math.ceil((((dt - yearStart) / 86400000) + 1)/7);
    return `${dt.getUTCFullYear()}-W${String(weekNo).padStart(2,'0')}`;
  }
  window.isoWeekString = isoWeekString;
  const weeks=[];
  for(let i=0;i<8;i++){
    const d=new Date(now); d.setDate(d.getDate()-i*7);
    weeks.push(isoWeekString(d));
  }
  select.innerHTML=weeks.map(w=>`<option value="${w}">${w}</option>`).join('');
  select.value=isoWeekString(now);
  select.dispatchEvent(new Event('change'));
}

if (document.readyState !== 'loading') {
  initWeekSelector();
} else {
  document.addEventListener('DOMContentLoaded', initWeekSelector);
}
