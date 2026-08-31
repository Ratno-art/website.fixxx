// script.js
$(document).ready(function() {
    // Auto refresh setiap 10 detik
    setInterval(function() {
        location.reload();
    }, 10000);
    
    // Efek hover untuk card
    $('.card').hover(
        function() {
            $(this).css('transform', 'translateY(-5px)');
        },
        function() {
            $(this).css('transform', 'translateY(0)');
        }
    );
    
    // Sorting tabel secara client-side (opsional)
    $('th').click(function() {
        var table = $(this).parents('table').eq(0);
        var index = $(this).index();
        var rows = table.find('tbody tr').toArray().sort(comparator(index));
        this.asc = !this.asc;
        if (!this.asc) {
            rows = rows.reverse();
        }
        for (var i = 0; i < rows.length; i++) {
            table.append(rows[i]);
        }
    });
    
    function comparator(index) {
        return function(a, b) {
            var valA = getCellValue(a, index);
            var valB = getCellValue(b, index);
            return $.isNumeric(valA) && $.isNumeric(valB) ? valA - valB : valA.localeCompare(valB);
        };
    }
    
    function getCellValue(row, index) {
        return $(row).children('td').eq(index).text();
    }
});