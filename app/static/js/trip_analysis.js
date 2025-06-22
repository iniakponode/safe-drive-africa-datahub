document.addEventListener('DOMContentLoaded',()=>{
  const tableBody=document.querySelector('#trip-summary tbody');
  const loading=document.getElementById('trip-loading');
  const error=document.getElementById('trip-error');
  if(!tableBody) return;
  loading.style.display='block';
  fetch(`/metrics/behavior/trip/${tripId}/ubpk`)
    .then(r=>r.ok?r.json():null)
    .then(data=>{
      loading.style.display='none';
      if(!data){error.style.display='block';return;}
      const rows=[
        ['Week',data.week],
        ['Week Start',data.weekStart],
        ['Week End',data.weekEnd],
        ['Total Unsafe Count',data.totalUnsafeCount],
        ['Distance (km)',data.distanceKm],
        ['UBPK',data.ubpk]
      ];
      rows.forEach(([k,v])=>{
        const tr=document.createElement('tr');
        tr.innerHTML=`<th>${k}</th><td>${v}</td>`;
        tableBody.appendChild(tr);
      });
    })
    .catch(()=>{loading.style.display='none'; error.style.display='block';});
});
