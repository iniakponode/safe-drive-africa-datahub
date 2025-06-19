function hideLoadingOverlay() {
    const overlay = document.getElementById('loading-overlay');
    if (overlay) {
        overlay.classList.add('hidden');
    }
}
// Fallback in case DOM events fail
setTimeout(hideLoadingOverlay, 5000);
// store paginators globally so that tables updated dynamically can refresh
window.tablePaginators = window.tablePaginators || {};
function setupTablePagination(config) {
    const table = document.getElementById(config.tableId);
    const searchInput = document.getElementById(config.searchInputId);
    const prevBtn = document.getElementById(config.prevBtnId);
    const nextBtn = document.getElementById(config.nextBtnId);
    const pageInfo = document.getElementById(config.pageInfoId);
    const pageNumbers = document.getElementById(config.pageNumbersId);
    if (!table || !searchInput || !prevBtn || !nextBtn || !pageInfo) {
        return null;
    }

    let rows = Array.from(table.querySelectorAll('tbody tr'));
    let filteredRows = rows.slice();
    let currentPage = 1;
    const rowsPerPage = config.rowsPerPage || 10;

    function render() {
        const totalPages = Math.max(1, Math.ceil(filteredRows.length / rowsPerPage));
        currentPage = Math.min(currentPage, totalPages);
        const start = (currentPage - 1) * rowsPerPage;
        const end = start + rowsPerPage;
        rows.forEach(row => row.style.display = 'none');
        filteredRows.slice(start, end).forEach(row => row.style.display = '');
        pageInfo.textContent = `Page ${currentPage} of ${totalPages}`;
        prevBtn.disabled = currentPage === 1;
        nextBtn.disabled = currentPage === totalPages;
        if (pageNumbers) {
            pageNumbers.innerHTML = '';
            for (let i = 1; i <= totalPages; i++) {
                const li = document.createElement('li');
                li.className = 'page-item' + (i === currentPage ? ' active' : '');
                const a = document.createElement('a');
                a.className = 'page-link';
                a.href = '#';
                a.textContent = i;
                a.addEventListener('click', (e) => {
                    e.preventDefault();
                    currentPage = i;
                    render();
                });
                li.appendChild(a);
                pageNumbers.appendChild(li);
            }
        }
    }

    function filterRows() {
        const q = searchInput.value.toLowerCase();
        filteredRows = rows.filter(r => r.textContent.toLowerCase().includes(q));
        currentPage = 1;
        render();
    }

    searchInput.addEventListener('input', filterRows);
    prevBtn.addEventListener('click', () => { if (currentPage > 1) { currentPage--; render(); }});
    nextBtn.addEventListener('click', () => { const totalPages = Math.ceil(filteredRows.length / rowsPerPage); if (currentPage < totalPages) { currentPage++; render(); }});
    function refresh() {
        rows = Array.from(table.querySelectorAll('tbody tr'));
        filterRows();
    }

    render();
    return { refresh };
}

document.addEventListener('DOMContentLoaded', function() {
    hideLoadingOverlay();
    window.tablePaginators.trip = setupTablePagination({
        tableId: 'trip-table',
        searchInputId: 'trip-search',
        prevBtnId: 'trip-prev',
        nextBtnId: 'trip-next',
        pageInfoId: 'trip-page-info',
        pageNumbersId: 'trip-pages',
        rowsPerPage: 10
    });
    window.tablePaginators.driver = setupTablePagination({
        tableId: 'driver-stats-table',
        searchInputId: 'driver-search',
        prevBtnId: 'driver-prev',
        nextBtnId: 'driver-next',
        pageInfoId: 'driver-page-info',
        pageNumbersId: 'driver-pages',
        rowsPerPage: 10
    });
});

// hide overlay if page already loaded
if (document.readyState === 'complete' || document.readyState === 'interactive') {
    hideLoadingOverlay();
}
window.addEventListener('load', hideLoadingOverlay);
