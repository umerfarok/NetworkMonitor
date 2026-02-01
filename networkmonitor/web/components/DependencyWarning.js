import { useState, useEffect, useCallback } from 'react';
import React from 'react';

const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:5000';

const DependencyWarning = () => {
  const [dependencies, setDependencies] = useState({
    loading: true,
    ok: false,
    missing: [],
    warnings: []
  });
  const [expanded, setExpanded] = useState(false);

  const fetchDependencies = useCallback(async () => {
    try {
      const response = await fetch(`${API_BASE}/api/dependencies/check`);
      const data = await response.json();

      if (data.success) {
        setDependencies({
          loading: false,
          ok: data.data.dependencies_ok,
          missing: data.data.missing_dependencies || [],
          warnings: data.data.warnings || []
        });
      }
    } catch (error) {
      console.error('Failed to check dependencies:', error);
      setDependencies({
        loading: false,
        ok: false,
        missing: ['Unable to check dependencies'],
        warnings: []
      });
    }
  }, []);

  useEffect(() => {
    fetchDependencies();
  }, [fetchDependencies]);

  if (dependencies.loading) {
    return (
      <div style={styles.loading}>
        <div style={styles.spinner}></div>
        <p>Checking system dependencies...</p>
      </div>
    );
  }

  if (dependencies.ok && dependencies.warnings.length === 0) {
    return null;
  }

  return (
    <div style={styles.container}>
      <div style={styles.card}>
        <div style={styles.header}>
          <div style={styles.iconContainer}>
            <svg width="32" height="32" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
              <path d="M12 2L1 21h22L12 2zm0 3.516L20.297 19H3.703L12 5.516z" fill="#f57c00" />
              <path d="M11 10h2v5h-2zM11 16h2v2h-2z" fill="#f57c00" />
            </svg>
          </div>
          <div>
            <h2 style={styles.title}>System Requirements Issue</h2>
            <p style={styles.subtitle}>Some components need attention</p>
          </div>
        </div>

        {dependencies.missing.length > 0 && (
          <div style={styles.errorSection}>
            <h3 style={styles.sectionTitle}>
              <span style={{ ...styles.badge, background: '#ffebee', color: '#c62828' }}>
                Missing
              </span>
              Requirements
            </h3>
            <ul style={styles.list}>
              {dependencies.missing.map((dep, idx) => (
                <li key={idx} style={styles.listItem}>
                  <svg width="20" height="20" viewBox="0 0 24 24" fill="#c62828">
                    <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm1 15h-2v-2h2v2zm0-4h-2V7h2v6z" />
                  </svg>
                  {dep}
                </li>
              ))}
            </ul>
          </div>
        )}

        {dependencies.warnings.length > 0 && (
          <div style={styles.warningSection}>
            <h3 style={styles.sectionTitle}>
              <span style={{ ...styles.badge, background: '#fff3e0', color: '#ef6c00' }}>
                Warnings
              </span>
            </h3>
            <ul style={styles.list}>
              {dependencies.warnings.map((warning, idx) => (
                <li key={idx} style={styles.listItem}>
                  <svg width="20" height="20" viewBox="0 0 24 24" fill="#ef6c00">
                    <path d="M1 21h22L12 2 1 21zm12-3h-2v-2h2v2zm0-4h-2v-4h2v4z" />
                  </svg>
                  {warning}
                </li>
              ))}
            </ul>
          </div>
        )}

        <button
          style={styles.expandButton}
          onClick={() => setExpanded(!expanded)}
        >
          {expanded ? 'Hide' : 'Show'} Installation Guide
          <svg
            width="20"
            height="20"
            viewBox="0 0 24 24"
            fill="currentColor"
            style={{
              transform: expanded ? 'rotate(180deg)' : 'rotate(0)',
              transition: 'transform 0.3s ease'
            }}
          >
            <path d="M7.41 8.59L12 13.17l4.59-4.58L18 10l-6 6-6-6 1.41-1.41z" />
          </svg>
        </button>

        {expanded && (
          <div style={styles.guide}>
            <div style={styles.step}>
              <span style={styles.stepNumber}>1</span>
              <div>
                <h4>Install Npcap (Windows)</h4>
                <p>Download from <a href="https://npcap.com" target="_blank" rel="noopener noreferrer" style={styles.link}>npcap.com</a></p>
                <p style={styles.note}>Enable "WinPcap API-compatible Mode" during installation</p>
              </div>
            </div>

            <div style={styles.step}>
              <span style={styles.stepNumber}>2</span>
              <div>
                <h4>Run as Administrator</h4>
                <p>NetworkMonitor requires admin rights for network scanning</p>
              </div>
            </div>

            <div style={styles.step}>
              <span style={styles.stepNumber}>3</span>
              <div>
                <h4>Restart the Application</h4>
                <p>After installing dependencies, restart NetworkMonitor</p>
              </div>
            </div>
          </div>
        )}

        <button
          style={styles.retryButton}
          onClick={fetchDependencies}
        >
          <svg width="20" height="20" viewBox="0 0 24 24" fill="currentColor">
            <path d="M17.65 6.35A7.958 7.958 0 0012 4c-4.42 0-7.99 3.58-7.99 8s3.57 8 7.99 8c3.73 0 6.84-2.55 7.73-6h-2.08A5.99 5.99 0 0112 18c-3.31 0-6-2.69-6-6s2.69-6 6-6c1.66 0 3.14.69 4.22 1.78L13 11h7V4l-2.35 2.35z" />
          </svg>
          Check Again
        </button>
      </div>
    </div>
  );
};

