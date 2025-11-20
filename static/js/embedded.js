/**
 * Embedded Mode JavaScript - Phase 3
 *
 * Handles communication between the embedded application and the
 * parent Integrated Business Platform.
 */

(function() {
    'use strict';

    /**
     * Embedded Mode Manager
     */
    const EmbeddedMode = {
        // Configuration
        config: {
            platformOrigin: document.body.dataset.platformOrigin || '*',
            enablePostMessage: true,
            enableSessionSync: true,
            enableThemeSync: true,
            enableNavigationSync: true,
            debug: false
        },

        // State
        isEmbedded: false,
        parentWindow: null,

        /**
         * Initialize embedded mode
         */
        init: function() {
            this.detectEmbeddedMode();

            if (this.isEmbedded) {
                this.log('Embedded mode detected');
                this.setupPostMessageListener();
                this.setupNavigationSync();
                this.setupThemeSync();
                this.notifyParentReady();
            }
        },

        /**
         * Detect if running in iframe
         */
        detectEmbeddedMode: function() {
            try {
                this.isEmbedded = window.self !== window.top;
                this.parentWindow = window.parent;

                // Add embedded class to body
                if (this.isEmbedded) {
                    document.body.classList.add('embedded-mode');

                    // Check for embedded mode parameters
                    const urlParams = new URLSearchParams(window.location.search);
                    const embeddedParam = urlParams.get('embedded');

                    if (embeddedParam === 'minimal') {
                        document.body.classList.add('minimal-chrome');
                    } else if (embeddedParam === 'no-nav') {
                        document.body.classList.add('no-navigation');
                    }
                }
            } catch (e) {
                this.log('Error detecting embedded mode:', e);
                this.isEmbedded = false;
            }
        },

        /**
         * Setup PostMessage listener for parent communication
         */
        setupPostMessageListener: function() {
            if (!this.config.enablePostMessage) return;

            window.addEventListener('message', (event) => {
                // Validate origin if specified
                if (this.config.platformOrigin !== '*' &&
                    event.origin !== this.config.platformOrigin) {
                    this.log('Rejected message from unauthorized origin:', event.origin);
                    return;
                }

                this.log('Received message from parent:', event.data);

                // Handle different message types
                if (event.data.type) {
                    switch (event.data.type) {
                        case 'session_sync':
                            this.handleSessionSync(event.data);
                            break;
                        case 'theme_update':
                            this.handleThemeUpdate(event.data);
                            break;
                        case 'navigation_update':
                            this.handleNavigationUpdate(event.data);
                            break;
                        case 'resize':
                            this.handleResize(event.data);
                            break;
                        case 'logout':
                            this.handleLogout(event.data);
                            break;
                        default:
                            this.log('Unknown message type:', event.data.type);
                    }
                }
            });

            this.log('PostMessage listener initialized');
        },

        /**
         * Notify parent window that iframe is ready
         */
        notifyParentReady: function() {
            this.sendMessageToParent({
                type: 'iframe_ready',
                timestamp: new Date().toISOString(),
                url: window.location.href
            });
        },

        /**
         * Send message to parent window
         */
        sendMessageToParent: function(message) {
            if (!this.isEmbedded || !this.config.enablePostMessage) return;

            try {
                this.parentWindow.postMessage(message, this.config.platformOrigin);
                this.log('Sent message to parent:', message);
            } catch (e) {
                this.log('Error sending message to parent:', e);
            }
        },

        /**
         * Handle session synchronization from parent
         */
        handleSessionSync: function(data) {
            if (!this.config.enableSessionSync) return;

            this.log('Syncing session from parent');

            // Store session data in sessionStorage
            if (data.sessionToken) {
                sessionStorage.setItem('platform_session_token', data.sessionToken);
            }

            if (data.userData) {
                sessionStorage.setItem('platform_user_data', JSON.stringify(data.userData));
            }

            // Notify application of session update
            window.dispatchEvent(new CustomEvent('session_synced', {
                detail: data
            }));
        },

        /**
         * Handle theme updates from parent
         */
        handleThemeUpdate: function(data) {
            if (!this.config.enableThemeSync) return;

            this.log('Updating theme from parent:', data.theme);

            // Apply theme to body
            if (data.theme) {
                document.body.setAttribute('data-theme', data.theme);
            }

            // Apply custom CSS variables if provided
            if (data.cssVariables) {
                const root = document.documentElement;
                for (const [key, value] of Object.entries(data.cssVariables)) {
                    root.style.setProperty(`--${key}`, value);
                }
            }

            // Apply custom colors if provided
            if (data.primaryColor) {
                document.documentElement.style.setProperty('--primary-color', data.primaryColor);
            }
            if (data.secondaryColor) {
                document.documentElement.style.setProperty('--secondary-color', data.secondaryColor);
            }

            // Notify application of theme update
            window.dispatchEvent(new CustomEvent('theme_updated', {
                detail: data
            }));
        },

        /**
         * Handle navigation updates from parent
         */
        handleNavigationUpdate: function(data) {
            if (!this.config.enableNavigationSync) return;

            this.log('Handling navigation from parent:', data.path);

            if (data.path) {
                // Navigate to specified path
                window.location.href = data.path;
            }
        },

        /**
         * Handle resize events from parent
         */
        handleResize: function(data) {
            this.log('Handling resize:', data);

            // Notify application of resize
            window.dispatchEvent(new CustomEvent('embedded_resize', {
                detail: {
                    width: data.width,
                    height: data.height
                }
            }));
        },

        /**
         * Handle logout from parent
         */
        handleLogout: function(data) {
            this.log('Logout requested from parent');

            // Clear local storage
            sessionStorage.clear();
            localStorage.removeItem('platform_session_token');

            // Redirect to logout URL
            window.location.href = '/accounts/logout/';
        },

        /**
         * Setup navigation synchronization
         */
        setupNavigationSync: function() {
            if (!this.config.enableNavigationSync) return;

            // Notify parent of navigation changes
            let lastPath = window.location.pathname;

            window.addEventListener('popstate', () => {
                const currentPath = window.location.pathname;
                if (currentPath !== lastPath) {
                    this.sendMessageToParent({
                        type: 'navigation_change',
                        path: currentPath,
                        url: window.location.href,
                        timestamp: new Date().toISOString()
                    });
                    lastPath = currentPath;
                }
            });

            // Intercept link clicks to notify parent
            document.addEventListener('click', (e) => {
                const link = e.target.closest('a');
                if (link && link.href && !link.target && !link.download) {
                    const url = new URL(link.href);
                    if (url.origin === window.location.origin) {
                        this.sendMessageToParent({
                            type: 'navigation_intent',
                            path: url.pathname,
                            url: link.href,
                            timestamp: new Date().toISOString()
                        });
                    }
                }
            });

            this.log('Navigation sync initialized');
        },

        /**
         * Setup theme synchronization
         */
        setupThemeSync: function() {
            if (!this.config.enableThemeSync) return;

            // Request current theme from parent
            this.sendMessageToParent({
                type: 'theme_request',
                timestamp: new Date().toISOString()
            });

            this.log('Theme sync initialized');
        },

        /**
         * Update iframe height based on content
         */
        updateHeight: function() {
            if (!this.isEmbedded) return;

            const height = document.documentElement.scrollHeight;
            this.sendMessageToParent({
                type: 'height_update',
                height: height,
                timestamp: new Date().toISOString()
            });
        },

        /**
         * Notify parent of content changes
         */
        notifyContentChange: function() {
            this.updateHeight();
        },

        /**
         * Debug logging
         */
        log: function(...args) {
            if (this.config.debug || document.body.dataset.debugEmbedded === 'true') {
                console.log('[EmbeddedMode]', ...args);
            }
        }
    };

    /**
     * Auto-initialize on DOMContentLoaded
     */
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', function() {
            EmbeddedMode.init();
        });
    } else {
        EmbeddedMode.init();
    }

    /**
     * Update height on content changes
     */
    window.addEventListener('load', function() {
        EmbeddedMode.updateHeight();
    });

    // Update height when DOM changes
    if (window.MutationObserver) {
        const observer = new MutationObserver(function() {
            EmbeddedMode.notifyContentChange();
        });

        observer.observe(document.body, {
            childList: true,
            subtree: true,
            attributes: false
        });
    }

    /**
     * Export to window for external access
     */
    window.EmbeddedMode = EmbeddedMode;

})();
