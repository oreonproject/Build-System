/* Oreon Build System - Modern JavaScript */

// Initialize when DOM is ready
$(document).ready(function() {
    initializeOreonUI();
    initializeBuildTables();
    initializeSearchFunctionality();
    initializeAnimations();
    initializeTooltips();
    initializeModernFeatures();
});

function initializeOreonUI() {
    // Add smooth scrolling to all links
    $('a[href^="#"]').on('click', function(event) {
        var target = $(this.getAttribute('href'));
        if (target.length) {
            event.preventDefault();
            $('html, body').stop().animate({
                scrollTop: target.offset().top - 70
            }, 1000);
        }
    });

    // Add modern button hover effects
    $('.oreon-btn, .btn').hover(
        function() {
            $(this).addClass('oreon-btn-hover');
        },
        function() {
            $(this).removeClass('oreon-btn-hover');
        }
    );

    // Enhanced panel interactions
    $('.panel-default').hover(
        function() {
            $(this).addClass('panel-hover');
        },
        function() {
            $(this).removeClass('panel-hover');
        }
    );
}

function initializeBuildTables() {
    // Hide build details initially with smooth animation
    $("table.builds-table tr.details").hide();

    // Enhanced build row clicking with smooth animations
    $("table.builds-table tr[class^='build-']").each(function(i, e) {
        $(this).click(function() {
            // Hide all other details with fade out
            $("table.builds-table tr.details").fadeOut(200);
            
            // Show this row's details with fade in after a brief delay
            var detailRow = $(this).next();
            setTimeout(() => {
                detailRow.fadeIn(300);
            }, 250);
            
            // Add visual feedback
            $(this).addClass('build-row-selected');
            setTimeout(() => {
                $(this).removeClass('build-row-selected');
            }, 1000);
        });
        
        // Add hover effects for build rows
        $(this).hover(
            function() {
                $(this).addClass('build-row-hover');
            },
            function() {
                $(this).removeClass('build-row-hover');
            }
        );
    });
}

function initializeSearchFunctionality() {
    // Enhanced search with debouncing
    let searchTimeout;
    
    function search_by_attribute(attribute, form_id) {
        event.preventDefault();
        var value = $("form[id=" + form_id + "]").find("input[name=fulltext]").val();

        // When searching by group but omitting the starting @
        var group = $(event.target).attr("id") == "search-groupname";
        if (group && value[0] != "@") {
            value = "@" + value;
        }

        var url = "/coprs/fulltext/?" + attribute + "=" + encodeURIComponent(value);
        
        // Show loading state
        showSearchLoading();
        
        // Navigate with small delay for UX
        setTimeout(() => {
            window.location.href = url;
        }, 300);
    }
    
    // Live search suggestions (if implemented)
    $('input[name="fulltext"]').on('input', function() {
        clearTimeout(searchTimeout);
        const query = $(this).val();
        
        if (query.length > 2) {
            searchTimeout = setTimeout(() => {
                // Implement live search suggestions here
                showSearchSuggestions(query);
            }, 300);
        } else {
            hideSearchSuggestions();
        }
    });
    
    // Make search_by_attribute globally available
    window.search_by_attribute = search_by_attribute;
}

function initializeAnimations() {
    // Fade in elements on scroll
    $(window).scroll(function() {
        $('.oreon-fade-in').each(function() {
            var elementTop = $(this).offset().top;
            var elementBottom = elementTop + $(this).outerHeight();
            var viewportTop = $(window).scrollTop();
            var viewportBottom = viewportTop + $(window).height();
            
            if (elementBottom > viewportTop && elementTop < viewportBottom) {
                $(this).addClass('fade-in-visible');
            }
        });
    });

    // Build detail menu with modern transitions
    $("div.horizontal-menu li").click(function() {
        $("div.horizontal-menu li.selected")
            .removeClass('selected')
            .addClass('left-for-now');
        
        $(this).addClass('clicked').addClass('selected');
        
        // Remove temporary classes after animation
        setTimeout(() => {
            $("div.horizontal-menu li.left-for-now").removeClass('left-for-now');
            $(this).removeClass('clicked');
        }, 300);
    });

    // Enhanced legal flag interactions
    $("div.legal-flag").hover(
        function() {
            $(this).children(".message").slideDown(200);
        },
        function() {
            $(this).children(".message").slideUp(200);
        }
    );
}

function initializeTooltips() {
    // Initialize Bootstrap tooltips with custom styling
    $('[data-toggle="tooltip"]').tooltip({
        container: 'body',
        html: true,
        template: '<div class="tooltip oreon-tooltip" role="tooltip"><div class="arrow"></div><div class="tooltip-inner"></div></div>'
    });

    // Add tooltips to build status indicators
    $('.build-succeeded').attr('title', 'Build completed successfully');
    $('.build-failed').attr('title', 'Build failed - click for details');
    $('.build-running').attr('title', 'Build in progress');
    $('.build-pending').attr('title', 'Build waiting in queue');
}

function initializeModernFeatures() {
    // Real-time build status updates
    if (window.location.pathname.includes('/build/')) {
        startBuildStatusPolling();
    }
    
    // Progressive loading for large tables
    initializeProgressiveLoading();
    
    // Modern form validation
    initializeFormValidation();
    
    // Keyboard shortcuts
    initializeKeyboardShortcuts();
    
    // Dark mode toggle (if implemented)
    initializeDarkModeToggle();
}

