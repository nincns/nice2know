/**
 * Nice2Know - Web Editor
 * Main editor logic and UI handling
 */

class Editor {
    constructor() {
        this.mailId = null;
        this.data = null;
        this.originalData = null;
        this.isDirty = false;
        
        this.init();
    }
    
    async init() {
        // Get mail_id from DOM
        const appEl = document.getElementById('app');
        this.mailId = appEl?.dataset?.mailId;
        
        if (!this.mailId) {
            this.showError('Mail-ID nicht gefunden');
            return;
        }
        
        // Load data
        await this.loadData();
    }
    
    async loadData() {
        try {
            this.data = await API.load(this.mailId);
            this.originalData = JSON.parse(JSON.stringify(this.data)); // Deep clone
            
            this.render();
            this.attachEventListeners();
        } catch (error) {
            this.showError('Fehler beim Laden der Daten: ' + error.message);
        }
    }
    
    render() {
        const app = document.getElementById('app');
        
        const html = `
            ${this.renderHeader()}
            <div class="container">
                ${this.renderQualitySummary()}
                ${this.renderProblemSection()}
                ${this.renderSolutionSection()}
                ${this.renderAssetSection()}
            </div>
            ${this.renderFooter()}
        `;
        
        app.innerHTML = html;
    }
    
    renderHeader() {
        return `
            <div class="header">
                <div class="header-content">
                    <div class="header-title">
                        <span class="header-icon">📝</span>
                        <div class="header-text">
                            <h1>Daten bearbeiten</h1>
                            <div class="mail-id">Mail-ID: ${this.mailId}</div>
                        </div>
                    </div>
                    <div class="header-actions">
                        <button class="btn btn-secondary" id="btn-cancel">
                            Abbrechen
                        </button>
                        <button class="btn btn-success" id="btn-save">
                            💾 Speichern
                        </button>
                    </div>
                </div>
            </div>
        `;
    }
    
    renderQualitySummary() {
        const stats = this.calculateQualityStats();
        
        return `
            <div class="quality-summary">
                <div class="quality-header">
                    <span class="quality-icon">📊</span>
                    <div>
                        <div class="quality-title">Datenqualität</div>
                        <div class="quality-score">${stats.percent}%</div>
                    </div>
                </div>
                <div class="quality-stats">
                    <span class="quality-stat complete">✓ ${stats.complete} vollständig</span>
                    <span class="quality-stat missing">⚠ ${stats.missing} fehlen</span>
                    <span class="quality-stat unclear">❓ ${stats.unclear} unklar</span>
                </div>
                <p class="quality-description">
                    Bitte füllen Sie die fehlenden oder unklaren Felder aus.
                </p>
            </div>
        `;
    }
    
    renderProblemSection() {
        const problem = this.data.problem.problem || {};
        const reporter = this.data.problem.reporter || {};
        const classification = this.data.problem.classification || {};
        
        return `
            <div class="section">
                <div class="section-header">
                    <span class="section-icon">⚠️</span>
                    <span class="section-title">Problem</span>
                </div>
                <div class="section-body">
                    ${this.renderField('problem_title', 'Titel', problem.title, 'text', true)}
                    ${this.renderField('problem_description', 'Beschreibung', problem.description, 'textarea', true)}
                    ${this.renderField('reporter_name', 'Melder', reporter.name, 'text')}
                    ${this.renderField('reporter_email', 'E-Mail', reporter.email, 'email')}
                    ${this.renderField('reporter_department', 'Abteilung', reporter.department, 'text')}
                    
                    <div class="meta-grid">
                        <div class="meta-item">
                            <div class="meta-label">Schweregrad</div>
                            ${this.renderSelect('severity', classification.severity, [
                                { value: 'low', label: 'Niedrig' },
                                { value: 'medium', label: 'Mittel' },
                                { value: 'high', label: 'Hoch' },
                                { value: 'critical', label: 'Kritisch' }
                            ])}
                        </div>
                        <div class="meta-item">
                            <div class="meta-label">Kategorie</div>
                            ${this.renderField('category', '', classification.category, 'text', false, true)}
                        </div>
                        <div class="meta-item">
                            <div class="meta-label">Status</div>
                            ${this.renderSelect('status', this.data.problem.status, [
                                { value: 'new', label: 'Neu' },
                                { value: 'processing', label: 'In Bearbeitung' },
                                { value: 'resolved', label: 'Gelöst' }
                            ])}
                        </div>
                    </div>
                </div>
            </div>
        `;
    }
    
