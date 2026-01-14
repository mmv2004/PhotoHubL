document.addEventListener('DOMContentLoaded', function() {
    const searchInput = document.getElementById('client-search');
    const table = document.getElementById('clients-table');
    const rows = table.querySelectorAll('tbody tr');

    searchInput.addEventListener('keyup', function() {
        const searchText = searchInput.value.toLowerCase();

        rows.forEach(row => {
            const rowText = row.textContent.toLowerCase();
            row.style.display = rowText.includes(searchText) ? '' : 'none';
        });
    });
});
