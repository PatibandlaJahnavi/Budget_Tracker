// ═══════════════════════════════════════════
//   FINANCE TRACKER - MAIN JAVASCRIPT
// ═══════════════════════════════════════════


// ── 1. Auto Hide Alert Messages ──────────────
// Automatically hides success/error messages
// after 3 seconds

document.addEventListener('DOMContentLoaded', function() {
    const alerts = document.querySelectorAll('.alert');
    alerts.forEach(function(alert) {
        setTimeout(function() {
            alert.style.transition = 'opacity 0.5s';
            alert.style.opacity = '0';
            setTimeout(function() {
                alert.remove();
            }, 500);
        }, 3000);
    });
});


// ── 2. Progress Bar Colors ───────────────────
// Changes progress bar color based on percentage
// Green = safe, Orange = warning, Red = over budget

document.addEventListener('DOMContentLoaded', function() {
    const progressBars = document.querySelectorAll('.progress-bar');
    progressBars.forEach(function(bar) {
        const percent = parseInt(bar.getAttribute('data-percent'));

        if (percent >= 100) {
            bar.classList.add('danger');
            bar.style.width = '100%';
        } else if (percent >= 80) {
            bar.classList.add('warning');
            bar.style.width = percent + '%';
        } else {
            bar.classList.add('safe');
            bar.style.width = percent + '%';
        }
    });
});


// ── 3. Confirm Delete ────────────────────────
// Shows confirmation popup before deleting
// anything important

function confirmDelete(message) {
    return confirm(message || 'Are you sure you want to delete?');
}


// ── 4. Set Today's Date Automatically ────────
// Sets today's date as default in date fields

document.addEventListener('DOMContentLoaded', function() {
    const dateInputs = document.querySelectorAll('input[type="date"]');
    const today = new Date().toISOString().split('T')[0];
    dateInputs.forEach(function(input) {
        if (!input.value) {
            input.value = today;
        }
    });
});


// ── 5. Form Validation ───────────────────────
// Checks that amount is greater than 0
// before submitting the form

document.addEventListener('DOMContentLoaded', function() {
    const forms = document.querySelectorAll('form');
    forms.forEach(function(form) {
        form.addEventListener('submit', function(e) {
            const amountInput = form.querySelector(
                'input[name="amount"]'
            );
            if (amountInput) {
                const value = parseFloat(amountInput.value);
                if (isNaN(value) || value <= 0) {
                    e.preventDefault();
                    alert('Please enter a valid amount greater than 0');
                    amountInput.focus();
                }
            }
        });
    });
});


// ── 6. Dashboard Chart ───────────────────────
// Draws pie chart on dashboard if canvas exists
// Uses Chart.js library

document.addEventListener('DOMContentLoaded', function() {
    const ctx = document.getElementById('expenseChart');
    if (ctx) {
        // Get data from HTML data attributes
        const labels = JSON.parse(
            ctx.getAttribute('data-labels') || '[]'
        );
        const data = JSON.parse(
            ctx.getAttribute('data-values') || '[]'
        );

        new Chart(ctx, {
            type: 'pie',
            data: {
                labels: labels,
                datasets: [{
                    data: data,
                    backgroundColor: [
                        '#667eea',
                        '#f093fb',
                        '#11998e',
                        '#f7971e',
                        '#cb2d3e',
                        '#38ef7d',
                        '#764ba2',
                        '#ffd200',
                    ],
                    borderWidth: 2,
                    borderColor: '#fff'
                }]
            },
            options: {
                responsive: true,
                plugins: {
                    legend: {
                        position: 'bottom',
                    },
                    title: {
                        display: true,
                        text: 'Monthly Expenses by Category'
                    }
                }
            }
        });
    }
});


// ── 7. Balance Color ─────────────────────────
// Makes balance text red if negative
// and green if positive

document.addEventListener('DOMContentLoaded', function() {
    const balanceEl = document.getElementById('balance-amount');
    if (balanceEl) {
        const balance = parseFloat(
            balanceEl.textContent.replace('$', '')
        );
        if (balance < 0) {
            balanceEl.style.color = '#dc3545';
        } else {
            balanceEl.style.color = '#28a745';
        }
    }
});


// ── 8. Search Filter Live ────────────────────
// Filters table rows as user types in search box

document.addEventListener('DOMContentLoaded', function() {
    const searchInput = document.getElementById('live-search');
    if (searchInput) {
        searchInput.addEventListener('keyup', function() {
            const value = this.value.toLowerCase();
            const rows = document.querySelectorAll(
                '#results-table tbody tr'
            );
            rows.forEach(function(row) {
                const text = row.textContent.toLowerCase();
                row.style.display = text.includes(value)
                    ? ''
                    : 'none';
            });
        });
    }
});