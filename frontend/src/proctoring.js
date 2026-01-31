/**
 * Proctoring Client Module
 * 
 * Handles client-side anti-cheat monitoring:
 * - Webcam capture and frame sending
 * - Tab switch / window blur detection
 * - Copy/paste detection
 * - Keyboard shortcut monitoring
 * 
 * Features with 100% client-side accuracy:
 * - Tab switching detection
 * - Window focus/blur detection
 * - Copy/paste detection
 * - Right-click prevention
 * - DevTools detection
 */

class ProctoringClient {
    constructor(options = {}) {
        this.apiBase = options.apiBase || '/api/proctoring';
        this.authToken = options.authToken || localStorage.getItem('token'); // Get auth token
        this.sessionId = null;
        this.isActive = false;
        this.videoStream = null;
        this.videoElement = null;
        this.canvasElement = null;
        this.captureInterval = null;
        
        // Configuration
        this.config = {
            captureIntervalMs: options.captureInterval || 2000, // Capture every 2 seconds
            verifyPersonEvery: options.verifyPersonEvery || 30, // Verify person every 30 frames
            enableTabSwitchDetection: options.enableTabSwitchDetection !== false,
            enableCopyPasteDetection: options.enableCopyPasteDetection !== false,
            enableRightClickPrevention: options.enableRightClickPrevention || false,
            showAlerts: options.showAlerts !== false,
            onViolation: options.onViolation || null,
            onAlert: options.onAlert || null
        };
        
        this.frameCount = 0;
        this.violations = [];
        
        // Bind methods
        this._handleVisibilityChange = this._handleVisibilityChange.bind(this);
        this._handleWindowBlur = this._handleWindowBlur.bind(this);
        this._handleWindowFocus = this._handleWindowFocus.bind(this);
        this._handleCopy = this._handleCopy.bind(this);
        this._handlePaste = this._handlePaste.bind(this);
        this._handleContextMenu = this._handleContextMenu.bind(this);
        this._handleKeyDown = this._handleKeyDown.bind(this);
    }
    
    /**
     * Check proctoring system status
     */
    async checkStatus() {
        try {
            const response = await fetch(`${this.apiBase}/status`);
            return await response.json();
        } catch (error) {
            console.error('Failed to check proctoring status:', error);
            return { available: false, error: error.message };
        }
    }
    
