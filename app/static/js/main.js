function hideLoadingOverlay() {
    const overlay = document.getElementById('loading-overlay');
    if (overlay) {
        overlay.classList.add('hidden');
    }
}

function setupTablePagination(config) {
    const table = document.getElementById(config.tableId);
    const searchInput = document.getElementById(config.searchInputId);
    const prevBtn = document.getElementById(config.prevBtnId);
    const nextBtn = document.getElementById(config.nextBtnId);
    const pageInfo = document.getElementById(config.pageInfoId);
    if (!table || !searchInput || !prevBtn || !nextBtn || !pageInfo) {
        return;
    }

    const rows = Array.from(table.querySelectorAll('tbody tr'));
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

    render();
}

document.addEventListener('DOMContentLoaded', function() {
    hideLoadingOverlay();
    setupTablePagination({
        tableId: 'trip-table',
        searchInputId: 'trip-search',
        prevBtnId: 'trip-prev',
        nextBtnId: 'trip-next',
        pageInfoId: 'trip-page-info',
        rowsPerPage: 10
    });
    setupTablePagination({
        tableId: 'driver-stats-table',
        searchInputId: 'driver-search',
        prevBtnId: 'driver-prev',
        nextBtnId: 'driver-next',
        pageInfoId: 'driver-page-info',
        rowsPerPage: 10
    });
});
