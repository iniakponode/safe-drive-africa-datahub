function getLastNWeeks(n) {
  const weeks = [];
  const today = new Date();
  for (let i = 0; i < n; i++) {
    const dt = new Date(today);
    dt.setDate(dt.getDate() - 7 * i);
    const [year, week] = dt.toISOString().split('T')[0]
      .split('-')
      .map((v, idx) => idx === 1 ? String(Math.ceil((+v - 1 + ((new Date(dt.getFullYear(), 0, 1).getDay() + 6) % 7)) / 7)).padStart(2, '0') : v);
    weeks.push(`${year}-W${week}`);
  }
  return weeks;
}

document.addEventListener('DOMContentLoaded', () => {
  const selector = document.getElementById('week-selector');
  const tableBody = document.querySelector('#trip-table-body');
  if (!selector || !tableBody) return;
  getLastNWeeks(8).forEach(wk => {
    const opt = document.createElement('option');
    opt.value = wk; opt.textContent = wk;
    selector.appendChild(opt);
  });
  selector.value = getLastNWeeks(1)[0];
  loadTrips(selector.value);
  selector.addEventListener('change', () => loadTrips(selector.value));
});

async function loadTrips(week) {
  const tableBody = document.querySelector('#trip-table-body');
  tableBody.innerHTML = '<tr><td colspan="6">Loading…</td></tr>';
  try {
    const res = await fetch(`/metrics/behavior/trips?week=${week}`);
    if (!res.ok) throw new Error('No data');
    const trips = await res.json();
    if (trips.length === 0) {
      tableBody.innerHTML = '<tr><td colspan="6">No data for this week</td></tr>';
      return;
    }
    tableBody.innerHTML = '';
    trips.forEach(trip => {
      const tr = document.createElement('tr');
      tr.innerHTML = `
        <td><a href="/analysis/trip/${trip.tripId}">${trip.tripId}</a></td>
        <td><a href="/analysis/driver/${trip.driverProfileId}">${trip.driverProfileId}</a></td>
        <td>${trip.week}</td>
        <td>${trip.totalUnsafeCount}</td>
        <td>${trip.distanceKm.toFixed(2)}</td>
        <td>${trip.ubpk.toFixed(3)}</td>
      `;
      tableBody.appendChild(tr);
    });
  } catch (e) {
    tableBody.innerHTML = '<tr><td colspan="6">No data for this week</td></tr>';
  }
}
