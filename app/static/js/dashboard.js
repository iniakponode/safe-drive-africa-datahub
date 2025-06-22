(document=>{
  document.addEventListener('DOMContentLoaded', ()=>{
    const weekSel=document.getElementById('week-selector');
    const tbody=document.getElementById('trips-tbody');
    if(!weekSel||!tbody) return;
    const load=()=>{
      const week=weekSel.value;
      weekSel.disabled=true;
      tbody.innerHTML='<tr><td colspan="6">Loading...</td></tr>';
      fetch(`/metrics/behavior/trips?week=${week}`)
        .then(r=>r.ok?r.json():[])
        .then(rows=>{
          tbody.innerHTML='';
          if(!rows.length){
            tbody.innerHTML='<tr><td colspan="6">No data for this week</td></tr>';
          }else{
            rows.forEach(row=>{
              const tr=document.createElement('tr');
              tr.innerHTML=`<td><a href="/analysis/trip/${row.tripId}">${row.tripId}</a></td>
                <td><a href="/analysis/driver/${row.driverId}">${row.driverId}</a></td>
                <td>${row.week}</td>
                <td>${row.totalUnsafeCount}</td>
                <td>${row.distanceKm}</td>
                <td>${row.ubpk}</td>`;
              tbody.appendChild(tr);
            });
          }
        })
        .catch(()=>{tbody.innerHTML='<tr><td colspan="6">No data for this week</td></tr>';})
        .finally(()=>{weekSel.disabled=false;});
    };
    weekSel.addEventListener('change',load);
    load();
  });
})(document);