    renderSolutionSection() {
        if (!this.data.solution || !this.data.solution.solution) {
            return `
                <div class="section">
                    <div class="section-header">
                        <span class="section-icon">✅</span>
                        <span class="section-title">Lösung</span>
                    </div>
                    <div class="section-body">
                        <p class="text-muted text-center">Noch keine Lösung verfügbar.</p>
                    </div>
                </div>
            `;
        }
        
        const solution = this.data.solution.solution || {};
        const metadata = this.data.solution.metadata || {};
        
        return `
            <div class="section">
                <div class="section-header">
                    <span class="section-icon">✅</span>
                    <span class="section-title">Lösung</span>
                </div>
                <div class="section-body">
                    ${this.renderField('solution_title', 'Titel', solution.title, 'text')}
                    ${this.renderField('solution_description', 'Beschreibung', solution.description, 'textarea')}
                    
                    <div class="meta-grid">
                        <div class="meta-item">
                            <div class="meta-label">Typ</div>
                            ${this.renderField('solution_type', '', solution.type, 'text', false, true)}
                        </div>
                        <div class="meta-item">
                            <div class="meta-label">Ansatz</div>
                            ${this.renderField('solution_approach', '', solution.approach, 'text', false, true)}
                        </div>
                        <div class="meta-item">
                            <div class="meta-label">Komplexität</div>
                            ${this.renderSelect('solution_complexity', metadata.complexity, [
                                { value: 'low', label: 'Niedrig' },
                                { value: 'medium', label: 'Mittel' },
                                { value: 'high', label: 'Hoch' }
                            ])}
                        </div>
                        <div class="meta-item">
                            <div class="meta-label">Geschätzte Zeit</div>
                            ${this.renderField('solution_estimated_time', '', metadata.estimated_time, 'text', false, true)}
                        </div>
                    </div>
                </div>
            </div>
        `;
    }
    
    renderAssetSection() {
        const asset = this.data.asset.asset || {};
        const technical = this.data.asset.technical || {};
        
        return `
            <div class="section">
                <div class="section-header">
                    <span class="section-icon">🖥️</span>
                    <span class="section-title">Asset / Betroffenes System</span>
                </div>
                <div class="section-body">
                    ${this.renderField('asset_name', 'Name', asset.display_name || asset.name, 'text', true)}
                    ${this.renderField('asset_description', 'Beschreibung', asset.description, 'textarea')}
                    
                    <div class="meta-grid">
                        <div class="meta-item">
                            <div class="meta-label">Typ</div>
                            ${this.renderSelect('asset_type', asset.type, [
                                { value: 'hardware', label: 'Hardware' },
                                { value: 'software', label: 'Software' },
                                { value: 'service', label: 'Service' },
                                { value: 'network', label: 'Netzwerk' }
                            ])}
                        </div>
                        <div class="meta-item">
                            <div class="meta-label">Kategorie</div>
                            ${this.renderField('asset_category', '', asset.category, 'text', false, true)}
                        </div>
                        <div class="meta-item">
                            <div class="meta-label">Kritikalität</div>
                            ${this.renderSelect('asset_criticality', asset.criticality, [
                                { value: 'low', label: 'Niedrig' },
                                { value: 'medium', label: 'Mittel' },
                                { value: 'high', label: 'Hoch' },
                                { value: 'critical', label: 'Kritisch' }
                            ])}
                        </div>
                    </div>
                    
                    <h3 class="mt-3 mb-2">Technische Details</h3>
                    <div class="meta-grid">
                        <div class="meta-item">
                            <div class="meta-label">Software</div>
                            ${this.renderField('asset_software', '', technical.software, 'text', false, true)}
                        </div>
                        <div class="meta-item">
                            <div class="meta-label">Version</div>
                            ${this.renderField('asset_version', '', technical.version, 'text', false, true)}
                        </div>
                        <div class="meta-item">
                            <div class="meta-label">Plattform</div>
                            ${this.renderField('asset_platform', '', technical.platform, 'text', false, true)}
                        </div>
                    </div>
                </div>
            </div>
        `;
    }
    
