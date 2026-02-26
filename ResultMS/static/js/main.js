

$(function () {

  function updateClock() {
    const now  = new Date();
    const opts = {
      weekday: 'short', month: 'short', day: 'numeric',
      hour: '2-digit', minute: '2-digit'
    };
    $('#liveClock').text(now.toLocaleDateString('en-IN', opts));
  }
  updateClock();
  setInterval(updateClock, 30000);


  $('#menuToggle').on('click', function () {
    $('#sidebar').toggleClass('open');
    $('body').toggleClass('sidebar-open');
  });

  // Overlay click closes sidebar on mobile
  $(document).on('click', function (e) {
    if ($(window).width() <= 768) {
      if (!$(e.target).closest('#sidebar, #menuToggle').length) {
        $('#sidebar').removeClass('open');
        $('body').removeClass('sidebar-open');
      }
    }
  });

  // Sidebar link active state feedback
  $('.nav-item').on('click', function () {
    $(this).addClass('nav-item--clicking');
    setTimeout(() => $(this).removeClass('nav-item--clicking'), 300);
  });


  /* ══════════════════════════════════════
     3. AUTO-DISMISS FLASH MESSAGES
  ══════════════════════════════════════ */
  $('.flash').each(function (i) {
    const $flash = $(this);
    setTimeout(function () {
      $flash.css({ transition: 'all 0.5s ease', opacity: '0', transform: 'translateY(-8px)' });
      setTimeout(() => $flash.slideUp(200, () => $flash.remove()), 500);
    }, 4000 + i * 300);
  });

  $(document).on('click', '.flash-close', function () {
    $(this).closest('.flash').css({ opacity: '0', transform: 'translateX(20px)', transition: 'all 0.3s ease' });
    setTimeout(() => $(this).closest('.flash').slideUp(200, function () { $(this).remove(); }), 300);
  });


  /* ══════════════════════════════════════
     4. ANIMATED STAT COUNTERS
  ══════════════════════════════════════ */
  function animateCounter($el) {
    const target = parseInt($el.text()) || 0;
    if (target === 0) return;
    $el.text('0');
    $({ count: 0 }).animate({ count: target }, {
      duration: 1000,
      easing: 'swing',
      step: function () {
        $el.text(Math.floor(this.count));
      },
      complete: function () {
        $el.text(target);
      }
    });
  }

  // Trigger counter when stat cards come into view
  const counterObserver = new IntersectionObserver(function (entries) {
    entries.forEach(function (entry) {
      if (entry.isIntersecting) {
        animateCounter($(entry.target).find('.stat-value'));
        counterObserver.unobserve(entry.target);
      }
    });
  }, { threshold: 0.3 });

  $('.stat-card').each(function () {
    counterObserver.observe(this);
  });


  /* ══════════════════════════════════════
     5. DISTRIBUTION BAR ANIMATION
  ══════════════════════════════════════ */
  const barObserver = new IntersectionObserver(function (entries) {
    entries.forEach(function (entry) {
      if (entry.isIntersecting) {
        $(entry.target).find('.dist-bar').each(function () {
          const $bar   = $(this);
          const target = $bar.data('width') || $bar.attr('style').match(/width:\s*([\d.]+)%/)?.[1] || 0;
          $bar.css('width', '0').animate({ width: target + '%' }, { duration: 1000, easing: 'swing' });
        });
        barObserver.unobserve(entry.target);
      }
    });
  }, { threshold: 0.2 });

  $('.class-dist').each(function () {
    // Store original widths and reset
    $(this).find('.dist-bar').each(function () {
      const w = $(this).css('width');
      $(this).data('width', parseFloat(w)).css('width', '0');
    });
    barObserver.observe(this);
  });


  /* ══════════════════════════════════════
     6. CARD ENTRANCE ANIMATIONS
  ══════════════════════════════════════ */
  const cardObserver = new IntersectionObserver(function (entries) {
    entries.forEach(function (entry, i) {
      if (entry.isIntersecting) {
        const $el = $(entry.target);
        setTimeout(function () {
          $el.css({ opacity: '1', transform: 'translateY(0)' });
        }, i * 60);
        cardObserver.unobserve(entry.target);
      }
    });
  }, { threshold: 0.1 });

  $('.student-result-card, .stat-card, .card').each(function () {
    $(this).css({ opacity: '0', transform: 'translateY(16px)', transition: 'opacity 0.4s ease, transform 0.4s ease' });
    cardObserver.observe(this);
  });


  /* ══════════════════════════════════════
     7. TABLE ROW HOVER ENHANCEMENT
  ══════════════════════════════════════ */
  $(document).on('mouseenter', '.table tbody tr', function () {
    $(this).find('td:first-child').css('border-left', '3px solid #6366F1');
  }).on('mouseleave', '.table tbody tr', function () {
    $(this).find('td:first-child').css('border-left', '');
  });


  /* ══════════════════════════════════════
     8. BUTTON LOADING STATE
  ══════════════════════════════════════ */
  $(document).on('click', 'button[type=submit].btn-success, button[type=submit].btn-primary', function () {
    const $btn = $(this);
    const orig = $btn.html();
    $btn.data('original', orig);

    setTimeout(function () {
      if ($btn.closest('form').find('.marks-input.invalid').length === 0) {
        $btn.html('<span class="btn-spinner"></span> Saving…').prop('disabled', true).addClass('loading');
      }
    }, 50);

    // Re-enable after 8s as safety net
    setTimeout(function () {
      $btn.html(orig).prop('disabled', false).removeClass('loading');
    }, 8000);
  });


  /* ══════════════════════════════════════
     9. FORM FIELD FOCUS EFFECTS
  ══════════════════════════════════════ */
  $(document).on('focus', '.form-input, .marks-input', function () {
    $(this).closest('.form-group').addClass('form-group--focused');
  }).on('blur', '.form-input, .marks-input', function () {
    $(this).closest('.form-group').removeClass('form-group--focused');
  });


  /* ══════════════════════════════════════
     10. CONFIRMATION DIALOGS (ENHANCED)
  ══════════════════════════════════════ */
  $(document).on('submit', 'form[data-confirm]', function (e) {
    const msg = $(this).data('confirm') || 'Are you sure?';
    if (!confirm(msg)) {
      e.preventDefault();
    }
  });


  /* ══════════════════════════════════════
     11. SEARCH INPUT CLEAR BUTTON
  ══════════════════════════════════════ */
  $('.search-input').each(function () {
    const $input = $(this);
    if ($input.val().length > 0) {
      addClearBtn($input);
    }
    $input.on('input', function () {
      if ($(this).val().length > 0) {
        addClearBtn($(this));
      } else {
        $(this).siblings('.search-clear').remove();
      }
    });
  });

  function addClearBtn($input) {
    if ($input.siblings('.search-clear').length) return;
    const $clear = $('<button type="button" class="search-clear" title="Clear">✕</button>').css({
      position: 'absolute',
      right: '10px',
      top: '50%',
      transform: 'translateY(-50%)',
      background: 'none',
      border: 'none',
      color: '#94A3B8',
      cursor: 'pointer',
      fontSize: '12px',
      padding: '2px 4px',
      lineHeight: '1'
    });
    $input.wrap('<div style="position:relative;flex:1;min-width:240px"></div>');
    $input.css('padding-right', '30px').after($clear);
    $clear.on('click', function () {
      $input.val('').trigger('input').focus();
      $(this).remove();
    });
  }


  /* ══════════════════════════════════════
     12. TOOLTIP INIT (Bootstrap)
  ══════════════════════════════════════ */
  if (typeof bootstrap !== 'undefined') {
    const tooltipEls = document.querySelectorAll('[data-bs-toggle="tooltip"]');
    tooltipEls.forEach(el => new bootstrap.Tooltip(el, { trigger: 'hover' }));
  }


  /* ══════════════════════════════════════
     13. GRADE PILL HOVER POPOVER
  ══════════════════════════════════════ */
  const gradeDesc = {
    'A+': '90–100% · Outstanding',
    'A':  '80–89% · Excellent',
    'B+': '70–79% · Very Good',
    'B':  '60–69% · Good',
    'C+': '50–59% · Above Average',
    'C':  '40–49% · Average',
    'D':  '33–39% · Pass',
    'F':  'Below 33% · Fail'
  };

  $(document).on('mouseenter', '.grade-pill', function () {
    const grade = $(this).text().trim();
    const desc  = gradeDesc[grade];
    if (!desc) return;

    const $tip = $('<div class="grade-tooltip">' + desc + '</div>').css({
      position: 'absolute',
      background: '#1E293B',
      color: 'white',
      fontSize: '11px',
      fontWeight: '500',
      padding: '5px 10px',
      borderRadius: '6px',
      whiteSpace: 'nowrap',
      zIndex: 9999,
      pointerEvents: 'none',
      boxShadow: '0 4px 12px rgba(0,0,0,0.2)'
    });

    $('body').append($tip);
    const pos = $(this).offset();
    $tip.css({ top: pos.top - $tip.outerHeight() - 6, left: pos.left });
    $(this).data('tooltip-el', $tip);
  }).on('mouseleave', '.grade-pill', function () {
    const $tip = $(this).data('tooltip-el');
    if ($tip) $tip.remove();
  });


  /* ══════════════════════════════════════
     14. PRINT DATE
  ══════════════════════════════════════ */
  const $printDate = $('#printDate');
  if ($printDate.length) {
    $printDate.text(new Date().toLocaleDateString('en-IN', {
      year: 'numeric', month: 'long', day: 'numeric'
    }));
  }


  /* ══════════════════════════════════════
     15. SCROLL TO FLASH
  ══════════════════════════════════════ */
  if ($('.flash-wrap .flash').length) {
    $('html, body').animate({
      scrollTop: $('.flash-wrap').offset().top - 80
    }, 400);
  }


  /* ══════════════════════════════════════
     16. TOPBAR SHADOW ON SCROLL
  ══════════════════════════════════════ */
  $(window).on('scroll', function () {
    if ($(this).scrollTop() > 10) {
      $('.topbar').css('box-shadow', '0 4px 20px rgba(0,0,0,0.1)');
    } else {
      $('.topbar').css('box-shadow', '0 1px 0 rgba(0,0,0,0.05), 0 4px 16px rgba(0,0,0,0.04)');
    }
  });


  /* ══════════════════════════════════════
     17. TABLE SORT INDICATOR
  ══════════════════════════════════════ */
  $('.table th[data-sort]').css('cursor', 'pointer').on('click', function () {
    const col = $(this).data('sort');
    const $table = $(this).closest('table');
    const $tbody = $table.find('tbody');
    const rows   = $tbody.find('tr').toArray();
    const asc    = $(this).data('asc') !== true;

    rows.sort(function (a, b) {
      const aVal = $(a).find('td').eq(col).text().trim();
      const bVal = $(b).find('td').eq(col).text().trim();
      const aNum = parseFloat(aVal);
      const bNum = parseFloat(bVal);

      if (!isNaN(aNum) && !isNaN(bNum)) {
        return asc ? aNum - bNum : bNum - aNum;
      }
      return asc ? aVal.localeCompare(bVal) : bVal.localeCompare(aVal);
    });

    $table.find('th').removeData('asc').find('.sort-icon').remove();
    $(this).data('asc', asc).append('<span class="sort-icon">' + (asc ? ' ▲' : ' ▼') + '</span>');
    $tbody.append(rows);
  });


  /* ══════════════════════════════════════
     18. SMOOTH PAGE TRANSITIONS
  ══════════════════════════════════════ */
  $('a.nav-item').on('click', function (e) {
    const href = $(this).attr('href');
    if (!href || href === '#' || href.startsWith('javascript')) return;

    e.preventDefault();
    $('body').css({ opacity: '1', transition: 'opacity 0.2s ease' })
             .animate({ opacity: 0 }, 200, function () {
               window.location.href = href;
             });
  });

  // Fade in on load
  $('body').css('opacity', '0').animate({ opacity: 1 }, 300);


  /* ══════════════════════════════════════
     19. INPUT RIPPLE EFFECT
  ══════════════════════════════════════ */
  $(document).on('focus', '.marks-input', function () {
    $(this).closest('tr').css({
      background: 'linear-gradient(90deg, #F0F4FF, #FAFCFF)',
      transition: 'background 0.3s ease'
    });
  }).on('blur', '.marks-input', function () {
    $(this).closest('tr').css('background', '');
  });


  /* ══════════════════════════════════════
     20. KEYBOARD SHORTCUT — Ctrl+Enter to submit
  ══════════════════════════════════════ */
  $(document).on('keydown', function (e) {
    if ((e.ctrlKey || e.metaKey) && e.key === 'Enter') {
      const $form = $('form#resultForm');
      if ($form.length) {
        $form.submit();
      }
    }
  });


  /* ══════════════════════════════════════
     21. SIDEBAR ACTIVE LINK HIGHLIGHT
  ══════════════════════════════════════ */
  const currentPath = window.location.pathname;
  $('.nav-item').each(function () {
    const href = $(this).attr('href');
    if (href && href !== '/' && currentPath.startsWith(href)) {
      $(this).addClass('active');
    } else if (href === '/' && currentPath === '/') {
      $(this).addClass('active');
    }
  });


  /* ══════════════════════════════════════
     22. MARK TABLE PROGRESS BARS
  ══════════════════════════════════════ */
  $('.ms-table tbody tr').each(function () {
    const $cells = $(this).find('td');
    if ($cells.length >= 5) {
      const pctText = $cells.eq(4).text().trim();
      const pct     = parseFloat(pctText);
      if (!isNaN(pct)) {
        const color = pct >= 80 ? '#059669' : pct >= 60 ? '#3B82F6' : pct >= 33 ? '#F59E0B' : '#EF4444';
        $cells.eq(4).html(
          '<div style="display:flex;align-items:center;gap:8px">' +
          '<div style="flex:1;background:#F1F5F9;border-radius:99px;height:6px;overflow:hidden">' +
          '<div style="width:0;height:100%;background:' + color + ';border-radius:99px;transition:width 1s ease" data-w="' + pct + '"></div>' +
          '</div>' +
          '<span style="font-size:12px;font-weight:600;min-width:38px;text-align:right">' + pctText + '</span>' +
          '</div>'
        );
      }
    }
  });

  // Animate those bars
  setTimeout(function () {
    $('[data-w]').each(function () {
      $(this).css('width', $(this).data('w') + '%');
    });
  }, 400);


  /* ══════════════════════════════════════
     23. BACK TO TOP BUTTON
  ══════════════════════════════════════ */
  const $backTop = $('<button id="backToTop" title="Back to top">↑</button>').css({
    position: 'fixed',
    bottom: '28px',
    right: '28px',
    width: '40px',
    height: '40px',
    background: 'linear-gradient(135deg, #4F46E5, #7C3AED)',
    color: 'white',
    border: 'none',
    borderRadius: '50%',
    fontSize: '18px',
    fontWeight: '700',
    cursor: 'pointer',
    boxShadow: '0 4px 16px rgba(79,70,229,0.4)',
    opacity: '0',
    transform: 'scale(0)',
    transition: 'all 0.3s cubic-bezier(0.34,1.56,0.64,1)',
    zIndex: '500',
    lineHeight: '40px',
    textAlign: 'center'
  });

  $('body').append($backTop);

  $(window).on('scroll', function () {
    if ($(this).scrollTop() > 300) {
      $backTop.css({ opacity: '1', transform: 'scale(1)' });
    } else {
      $backTop.css({ opacity: '0', transform: 'scale(0)' });
    }
  });

  $backTop.on('click', function () {
    $('html, body').animate({ scrollTop: 0 }, 500, 'swing');
  });


  /* ══════════════════════════════════════
     24. RESULTS SECTION — EXPAND/COLLAPSE
  ══════════════════════════════════════ */
  $(document).on('click', '.src-header', function (e) {
    // Only collapse if not clicking buttons/links inside header
    if ($(e.target).closest('.btn, a, button').length) return;

    const $card    = $(this).closest('.student-result-card');
    const $body    = $card.find('.table-wrap');
    const $toggle  = $card.find('.src-collapse-icon');

    if ($body.is(':visible')) {
      $body.slideUp(250);
      $toggle.text('▼');
      $card.css('opacity', '0.75');
    } else {
      $body.slideDown(250);
      $toggle.text('▲');
      $card.css('opacity', '1');
    }
  });

  // Add collapse icon to each src-header
  $('.src-header').append('<span class="src-collapse-icon" style="margin-left:auto;color:#94A3B8;font-size:12px;cursor:pointer">▲</span>');


  /* ══════════════════════════════════════
     25. BADGE ANIMATION ON HOVER
  ══════════════════════════════════════ */
  $(document).on('mouseenter', '.badge', function () {
    $(this).css({ transform: 'scale(1.08)', transition: 'transform 0.15s ease' });
  }).on('mouseleave', '.badge', function () {
    $(this).css('transform', '');
  });

});
/* End of ResultMS premium JS */
/* ══════════════════════════════════════
   FIX — Mobile sidebar with overlay
══════════════════════════════════════ */
$(function () {
  // Add overlay div to body if not present
  if (!$('#sidebarOverlay').length) {
    $('body').append('<div id="sidebarOverlay" class="sidebar-overlay"></div>');
  }

  $('#menuToggle').off('click').on('click', function () {
    $('#sidebar').toggleClass('open');
    $('#sidebarOverlay').toggleClass('active');
  });

  $('#sidebarOverlay').on('click', function () {
    $('#sidebar').removeClass('open');
    $('#sidebarOverlay').removeClass('active');
  });
});