const styles = {
  container: {
    padding: '24px',
    minHeight: '100vh',
    background: 'linear-gradient(135deg, #f5f7fa 0%, #e4e8eb 100%)',
    fontFamily: "'Inter', system-ui, sans-serif",
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center'
  },
  card: {
    background: 'white',
    borderRadius: '20px',
    padding: '32px',
    maxWidth: '600px',
    width: '100%',
    boxShadow: '0 20px 60px rgba(0,0,0,0.1)'
  },
  loading: {
    display: 'flex',
    flexDirection: 'column',
    alignItems: 'center',
    justifyContent: 'center',
    padding: '48px',
    fontFamily: 'system-ui, sans-serif'
  },
  spinner: {
    width: '32px',
    height: '32px',
    border: '3px solid #e0e0e0',
    borderTopColor: '#2196f3',
    borderRadius: '50%',
    animation: 'spin 1s linear infinite',
    marginBottom: '16px'
  },
  header: {
    display: 'flex',
    alignItems: 'center',
    gap: '16px',
    marginBottom: '24px'
  },
  iconContainer: {
    width: '56px',
    height: '56px',
    background: '#fff3e0',
    borderRadius: '16px',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center'
  },
  title: {
    fontSize: '20px',
    fontWeight: '700',
    color: '#1a1a2e',
    margin: '0 0 4px 0'
  },
  subtitle: {
    fontSize: '14px',
    color: '#666',
    margin: 0
  },
  sectionTitle: {
    fontSize: '14px',
    fontWeight: '600',
    color: '#1a1a2e',
    display: 'flex',
    alignItems: 'center',
    gap: '8px',
    marginBottom: '12px'
  },
  badge: {
    padding: '4px 10px',
    borderRadius: '6px',
    fontSize: '12px',
    fontWeight: '600'
  },
  errorSection: {
    background: '#fef7f7',
    borderRadius: '12px',
    padding: '16px',
    marginBottom: '16px'
  },
  warningSection: {
    background: '#fffaf5',
    borderRadius: '12px',
    padding: '16px',
    marginBottom: '16px'
  },
  list: {
    listStyle: 'none',
    padding: 0,
    margin: 0
  },
  listItem: {
    display: 'flex',
    alignItems: 'center',
    gap: '10px',
    padding: '8px 0',
    fontSize: '14px',
    color: '#333'
  },
  expandButton: {
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    gap: '8px',
    width: '100%',
    padding: '12px',
    background: '#f8f9fa',
    border: 'none',
    borderRadius: '10px',
    fontSize: '14px',
    fontWeight: '500',
    color: '#666',
    cursor: 'pointer',
    marginBottom: '16px',
    transition: 'all 0.2s ease'
  },
  guide: {
    background: '#f8f9fa',
    borderRadius: '12px',
    padding: '20px',
    marginBottom: '16px'
  },
  step: {
    display: 'flex',
    gap: '16px',
    marginBottom: '20px'
  },
  stepNumber: {
    width: '28px',
    height: '28px',
    background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
    color: 'white',
    borderRadius: '50%',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    fontWeight: '600',
    fontSize: '14px',
    flexShrink: 0
  },
  link: {
    color: '#2196f3',
    textDecoration: 'none'
  },
  note: {
    fontSize: '13px',
    color: '#888',
    fontStyle: 'italic',
    marginTop: '4px'
  },
  retryButton: {
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    gap: '8px',
    width: '100%',
    padding: '14px',
    background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
    border: 'none',
    borderRadius: '12px',
    fontSize: '15px',
    fontWeight: '600',
    color: 'white',
    cursor: 'pointer',
    transition: 'all 0.3s ease'
  }
};

export default DependencyWarning;