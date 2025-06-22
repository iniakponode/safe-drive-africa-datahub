document.addEventListener('DOMContentLoaded',()=>{
  const select=document.getElementById('week-select');
  const loading=document.getElementById('loading');
  const pval=document.getElementById('p-value');
  const ctx=document.getElementById('trend-chart').getContext('2d');
  let chart=null;
  function isoWeeks(){
    const now=new Date();
    const list=[];
    for(let i=0;i<8;i++){
      const d=new Date(now);d.setDate(d.getDate()-i*7);
      list.push(window.isoWeekString?window.isoWeekString(d):(function(d){const dt=new Date(Date.UTC(d.getFullYear(),d.getMonth(),d.getDate()));const day=dt.getUTCDay()||7;dt.setUTCDate(dt.getUTCDate()+4-day);const yearStart=new Date(Date.UTC(dt.getUTCFullYear(),0,1));const week=Math.ceil((((dt-yearStart)/86400000)+1)/7);return `${dt.getUTCFullYear()}-W${String(week).padStart(2,'0')}`;})(d));
    }
    return list;
  }
  function populate(){
    const weeks=isoWeeks();
    select.innerHTML='';
    weeks.forEach(w=>{const o=document.createElement('option');o.value=w;o.textContent=w;select.appendChild(o);});
    select.value=weeks[0];
  }
  function renderChart(vals){
    const labels=vals.map((_,i)=>i+1);
    if(chart) chart.destroy();
    chart=new Chart(ctx,{type:'line',data:{labels,datasets:[{label:'UBPK',data:vals}]},options:{scales:{y:{beginAtZero:true}}}});
  }
  function load(){
    const week=select.value;
    loading.style.display='block';
    fetch(`/metrics/behavior/driver/${driverId}?week=${week}`)
      .then(r=>r.json())
      .then(d=>{
        renderChart(d.ubpkValues||[]);
        fetch(`/metrics/behavior/driver/${driverId}/improvement?week=${week}`)
          .then(r=>r.json())
          .then(im=>{pval.textContent=`${im.pValue.toFixed(3)} / ${im.meanDifference.toFixed(3)}`;})
          .catch(()=>{pval.textContent='';})
          .finally(()=>{loading.style.display='none';});
      })
      .catch(()=>{loading.style.display='none';});
  }
  populate();
  select.addEventListener('change',load);
  load();
});