function startBuildStatusPolling() {
    // Poll for build status updates every 10 seconds
    setInterval(() => {
        updateBuildStatus();
    }, 10000);
}

function updateBuildStatus() {
    // Get current build ID from URL or data attribute
    const buildId = getBuildIdFromPage();
    if (!buildId) return;
    
    fetch(`/api/builds/${buildId}/status`)
        .then(response => response.json())
        .then(data => {
            updateBuildStatusUI(data);
        })
        .catch(error => {
            console.log('Build status update failed:', error);
        });
}

function updateBuildStatusUI(statusData) {
    // Update build status indicators with smooth transitions
    $('.build-status').each(function() {
        const newStatus = statusData.status;
        if ($(this).data('status') !== newStatus) {
            $(this).fadeOut(200, () => {
                $(this)
                    .removeClass(function(index, className) {
                        return (className.match(/(^|\s)build-\S+/g) || []).join(' ');
                    })
                    .addClass(`build-${newStatus}`)
                    .data('status', newStatus)
                    .fadeIn(200);
            });
        }
    });
}

function initializeProgressiveLoading() {
    // Load table content progressively for better performance
    $('.builds-table-large').each(function() {
        const table = $(this);
        const rows = table.find('tbody tr');
        
        if (rows.length > 50) {
            // Hide rows beyond the first 50
            rows.slice(50).hide().addClass('progressive-load');
            
            // Add load more button
            table.after('<button class="oreon-btn oreon-btn-secondary load-more-builds">Load More Builds</button>');
        }
    });
    
    // Handle load more clicks
    $(document).on('click', '.load-more-builds', function() {
        const button = $(this);
        const hiddenRows = $('.progressive-load:hidden').slice(0, 25);
        
        button.text('Loading...').prop('disabled', true);
        
        setTimeout(() => {
            hiddenRows.fadeIn(300);
            button.text('Load More Builds').prop('disabled', false);
            
            if ($('.progressive-load:hidden').length === 0) {
                button.fadeOut(300);
            }
        }, 500);
    });
}

function initializeFormValidation() {
    // Modern form validation with real-time feedback
    $('form').each(function() {
        const form = $(this);
        
        form.find('input[required], textarea[required], select[required]').on('blur input', function() {
            validateField($(this));
        });
        
        form.on('submit', function(e) {
            let isValid = true;
            
            form.find('input[required], textarea[required], select[required]').each(function() {
                if (!validateField($(this))) {
                    isValid = false;
                }
            });
            
            if (!isValid) {
                e.preventDefault();
                showFormValidationError();
            }
        });
    });
}

function validateField(field) {
    const value = field.val().trim();
    const isValid = value.length > 0;
    
    field.removeClass('field-valid field-invalid');
    field.addClass(isValid ? 'field-valid' : 'field-invalid');
    
    return isValid;
}

function initializeKeyboardShortcuts() {
    $(document).keydown(function(e) {
        // Ctrl/Cmd + K for search
        if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
            e.preventDefault();
            $('input[name="fulltext"]').focus();
        }
        
        // Escape to close modals/dropdowns
        if (e.key === 'Escape') {
            $('.modal').modal('hide');
            $('.dropdown-menu').removeClass('show');
        }
    });
}

function initializeDarkModeToggle() {
    // Check for saved theme preference or default to light mode
    const currentTheme = localStorage.getItem('oreon-theme') || 'light';
    
    if (currentTheme === 'dark') {
        $('body').addClass('dark-mode');
    }
    
    // Theme toggle functionality
    $('.theme-toggle').on('click', function() {
        $('body').toggleClass('dark-mode');
        const theme = $('body').hasClass('dark-mode') ? 'dark' : 'light';
        localStorage.setItem('oreon-theme', theme);
    });
}

// Utility functions
function showSearchLoading() {
    $('.search-container').addClass('searching');
}

function showSearchSuggestions(query) {
    // Implement search suggestions UI
    console.log('Showing suggestions for:', query);
}

function hideSearchSuggestions() {
    $('.search-suggestions').hide();
}

function getBuildIdFromPage() {
    // Extract build ID from URL or data attributes
    const urlMatch = window.location.pathname.match(/\/build\/(\d+)/);
    return urlMatch ? urlMatch[1] : null;
}

function showFormValidationError() {
    // Show a modern notification
    showNotification('Please fill in all required fields', 'error');
}

function showNotification(message, type = 'info') {
    // Create and show a modern notification
    const notification = $(`
        <div class="oreon-notification oreon-notification-${type}">
            <span class="notification-message">${message}</span>
            <button class="notification-close">&times;</button>
        </div>
    `);
    
    $('body').append(notification);
    
    setTimeout(() => {
        notification.addClass('notification-visible');
    }, 10);
    
    // Auto-hide after 5 seconds
    setTimeout(() => {
        hideNotification(notification);
    }, 5000);
    
    // Click to close
    notification.find('.notification-close').on('click', () => {
        hideNotification(notification);
    });
}

function hideNotification(notification) {
    notification.removeClass('notification-visible');
    setTimeout(() => {
        notification.remove();
    }, 300);
}

// Export functions for global use
window.OreonBuildSystem = {
    showNotification,
    updateBuildStatus,
    search_by_attribute: window.search_by_attribute
}; 