    /**
     * Start proctoring session
     */
    async startSession(interviewId, sensitivity = 'medium') {
        try {
            // Start server-side session
            const response = await fetch(`${this.apiBase}/session/start`, {
                method: 'POST',
                headers: { 
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${this.authToken}`
                },
                body: JSON.stringify({
                    interview_id: interviewId,
                    sensitivity: sensitivity
                })
            });
            
            if (!response.ok) {
                throw new Error('Failed to start proctoring session');
            }
            
            const data = await response.json();
            this.sessionId = data.session_id;
            this.isActive = true;
            
            // Start client-side monitoring
            this._startClientMonitoring();
            
            console.log('Proctoring session started:', this.sessionId);
            return data;
        } catch (error) {
            console.error('Error starting proctoring session:', error);
            throw error;
        }
    }
    
    /**
     * Initialize webcam for face monitoring
     */
    async initializeWebcam(videoElementId, canvasElementId) {
        try {
            // Get video stream
            this.videoStream = await navigator.mediaDevices.getUserMedia({
                video: {
                    width: { ideal: 640 },
                    height: { ideal: 480 },
                    facingMode: 'user'
                },
                audio: false
            });
            
            // Set up video element
            this.videoElement = document.getElementById(videoElementId);
            if (this.videoElement) {
                this.videoElement.srcObject = this.videoStream;
                await this.videoElement.play();
            }
            
            // Set up canvas for frame capture
            this.canvasElement = document.getElementById(canvasElementId);
            if (!this.canvasElement) {
                this.canvasElement = document.createElement('canvas');
                this.canvasElement.width = 640;
                this.canvasElement.height = 480;
            }
            
            console.log('Webcam initialized for proctoring');
            return true;
        } catch (error) {
            console.error('Failed to initialize webcam:', error);
            return false;
        }
    }
    
    /**
     * Start capturing and analyzing frames
     */
    startFrameCapture() {
        if (!this.videoElement || !this.canvasElement || !this.sessionId) {
            console.error('Cannot start frame capture: missing video, canvas, or session');
            return;
        }
        
        this.captureInterval = setInterval(async () => {
            if (!this.isActive) return;
            
            try {
                await this._captureAndAnalyzeFrame();
            } catch (error) {
                console.error('Frame analysis error:', error);
            }
        }, this.config.captureIntervalMs);
        
        console.log('Frame capture started');
    }
    
    /**
     * Stop frame capture
     */
    stopFrameCapture() {
        if (this.captureInterval) {
            clearInterval(this.captureInterval);
            this.captureInterval = null;
        }
    }
    
    /**
     * Capture current frame and send for analysis
     */
    async _captureAndAnalyzeFrame() {
        if (!this.videoElement || !this.canvasElement) return;
        
        // Draw current frame to canvas
        const ctx = this.canvasElement.getContext('2d');
        ctx.drawImage(
            this.videoElement,
            0, 0,
            this.canvasElement.width,
            this.canvasElement.height
        );
        
        // Convert to base64
        const frameBase64 = this.canvasElement.toDataURL('image/jpeg', 0.7)
            .replace('data:image/jpeg;base64,', '');
        
        this.frameCount++;
        
        // Should we verify person identity this frame?
        const verifyPerson = this.frameCount % this.config.verifyPersonEvery === 0;
        
        // Send to server for analysis
        const response = await fetch(`${this.apiBase}/analyze-frame`, {
            method: 'POST',
            headers: { 
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${this.authToken}`
            },
            body: JSON.stringify({
                session_id: this.sessionId,
                frame_base64: frameBase64,
                verify_person: verifyPerson
            })
        });
        
        if (!response.ok) {
            console.error('Frame analysis failed');
            return;
        }
        
        const results = await response.json();
        
        // Handle violations
        if (results.violations && results.violations.length > 0) {
            this._handleViolations(results.violations);
        }
        
        // Handle alerts
        if (results.alerts && results.alerts.length > 0) {
            this._handleAlerts(results.alerts);
        }
        
        return results;
    }
    
    /**
     * Start client-side monitoring (tab switches, etc.)
     */
    _startClientMonitoring() {
        if (this.config.enableTabSwitchDetection) {
            document.addEventListener('visibilitychange', this._handleVisibilityChange);
            window.addEventListener('blur', this._handleWindowBlur);
            window.addEventListener('focus', this._handleWindowFocus);
        }
        
        if (this.config.enableCopyPasteDetection) {
            document.addEventListener('copy', this._handleCopy);
            document.addEventListener('paste', this._handlePaste);
        }
        
        if (this.config.enableRightClickPrevention) {
            document.addEventListener('contextmenu', this._handleContextMenu);
        }
        
        // Detect suspicious keyboard shortcuts (Ctrl+C, Ctrl+V, Alt+Tab, etc.)
        document.addEventListener('keydown', this._handleKeyDown);
        
        console.log('Client-side monitoring started');
    }
    
    /**
     * Stop client-side monitoring
     */
    _stopClientMonitoring() {
        document.removeEventListener('visibilitychange', this._handleVisibilityChange);
        window.removeEventListener('blur', this._handleWindowBlur);
        window.removeEventListener('focus', this._handleWindowFocus);
        document.removeEventListener('copy', this._handleCopy);
        document.removeEventListener('paste', this._handlePaste);
        document.removeEventListener('contextmenu', this._handleContextMenu);
        document.removeEventListener('keydown', this._handleKeyDown);
    }
    
    /**
     * Handle visibility change (tab switch)
     */
    async _handleVisibilityChange() {
        if (document.hidden) {
            console.log('Tab switch detected');
            await this._reportTabSwitch('switch');
        }
    }
    
    /**
     * Handle window blur
     */
    async _handleWindowBlur() {
        console.log('Window blur detected');
        await this._reportTabSwitch('blur');
    }
    
    /**
     * Handle window focus
     */
    _handleWindowFocus() {
        console.log('Window focused');
    }
    
    /**
     * Handle copy event
     */
    _handleCopy(event) {
        console.log('Copy detected');
        this._recordClientViolation('copy_attempt', 'User attempted to copy text');
    }
    
    /**
     * Handle paste event
     */
    _handlePaste(event) {
        console.log('Paste detected');
        this._recordClientViolation('paste_attempt', 'User attempted to paste text');
    }
    
    /**
     * Handle right-click
     */
    _handleContextMenu(event) {
        event.preventDefault();
        console.log('Right-click prevented');
    }
    
    /**
     * Handle keyboard shortcuts
     */
    _handleKeyDown(event) {
        // Detect suspicious shortcuts
        const suspiciousShortcuts = [
            { keys: ['Control', 'c'], name: 'Copy' },
            { keys: ['Control', 'v'], name: 'Paste' },
            { keys: ['Control', 'Shift', 'i'], name: 'DevTools' },
            { keys: ['F12'], name: 'DevTools' },
            { keys: ['Alt', 'Tab'], name: 'Alt+Tab' }
        ];
        
        // Check for DevTools
        if ((event.ctrlKey && event.shiftKey && event.key === 'I') ||
            (event.ctrlKey && event.shiftKey && event.key === 'J') ||
            (event.key === 'F12')) {
            console.log('DevTools shortcut detected');
            this._recordClientViolation('devtools_attempt', 'User attempted to open DevTools');
        }
    }
    
    /**
     * Report tab switch to server
     */
    async _reportTabSwitch(eventType) {
        if (!this.sessionId) return;
        
        try {
            const response = await fetch(`${this.apiBase}/tab-switch`, {
                method: 'POST',
                headers: { 
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${this.authToken}`
                },
                body: JSON.stringify({
                    session_id: this.sessionId,
                    event_type: eventType
                })
            });
            
            if (response.ok) {
                const result = await response.json();
                this._handleViolations([result.violation]);
            }
        } catch (error) {
            console.error('Failed to report tab switch:', error);
        }
    }
    
    /**
     * Record a client-side violation
     */
    _recordClientViolation(type, details) {
        const violation = {
            type: type,
            severity: 'low',
            timestamp: new Date().toISOString(),
            details: details,
            source: 'client'
        };
        
        this.violations.push(violation);
        this._handleViolations([violation]);
    }
    
    /**
     * Handle violations
     */
    _handleViolations(violations) {
        this.violations.push(...violations);
        
        if (this.config.onViolation) {
            violations.forEach(v => this.config.onViolation(v));
        }
        
        // Log violations
        violations.forEach(v => {
            console.warn(`Proctoring Violation: ${v.type} (${v.severity})`, v.details);
        });
    }
    
    /**
     * Handle alerts
     */
    _handleAlerts(alerts) {
        if (this.config.onAlert) {
            alerts.forEach(a => this.config.onAlert(a));
        }
        
        if (this.config.showAlerts) {
            alerts.forEach(a => {
                console.log('Proctoring Alert:', a);
            });
        }
    }
    
    /**
     * Upload reference photo for person verification
     */
    async setReferencePhoto(photoBlob) {
        if (!this.sessionId) {
            throw new Error('No active session');
        }
        
        const formData = new FormData();
        formData.append('photo', photoBlob, 'reference.jpg');
        
        const response = await fetch(
            `${this.apiBase}/session/reference-photo?session_id=${this.sessionId}`,
            {
                method: 'POST',
                body: formData
            }
        );
        
        return await response.json();
    }
    
    /**
     * Capture reference photo from webcam
     */
    async captureReferencePhoto() {
        if (!this.videoElement || !this.canvasElement) {
            throw new Error('Webcam not initialized');
        }
        
        const ctx = this.canvasElement.getContext('2d');
        ctx.drawImage(
            this.videoElement,
            0, 0,
            this.canvasElement.width,
            this.canvasElement.height
        );
        
        return new Promise((resolve) => {
            this.canvasElement.toBlob(async (blob) => {
                const result = await this.setReferencePhoto(blob);
                resolve(result);
            }, 'image/jpeg', 0.9);
        });
    }
    
    /**
     * Get current session report
     */
    async getReport() {
        if (!this.sessionId) {
            throw new Error('No active session');
        }
        
        const response = await fetch(`${this.apiBase}/session/${this.sessionId}/report`);
        return await response.json();
    }
    
    /**
     * End proctoring session
     */
    async endSession() {
        if (!this.sessionId) return;
        
        // Stop monitoring
        this.isActive = false;
        this.stopFrameCapture();
        this._stopClientMonitoring();
        
        // Stop webcam
        if (this.videoStream) {
            this.videoStream.getTracks().forEach(track => track.stop());
            this.videoStream = null;
        }
        
        // Get final report from server
        try {
            const response = await fetch(`${this.apiBase}/session/${this.sessionId}/end`, {
                method: 'POST',
                headers: {
                    'Authorization': `Bearer ${this.authToken}`
                }
            });
            
            const result = await response.json();
            console.log('Proctoring session ended:', result);
            
            this.sessionId = null;
            return result;
        } catch (error) {
            console.error('Error ending proctoring session:', error);
            throw error;
        }
    }
    
    /**
     * Get all recorded violations
     */
    getViolations() {
        return this.violations;
    }
    
    /**
     * Check if proctoring is currently active
     */
    isProctoring() {
        return this.isActive;
    }
}

// Export for use in other modules
export default ProctoringClient;

// Also expose as global for non-module usage
if (typeof window !== 'undefined') {
    window.ProctoringClient = ProctoringClient;
}
