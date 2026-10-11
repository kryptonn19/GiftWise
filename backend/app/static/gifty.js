/**
 * ==========================================================================
 * GIFTY ASSISTANT - FRIENDLY MASCOT & INTERACTIVE COMPANION WIDGET
 * ==========================================================================
 */

(function () {
  'use strict';

  // Mascot Configuration
  const MASCOT_NAME = 'Gifty';
  const STORAGE_KEY_INTRO_DISMISSED = 'gifty_intro_dismissed_v1';

  /**
   * Generates clean SVG markup for Gifty with dynamic expressions
   * @param {string} expression - 'happy' | 'curious' | 'thinking' | 'celebrating'
   * @param {number} size - viewBox size scaling
   */
  function getGiftySVG(expression = 'happy', size = 100) {
    let eyesSvg = '';
    let mouthSvg = '';
    let extraSvg = '';

    // Expressions logic
    if (expression === 'celebrating') {
      // Arc eyes ^ ^
      eyesSvg = `
        <path d="M 33 36 Q 38 30 43 36" stroke="#253443" stroke-width="3.5" stroke-linecap="round" fill="none" />
        <path d="M 57 36 Q 62 30 67 36" stroke="#253443" stroke-width="3.5" stroke-linecap="round" fill="none" />
      `;
      mouthSvg = `<path d="M 46 54 Q 50 59 54 54" stroke="#588db2" stroke-width="2.5" stroke-linecap="round" fill="none" />`;
      // Sparkles around Gifty
      extraSvg = `
        <path d="M 12 24 L 14 18 L 20 20 L 14 22 Z" fill="#f78d8d" />
        <path d="M 85 22 L 88 16 L 94 19 L 88 21 Z" fill="#d9822b" />
      `;
    } else if (expression === 'thinking') {
      // Eyes looking up-right
      eyesSvg = `
        <circle cx="36" cy="33" r="4.2" fill="#253443" />
        <circle cx="60" cy="33" r="4.2" fill="#253443" />
        <path d="M 33 26 L 41 27" stroke="#588db2" stroke-width="2.5" stroke-linecap="round" />
      `;
      mouthSvg = `<path d="M 47 55 Q 50 52 53 55" stroke="#588db2" stroke-width="2.5" stroke-linecap="round" fill="none" />`;
    } else if (expression === 'curious') {
      // One eye wider, small tilted mouth
      eyesSvg = `
        <circle cx="38" cy="35" r="4.8" fill="#253443" />
        <circle cx="62" cy="35" r="3.8" fill="#253443" />
        <path d="M 58 26 Q 63 24 67 27" stroke="#588db2" stroke-width="2" stroke-linecap="round" fill="none" />
      `;
      mouthSvg = `<path d="M 48 54 Q 52 57 56 53" stroke="#588db2" stroke-width="2.5" stroke-linecap="round" fill="none" />`;
    } else {
      // Happy / Default
      eyesSvg = `
        <circle cx="38" cy="35" r="4.2" fill="#253443" />
        <circle cx="62" cy="35" r="4.2" fill="#253443" />
      `;
      mouthSvg = `<path d="M 46 53 Q 50 57 54 53" stroke="#588db2" stroke-width="2.2" stroke-linecap="round" fill="none" />`;
    }

    return `
      <svg width="${size}" height="${size}" viewBox="0 0 100 100" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="${MASCOT_NAME} Mascot">
        ${extraSvg}
        <!-- Rounded Body & Ears (Reference Image Shape) -->
        <path d="M 22,38 
                 C 20,20 30,11 37,14 
                 C 42,16 45,18 50,18 
                 C 55,18 58,16 63,14 
                 C 70,11 80,20 78,38 
                 C 78,48 90,54 90,66 
                 C 90,82 81,91 66,91 
                 C 50,93 50,93 34,91 
                 C 19,91 10,82 10,66 
                 C 10,54 22,48 22,38 Z" 
              fill="#b3e0f2" 
              stroke="#588db2" 
              stroke-width="4.5" 
              stroke-linejoin="round" 
              stroke-linecap="round" />

        <!-- White Muzzle Oval -->
        <ellipse cx="50" cy="50" rx="17" ry="12.5" fill="#ffffff" />
        
        <!-- Inverted Blue Nose Triangle -->
        <polygon points="45.5,43.5 54.5,43.5 50,49" fill="#588db2" />
        
        <!-- Eyes & Mouth -->
        ${eyesSvg}
        ${mouthSvg}

        <!-- White Feet/Paws (Left & Right Bottom) -->
        <ellipse cx="23" cy="81" rx="12" ry="12" fill="#ffffff" stroke="#588db2" stroke-width="4" />
        <ellipse cx="77" cy="81" rx="12" ry="12" fill="#ffffff" stroke="#588db2" stroke-width="4" />
      </svg>
    `;
  }

  /**
   * Generates inline SVG icons for Gifty action buttons
   */
  function getSVGIcon(name) {
    const icons = {
      sparkles: `<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" style="margin-right:6px; display:inline-block; vertical-align:-2px;"><path d="m12 3-1.9 5.8a2 2 0 0 1-1.3 1.3L3 12l5.8 1.9a2 2 0 0 1 1.3 1.3L12 21l1.9-5.8a2 2 0 0 1 1.3-1.3L21 12l-5.8-1.9a2 2 0 0 1-1.3-1.3Z"/><path d="M5 3v4"/><path d="M19 17v4"/></svg>`,
      gift: `<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" style="margin-right:6px; display:inline-block; vertical-align:-2px;"><path d="M20 12v10H4V12"/><path d="M2 7h20v5H2z"/><path d="M12 22V7"/><path d="M12 7H7.5a2.5 2.5 0 0 1 0-5C11 2 12 7 12 7z"/><path d="M12 7h4.5a2.5 2.5 0 0 0 0-5C13 2 12 7 12 7z"/></svg>`,
      chart: `<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" style="margin-right:6px; display:inline-block; vertical-align:-2px;"><path d="M3 3v18h18"/><path d="M18 17V9"/><path d="M13 17V5"/><path d="M8 17v-3"/></svg>`,
      edit: `<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" style="margin-right:6px; display:inline-block; vertical-align:-2px;"><path d="M12 20h9"/><path d="M16.5 3.5a2.121 2.121 0 0 1 3 3L7 19l-4 1 1-4L16.5 3.5z"/></svg>`,
      search: `<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" style="margin-right:6px; display:inline-block; vertical-align:-2px;"><circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/></svg>`,
      heart: `<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" style="margin-right:6px; display:inline-block; vertical-align:-2px;"><path d="M20.84 4.61a5.5 5.5 0 0 0-7.78 0L12 5.67l-1.06-1.06a5.5 5.5 0 0 0-7.78 7.78l1.06 1.06L12 21.23l7.78-7.78 1.06-1.06a5.5 5.5 0 0 0 0-7.78z"/></svg>`
    };
    return icons[name] || '';
  }

  // Assistant Component Class
  class GiftyAssistant {
    constructor() {
      this.isOpen = false;
      this.currentTab = 'welcome';
      this.initUI();
      this.bindEvents();
      this.checkFirstVisit();
    }

    initUI() {
      // Root widget container
      this.container = document.createElement('div');
      this.container.id = 'gifty-widget-container';

      // Launcher Button
      this.launcher = document.createElement('button');
      this.launcher.className = 'gifty-launcher idle-anim';
      this.launcher.setAttribute('aria-label', `Open ${MASCOT_NAME} Assistant`);
      this.launcher.setAttribute('aria-expanded', 'false');
      this.launcher.innerHTML = `
        <div class="gifty-launcher-svg">${getGiftySVG('happy', 46)}</div>
        <div class="gifty-notification-dot" id="gifty-notif-dot" style="display:none;"></div>
      `;

      // Intro Bubble
      this.introBubble = document.createElement('div');
      this.introBubble.className = 'gifty-intro-bubble';
      this.introBubble.id = 'gifty-intro-bubble';
      this.introBubble.style.display = 'none';
      this.introBubble.innerHTML = `
        <div class="gifty-intro-text">
          Hey! I'm <strong>${MASCOT_NAME}</strong><br>Need help finding the perfect gift?
        </div>
        <button class="gifty-intro-close" id="gifty-intro-close-btn" aria-label="Dismiss message">&times;</button>
      `;

      // Assistant Panel
      this.panel = document.createElement('div');
      this.panel.className = 'gifty-panel';
      this.panel.id = 'gifty-panel';
      this.panel.setAttribute('role', 'dialog');
      this.panel.setAttribute('aria-label', `${MASCOT_NAME} Assistant Panel`);

      this.panel.innerHTML = `
        <div class="gifty-panel-header">
          <div class="gifty-header-left">
            <div class="gifty-header-avatar" id="gifty-header-avatar">
              ${getGiftySVG('happy', 38)}
            </div>
            <div>
              <div class="gifty-header-title">${MASCOT_NAME}</div>
              <div class="gifty-header-subtitle">Your Gifting Companion</div>
            </div>
          </div>
          <button class="gifty-panel-close" id="gifty-panel-close-btn" aria-label="Close panel">&times;</button>
        </div>
        <div class="gifty-panel-body" id="gifty-panel-body">
          <!-- Dynamic conversation content populated here -->
        </div>
      `;

      this.container.appendChild(this.introBubble);
      this.container.appendChild(this.panel);
      this.container.appendChild(this.launcher);
      document.body.appendChild(this.container);
    }

    bindEvents() {
      // Toggle Panel
      this.launcher.addEventListener('click', () => this.togglePanel());
      
      // Close Panel Button
      this.container.querySelector('#gifty-panel-close-btn').addEventListener('click', (e) => {
        e.stopPropagation();
        this.closePanel();
      });

      // Close Intro Bubble Button
      this.container.querySelector('#gifty-intro-close-btn').addEventListener('click', (e) => {
        e.stopPropagation();
        this.dismissIntro();
      });

      // Escape Key Listener
      document.addEventListener('keydown', (e) => {
        if (e.key === 'Escape' && this.isOpen) {
          this.closePanel();
        }
      });

      // Click Outside Listener
      document.addEventListener('click', (e) => {
        if (this.isOpen && !this.container.contains(e.target)) {
          this.closePanel();
        }
      });
    }

    checkFirstVisit() {
      const isDismissed = localStorage.getItem(STORAGE_KEY_INTRO_DISMISSED);
      if (!isDismissed) {
        setTimeout(() => {
          if (!this.isOpen) {
            this.introBubble.style.display = 'flex';
            const dot = this.container.querySelector('#gifty-notif-dot');
            if (dot) dot.style.display = 'block';
          }
        }, 1200);
      }
    }

    dismissIntro() {
      this.introBubble.style.display = 'none';
      const dot = this.container.querySelector('#gifty-notif-dot');
      if (dot) dot.style.display = 'none';
      localStorage.setItem(STORAGE_KEY_INTRO_DISMISSED, 'true');
    }

    togglePanel() {
      if (this.isOpen) {
        this.closePanel();
      } else {
        this.openPanel();
      }
    }

    openPanel() {
      this.isOpen = true;
      this.dismissIntro();
      this.panel.classList.add('open');
      this.launcher.setAttribute('aria-expanded', 'true');
      this.renderConversation();
    }

    closePanel() {
      this.isOpen = false;
      this.panel.classList.remove('open');
      this.launcher.setAttribute('aria-expanded', 'false');
    }

    onTabSwitched(tabId) {
      this.currentTab = tabId;
      if (this.isOpen) {
        this.renderConversation();
      }
    }

    renderConversation(customMessage = null, customActions = null, expression = 'happy') {
      const body = this.container.querySelector('#gifty-panel-body');
      const avatarContainer = this.container.querySelector('#gifty-header-avatar');

      // Determine greeting & actions based on active tab if no custom prompt provided
      let messageText = customMessage;
      let actions = customActions;

      if (!messageText) {
        if (this.currentTab === 'welcome') {
          expression = 'happy';
          messageText = "Hi, I'm Gifty! Welcome to GiftWise. I help you find thoughtful gifts based on real feedback. What would you like to do?";
          actions = [
            { label: `🎁 Get Gift Recommendations`, action: () => this.switchToTab('recommendations') },
            { label: `✍️ Share Gifting Feedback`, action: () => this.switchToTab('log-experience') },
            { label: `📊 View Analytics`, action: () => this.switchToTab('analytics') },
            { label: `🛍️ Browse Catalog`, action: () => this.switchToTab('catalog') }
          ];
        } else if (this.currentTab === 'recommendations') {
          expression = 'happy';
          messageText = "Looking for a gift? Let's find something they'll love! Pick an occasion or relationship below.";
          actions = [
            { label: `🎯 Find Gifts`, action: () => this.guideToRecs() },
            { label: `🎂 Birthday Gift Preset`, action: () => this.presetOccasion('Birthday') },
            { label: `❤️ Gift for Partner`, action: () => this.presetRelationship('Partner') },
            { label: `🤝 Gift for a Friend`, action: () => this.presetRelationship('Friend') },
            { label: `💰 Under $50 Budget`, action: () => this.presetBudget(10, 50) }
          ];
        } else if (this.currentTab === 'analytics') {
          expression = 'thinking';
          messageText = "Here's what our data shows about satisfaction rates, price points, and gift performance.";
          actions = [
            { label: `📊 View Satisfaction Gap`, action: () => this.scrollToElement('analytics-gap-table') },
            { label: `⭐ Reliable Gifts`, action: () => this.scrollToElement('analytics-reliable-table') },
            { label: `⚠️ Common Gift Pitfalls`, action: () => this.scrollToElement('analytics-failure-table') },
            { label: `🎁 Find Recommendations`, action: () => this.switchToTab('recommendations') }
          ];
        } else if (this.currentTab === 'catalog') {
          expression = 'curious';
          messageText = "Browse gifts by category or search by keyword to see ratings and prices.";
          actions = [
            { label: `🔍 Search Gifts`, action: () => this.focusCatalogSearch() },
            { label: `✍️ Share Feedback on a Gift`, action: () => this.switchToTab('log-experience') },
            { label: `🎁 Get Recommendations`, action: () => this.switchToTab('recommendations') }
          ];
        } else if (this.currentTab === 'log-experience') {
          expression = 'celebrating';
          messageText = "Gave a gift recently? Tell us how it went to help improve future recommendations!";
          actions = [
            { label: `✍️ Fill Out Feedback`, action: () => this.scrollToElement('experience-form') },
            { label: `🛍️ Browse Catalog`, action: () => this.switchToTab('catalog') }
          ];
        }
      }

      // Update avatar SVG with expression
      if (avatarContainer) {
        avatarContainer.innerHTML = getGiftySVG(expression, 38);
      }

      // Build HTML
      let html = `
        <div class="gifty-message">
          <div class="gifty-message-avatar">${getGiftySVG(expression, 30)}</div>
          <div class="gifty-bubble">${messageText}</div>
        </div>
      `;

      if (actions && actions.length > 0) {
        html += `
          <div class="gifty-actions-container">
            <div class="gifty-action-title">Quick Actions</div>
        `;
        actions.forEach((act, idx) => {
          html += `
            <button class="gifty-action-btn" data-act-idx="${idx}">
              <span>${act.label}</span>
              <span class="gifty-action-arrow">➔</span>
            </button>
          `;
        });
        html += `</div>`;
      }

      body.innerHTML = html;

      // Attach click events to action buttons
      const btnEls = body.querySelectorAll('.gifty-action-btn');
      btnEls.forEach(btn => {
        btn.addEventListener('click', () => {
          const idx = parseInt(btn.getAttribute('data-act-idx'));
          if (actions[idx] && typeof actions[idx].action === 'function') {
            actions[idx].action();
          }
        });
      });
    }

    // Helper Actions & Navigation
    switchToTab(tabId) {
      if (window.switchTab) {
        window.switchTab(tabId);
      }
    }

    guideToRecs() {
      this.switchToTab('recommendations');
      this.scrollToElement('recommendation-form');
    }

    presetOccasion(occName) {
      this.switchToTab('recommendations');
      const select = document.getElementById('rec-occasion');
      if (select) {
        for (let i = 0; i < select.options.length; i++) {
          if (select.options[i].text.toLowerCase().includes(occName.toLowerCase())) {
            select.selectedIndex = i;
            break;
          }
        }
      }
      this.renderConversation(`Great! I've pre-selected <strong>${occName}</strong> for you. Fill in your budget & click Generate!`, [
        { label: 'Generate Recommendations', action: () => this.submitRecForm() },
        { label: 'Change Budget', action: () => this.scrollToElement('rec-budget-min') }
      ], 'celebrating');
    }

    presetRelationship(relName) {
      this.switchToTab('recommendations');
      const select = document.getElementById('rec-relationship');
      if (select) {
        for (let i = 0; i < select.options.length; i++) {
          if (select.options[i].text.toLowerCase().includes(relName.toLowerCase())) {
            select.selectedIndex = i;
            break;
          }
        }
      }
      this.renderConversation(`Sweet! I've selected <strong>${relName}</strong>. Choose budget range to discover top Bayesian gifts!`, [
        { label: 'Generate Recommendations', action: () => this.submitRecForm() }
      ], 'happy');
    }

    presetBudget(min, max) {
      this.switchToTab('recommendations');
      if (window.setBudget) {
        window.setBudget(min, max);
      }
      this.renderConversation(`Budget set to <strong>$${min} - $${max}</strong>! Ready to generate recommendations?`, [
        { label: 'Generate Recommendations', action: () => this.submitRecForm() }
      ], 'celebrating');
    }

    submitRecForm() {
      const form = document.getElementById('recommendation-form');
      if (form) {
        form.dispatchEvent(new Event('submit', { cancelable: true, bubbles: true }));
        this.closePanel();
      }
    }

    focusCatalogSearch() {
      const input = document.getElementById('catalog-search');
      if (input) {
        input.focus();
        input.scrollIntoView({ behavior: 'smooth', block: 'center' });
      }
    }

    explainReviews() {
      this.renderConversation(
        "Gifting reviews measure giver expectations vs. actual recipient happiness! When you submit a review, VADER NLP analyzes the sentiment and updates our Bayesian confidence scores.",
        [
          { label: 'Submit a Review Now', action: () => this.scrollToElement('experience-form') },
          { label: 'View Analytics Dashboard', action: () => this.switchToTab('analytics') }
        ],
        'thinking'
      );
    }

    explainBayesian() {
      this.renderConversation(
        "Standard reviews suffer from small-sample bias (e.g. 1 review of 10/10 vs. 50 reviews of 9.2/10). Our Bayesian engine applies shrinkage towards the global mean with prior weight C=10.0, ensuring high-confidence recommendations you can genuinely trust!",
        [
          { label: 'Find Recommended Gifts', action: () => this.switchToTab('recommendations') },
          { label: 'Log Gifting Experience', action: () => this.switchToTab('log-experience') },
          { label: 'View Analytics Dashboard', action: () => this.switchToTab('analytics') }
        ],
        'thinking'
      );
    }

    scrollToElement(id) {
      const el = document.getElementById(id);
      if (el) {
        el.scrollIntoView({ behavior: 'smooth', block: 'start' });
      }
    }
  }

  // Initialize Gifty Assistant on DOM Ready
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initGifty);
  } else {
    initGifty();
  }

  function initGifty() {
    window.giftyInstance = new GiftyAssistant();

    // Hook into existing switchTab function if present
    if (typeof window.switchTab === 'function') {
      const originalSwitchTab = window.switchTab;
      window.switchTab = function (tabId, event) {
        originalSwitchTab(tabId, event);
        if (window.giftyInstance) {
          window.giftyInstance.onTabSwitched(tabId);
        }
      };
    }
  }
})();