    renderField(id, label, value, type = 'text', required = false, compact = false) {
        const isEmpty = !value || value === 'N/A' || value === 'null';
        const statusClass = isEmpty ? 'missing' : '';
        const statusIcon = isEmpty ? '⚠' : '✓';
        const displayValue = isEmpty ? '' : value;
        
        if (compact) {
            return `
                <input 
                    type="${type}" 
                    id="${id}" 
                    name="${id}"
                    class="field-input ${statusClass}" 
                    value="${this.escapeHtml(displayValue)}"
                    ${required ? 'required' : ''}
                />
            `;
        }
        
        const fieldHtml = type === 'textarea'
            ? `<textarea id="${id}" name="${id}" class="field-input ${statusClass}" ${required ? 'required' : ''}>${this.escapeHtml(displayValue)}</textarea>`
            : `<input type="${type}" id="${id}" name="${id}" class="field-input ${statusClass}" value="${this.escapeHtml(displayValue)}" ${required ? 'required' : ''}/>`;
        
        return `
            <div class="field-group">
                <label class="field-label" for="${id}">
                    <span class="field-status ${isEmpty ? 'status-missing' : 'status-complete'}">${statusIcon}</span>
                    ${label}
                    ${required ? '<span style="color: var(--danger)">*</span>' : ''}
                </label>
                ${fieldHtml}
            </div>
        `;
    }
    
    renderSelect(id, value, options) {
        const isEmpty = !value || value === 'N/A';
        const statusClass = isEmpty ? 'missing' : '';
        
        return `
            <select id="${id}" name="${id}" class="field-input ${statusClass}">
                <option value="">-- Bitte wählen --</option>
                ${options.map(opt => `
                    <option value="${opt.value}" ${value === opt.value ? 'selected' : ''}>
                        ${opt.label}
                    </option>
                `).join('')}
            </select>
        `;
    }
    
    renderFooter() {
        return `
            <div class="footer">
                <div class="footer-content">
                    <div class="footer-info">
                        Nice2Know Editor v1.0 &middot; Mail-ID: ${this.mailId}
                    </div>
                    <div class="footer-actions">
                        <button class="btn btn-secondary" id="btn-cancel-bottom">
                            Abbrechen
                        </button>
                        <button class="btn btn-success" id="btn-save-bottom">
                            💾 Speichern
                        </button>
                    </div>
                </div>
            </div>
        `;
    }
    
    attachEventListeners() {
        // Save buttons
        document.getElementById('btn-save')?.addEventListener('click', () => this.save());
        document.getElementById('btn-save-bottom')?.addEventListener('click', () => this.save());
        
        // Cancel buttons
        document.getElementById('btn-cancel')?.addEventListener('click', () => this.cancel());
        document.getElementById('btn-cancel-bottom')?.addEventListener('click', () => this.cancel());
        
        // Track changes
        const inputs = document.querySelectorAll('.field-input');
        inputs.forEach(input => {
            input.addEventListener('input', () => {
                this.isDirty = true;
            });
        });
        
        // Warn before leaving if unsaved changes
        window.addEventListener('beforeunload', (e) => {
            if (this.isDirty) {
                e.preventDefault();
                e.returnValue = '';
            }
        });
    }
    
    async save() {
        try {
            // Collect form data
            const updatedData = this.collectFormData();
            
            // Disable save buttons
            this.setButtonsDisabled(true);
            
            // Save via API
            await API.save(
                this.mailId,
                updatedData.problem,
                updatedData.solution,
                updatedData.asset
            );
            
            this.isDirty = false;
            this.showNotification('success', 'Erfolgreich gespeichert', 'Ihre Änderungen wurden gespeichert.');
            
            // Reload data
            setTimeout(() => {
                window.location.reload();
            }, 1500);
            
        } catch (error) {
            this.showNotification('error', 'Fehler beim Speichern', error.message);
            this.setButtonsDisabled(false);
        }
    }
    
    cancel() {
        if (this.isDirty) {
            if (!confirm('Sie haben ungespeicherte Änderungen. Wirklich abbrechen?')) {
                return;
            }
        }
        window.location.reload();
    }
    
