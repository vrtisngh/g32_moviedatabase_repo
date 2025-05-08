// Movie Fusion main JavaScript functionality

// Function to handle star rating hover effects in the review form
function initStarRating() {
    const ratingInput = document.getElementById('id_rating');
    const starContainer = document.querySelector('.star-rating-selector');
    
    if (ratingInput && starContainer) {
        const stars = starContainer.querySelectorAll('.star');
        
        // Set initial stars based on input value
        if (ratingInput.value) {
            setStars(parseInt(ratingInput.value));
        }
        
        // Add event listeners to stars
        stars.forEach(star => {
            star.addEventListener('click', function() {
                const value = this.dataset.value;
                ratingInput.value = value;
                setStars(value);
            });
            
            star.addEventListener('mouseenter', function() {
                const value = this.dataset.value;
                highlightStars(value);
            });
        });
        
        // Reset stars when leaving the container
        starContainer.addEventListener('mouseleave', function() {
            if (ratingInput.value) {
                setStars(parseInt(ratingInput.value));
            } else {
                resetStars();
            }
        });
        
        function setStars(value) {
            stars.forEach(star => {
                if (parseInt(star.dataset.value) <= value) {
                    star.classList.add('active');
                    star.innerHTML = '<i class="fas fa-star"></i>';
                } else {
                    star.classList.remove('active');
                    star.innerHTML = '<i class="far fa-star"></i>';
                }
            });
        }
        
        function highlightStars(value) {
            stars.forEach(star => {
                if (parseInt(star.dataset.value) <= value) {
                    star.innerHTML = '<i class="fas fa-star"></i>';
                } else {
                    star.innerHTML = '<i class="far fa-star"></i>';
                }
            });
        }
        
        function resetStars() {
            stars.forEach(star => {
                star.classList.remove('active');
                star.innerHTML = '<i class="far fa-star"></i>';
            });
        }
    }
}

// Enhance forms with Bootstrap classes
function enhanceFormsWithBootstrap() {
    const formInputs = document.querySelectorAll('input:not([type="hidden"]), select, textarea');
    formInputs.forEach(input => {
        if (!input.classList.contains('form-control') && input.type !== 'file' && input.type !== 'checkbox') {
            input.classList.add('form-control');
        }
        if (input.type === 'file') {
            input.classList.add('form-control');
        }
        if (input.type === 'checkbox') {
            input.classList.add('form-check-input');
            // Wrap checkbox in a div with the appropriate class
            const parent = input.parentNode;
            if (parent.tagName.toLowerCase() !== 'div' || !parent.classList.contains('form-check')) {
                const wrapper = document.createElement('div');
                wrapper.classList.add('form-check');
                parent.insertBefore(wrapper, input);
                wrapper.appendChild(input);
            }
        }
    });
}

// Initialize tooltips
function initTooltips() {
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
}

// Initialize popovers
function initPopovers() {
    const popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
    popoverTriggerList.map(function (popoverTriggerEl) {
        return new bootstrap.Popover(popoverTriggerEl);
    });
}

// Initialize the dashboard charts if present
function initDashboardCharts() {
    const genreChartCanvas = document.getElementById('genreChart');
    const ratingChartCanvas = document.getElementById('ratingChart');
    
    if (genreChartCanvas) {
        // Implementation using Chart.js would go here
        console.log('Genre chart initialized');
    }
    
    if (ratingChartCanvas) {
        // Implementation using Chart.js would go here
        console.log('Rating chart initialized');
    }
}

// Run all initialization functions when the DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    enhanceFormsWithBootstrap();
    initStarRating();
    initTooltips();
    initPopovers();
    initDashboardCharts();
    
    // Fade out alerts after 5 seconds
    const alerts = document.querySelectorAll('.alert:not(.alert-permanent)');
    alerts.forEach(alert => {
        setTimeout(() => {
            alert.classList.add('fade');
            setTimeout(() => {
                alert.remove();
            }, 500);
        }, 5000);
    });
});