    collectFormData() {
        const formData = {
            problem: JSON.parse(JSON.stringify(this.data.problem)),
            solution: this.data.solution ? JSON.parse(JSON.stringify(this.data.solution)) : null,
            asset: JSON.parse(JSON.stringify(this.data.asset))
        };
        
        // Problem fields
        formData.problem.problem.title = this.getFieldValue('problem_title');
        formData.problem.problem.description = this.getFieldValue('problem_description');
        formData.problem.reporter.name = this.getFieldValue('reporter_name');
        formData.problem.reporter.email = this.getFieldValue('reporter_email');
        formData.problem.reporter.department = this.getFieldValue('reporter_department');
        formData.problem.classification.severity = this.getFieldValue('severity');
        formData.problem.classification.category = this.getFieldValue('category');
        formData.problem.status = this.getFieldValue('status');
        
        // Solution fields (if exists)
        if (formData.solution) {
            formData.solution.solution.title = this.getFieldValue('solution_title');
            formData.solution.solution.description = this.getFieldValue('solution_description');
            formData.solution.solution.type = this.getFieldValue('solution_type');
            formData.solution.solution.approach = this.getFieldValue('solution_approach');
            formData.solution.metadata.complexity = this.getFieldValue('solution_complexity');
            formData.solution.metadata.estimated_time = this.getFieldValue('solution_estimated_time');
        }
        
        // Asset fields
        formData.asset.asset.name = this.getFieldValue('asset_name');
        formData.asset.asset.display_name = this.getFieldValue('asset_name');
        formData.asset.asset.description = this.getFieldValue('asset_description');
        formData.asset.asset.type = this.getFieldValue('asset_type');
        formData.asset.asset.category = this.getFieldValue('asset_category');
        formData.asset.asset.criticality = this.getFieldValue('asset_criticality');
        formData.asset.technical.software = this.getFieldValue('asset_software');
        formData.asset.technical.version = this.getFieldValue('asset_version');
        formData.asset.technical.platform = this.getFieldValue('asset_platform');
        
        return formData;
    }
    
    getFieldValue(id) {
        const field = document.getElementById(id);
        return field ? field.value.trim() : '';
    }
    
    setButtonsDisabled(disabled) {
        const buttons = [
            'btn-save',
            'btn-save-bottom',
            'btn-cancel',
            'btn-cancel-bottom'
        ];
        
        buttons.forEach(id => {
            const btn = document.getElementById(id);
            if (btn) {
                btn.disabled = disabled;
            }
        });
    }
    
    calculateQualityStats() {
        let complete = 0;
        let missing = 0;
        let unclear = 0;
        
        const fields = [
            this.data.problem.problem?.title,
            this.data.problem.problem?.description,
            this.data.problem.reporter?.name,
            this.data.problem.reporter?.email,
            this.data.problem.reporter?.department,
            this.data.asset.asset?.name,
            this.data.asset.asset?.description,
            this.data.asset.technical?.software,
            this.data.asset.technical?.version,
            this.data.asset.technical?.platform
        ];
        
        fields.forEach(field => {
            if (!field || field === 'N/A' || field === 'null') {
                missing++;
            } else {
                complete++;
            }
        });
        
        const total = complete + missing + unclear;
        const percent = total > 0 ? Math.round((complete / total) * 100) : 0;
        
        return { complete, missing, unclear, percent };
    }
    
    showNotification(type, title, message) {
        const icons = {
            success: '✓',
            error: '✗',
            warning: '⚠'
        };
        
        const notification = document.createElement('div');
        notification.className = `notification ${type}`;
        notification.innerHTML = `
            <div class="notification-icon">${icons[type]}</div>
            <div class="notification-content">
                <div class="notification-title">${title}</div>
                <div class="notification-message">${message}</div>
            </div>
            <button class="notification-close">×</button>
        `;
        
        document.body.appendChild(notification);
        
        // Auto-remove after 5 seconds
        setTimeout(() => {
            notification.remove();
        }, 5000);
        
        // Close button
        notification.querySelector('.notification-close').addEventListener('click', () => {
            notification.remove();
        });
    }
    
    showError(message) {
        const app = document.getElementById('app');
        app.innerHTML = `
            <div style="max-width: 600px; margin: 100px auto; padding: 20px; text-align: center;">
                <div style="background: #fee; border: 2px solid #c33; border-radius: 8px; padding: 30px; color: #c33;">
                    <h1 style="margin: 0 0 10px 0;">⚠️ Fehler</h1>
                    <p style="margin: 10px 0; color: #666;">${message}</p>
                </div>
            </div>
        `;
    }
    
    escapeHtml(text) {
        if (!text) return '';
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }
}

// Initialize editor when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    new Editor();
});
