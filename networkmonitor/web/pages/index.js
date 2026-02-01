import React, { useState, useEffect, useCallback } from 'react';
import Head from 'next/head';
import NetworkDashboard from '../components/NetworkDashboard';
import DependencyWarning from '../components/DependencyWarning';

const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:5000';

export default function Home() {
  const [status, setStatus] = useState({
    loading: true,
    serverRunning: false,
    dependenciesOk: false,
    error: null,
    retryCount: 0,
    autoRetrying: true
  });

  const checkServerStatus = useCallback(async () => {
    try {
      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), 5000);

      const response = await fetch(`${API_BASE}/api/status`, {
        signal: controller.signal
      });
      clearTimeout(timeoutId);

      const data = await response.json();

      if (data.success) {
        setStatus({
          loading: false,
          serverRunning: true,
          dependenciesOk: data.data.dependencies_ok,
          error: null,
          retryCount: 0,
          autoRetrying: false
        });
      } else {
        setStatus(prev => ({
          loading: false,
          serverRunning: false,
          dependenciesOk: false,
          error: data.error || "Failed to connect to server",
          retryCount: prev.retryCount + 1,
          autoRetrying: prev.retryCount < 5
        }));
      }
    } catch (error) {
      setStatus(prev => ({
        loading: false,
        serverRunning: false,
        dependenciesOk: false,
        error: error.name === 'AbortError' ? "Connection timed out" : "Could not connect to server",
        retryCount: prev.retryCount + 1,
        autoRetrying: prev.retryCount < 5
      }));
    }
  }, []);

  useEffect(() => {
    checkServerStatus();
  }, [checkServerStatus]);

  // Auto-retry logic
  useEffect(() => {
    let timer;
    if (!status.serverRunning && status.autoRetrying && !status.loading) {
      timer = setTimeout(() => {
        checkServerStatus();
      }, 3000); // Retry every 3 seconds
    }
    return () => clearTimeout(timer);
  }, [status.serverRunning, status.autoRetrying, status.loading, checkServerStatus]);

  if (status.loading) {
    return (
      <>
        <Head>
          <title>Network Monitor - Connecting...</title>
        </Head>
        <div className="loading-container">
          <div className="logo-container">
            <svg width="80" height="80" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
              <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm0 18c-4.42 0-8-3.58-8-8s3.58-8 8-8 8 3.58 8 8-3.58 8-8 8z" fill="#2196f3" />
              <circle cx="12" cy="12" r="4" fill="#2196f3" />
              <path d="M12 6v2M12 16v2M6 12h2M16 12h2" stroke="#2196f3" strokeWidth="2" strokeLinecap="round" />
            </svg>
          </div>
          <div className="loading-spinner"></div>
          <h2>Network Monitor</h2>
          <p>Connecting to local service...</p>
          <style jsx>{`
            .loading-container {
              display: flex;
              flex-direction: column;
              align-items: center;
              justify-content: center;
              height: 100vh;
              font-family: 'Inter', system-ui, sans-serif;
              background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
              color: white;
            }
            .logo-container {
              margin-bottom: 30px;
              padding: 20px;
              background: rgba(255, 255, 255, 0.1);
              border-radius: 50%;
              backdrop-filter: blur(10px);
            }
            .loading-spinner {
              border: 4px solid rgba(255, 255, 255, 0.3);
              width: 40px;
              height: 40px;
              border-radius: 50%;
              border-left-color: white;
              animation: spin 1s linear infinite;
              margin-bottom: 20px;
            }
            h2 {
              font-size: 24px;
              font-weight: 700;
              margin-bottom: 10px;
            }
            p {
              font-size: 16px;
              opacity: 0.8;
            }
            @keyframes spin {
              0% { transform: rotate(0deg); }
              100% { transform: rotate(360deg); }
            }
          `}</style>
        </div>
      </>
    );
  }

  if (!status.serverRunning) {
    return (
      <>
        <Head>
          <title>Network Monitor - Not Connected</title>
        </Head>
        <div className="error-container">
          <div className="error-card">
            <div className="icon-container warning">
              <svg width="48" height="48" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm1 15h-2v-2h2v2zm0-4h-2V7h2v6z" fill="#f57c00" />
              </svg>
            </div>
            <h1>Network Monitor Service Not Running</h1>
            <p className="subtitle">Start the local service to use the dashboard</p>

            <div className="error-box">
              <strong>Error:</strong> {status.error}
            </div>

            <div className="instructions">
              <h3>How to Start the Service</h3>
              <div className="step">
                <span className="step-number">1</span>
                <div>
                  <strong>Run as Administrator</strong>
                  <p>Right-click on <code>NetworkMonitor.exe</code> and select "Run as administrator"</p>
                </div>
              </div>
              <div className="step">
                <span className="step-number">2</span>
                <div>
                  <strong>Or use the Command Line</strong>
                  <p><code>python -m networkmonitor</code></p>
                </div>
              </div>
            </div>

            <div className="button-group">
              {status.autoRetrying ? (
                <div className="auto-retry">
                  <div className="mini-spinner"></div>
                  <span>Auto-retrying... (attempt {status.retryCount}/5)</span>
                </div>
              ) : (
                <button onClick={() => {
                  setStatus(prev => ({ ...prev, autoRetrying: true, retryCount: 0 }));
                  checkServerStatus();
                }} className="retry-button">
                  <svg width="20" height="20" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                    <path d="M17.65 6.35A7.958 7.958 0 0012 4c-4.42 0-7.99 3.58-7.99 8s3.57 8 7.99 8c3.73 0 6.84-2.55 7.73-6h-2.08A5.99 5.99 0 0112 18c-3.31 0-6-2.69-6-6s2.69-6 6-6c1.66 0 3.14.69 4.22 1.78L13 11h7V4l-2.35 2.35z" fill="currentColor" />
                  </svg>
                  Retry Connection
                </button>
              )}
            </div>
          </div>

          <style jsx>{`
            .error-container {
              min-height: 100vh;
              display: flex;
              align-items: center;
              justify-content: center;
              font-family: 'Inter', system-ui, sans-serif;
              background: linear-gradient(135deg, #f5f7fa 0%, #e4e8eb 100%);
              padding: 20px;
            }
            .error-card {
              background: white;
              border-radius: 20px;
              padding: 40px;
              max-width: 550px;
              width: 100%;
              box-shadow: 0 20px 60px rgba(0, 0, 0, 0.1);
              text-align: center;
            }
            .icon-container {
              width: 80px;
              height: 80px;
              border-radius: 50%;
              display: flex;
              align-items: center;
              justify-content: center;
              margin: 0 auto 24px;
            }
            .icon-container.warning {
              background: #fff3e0;
            }
            h1 {
              font-size: 24px;
              font-weight: 700;
              color: #1a1a2e;
              margin-bottom: 8px;
            }
            .subtitle {
              color: #666;
              margin-bottom: 24px;
            }
            .error-box {
              background: #ffebee;
              color: #c62828;
              padding: 12px 16px;
              border-radius: 8px;
              margin-bottom: 24px;
              font-size: 14px;
              text-align: left;
            }
            .instructions {
              text-align: left;
              background: #f8f9fa;
              border-radius: 12px;
              padding: 20px;
              margin-bottom: 24px;
            }
            .instructions h3 {
              font-size: 16px;
              font-weight: 600;
              margin-bottom: 16px;
              color: #1a1a2e;
            }
            .step {
              display: flex;
              gap: 16px;
              margin-bottom: 16px;
            }
            .step:last-child {
              margin-bottom: 0;
            }
            .step-number {
              width: 28px;
              height: 28px;
              background: #2196f3;
              color: white;
              border-radius: 50%;
              display: flex;
              align-items: center;
              justify-content: center;
              font-weight: 600;
              font-size: 14px;
              flex-shrink: 0;
            }
            .step strong {
              display: block;
              margin-bottom: 4px;
              color: #1a1a2e;
            }
            .step p {
              margin: 0;
              color: #666;
              font-size: 14px;
            }
            .step code {
              background: #e3f2fd;
              color: #1565c0;
              padding: 2px 8px;
              border-radius: 4px;
              font-family: 'Fira Code', monospace;
              font-size: 13px;
            }
            .button-group {
              display: flex;
              justify-content: center;
            }
            .retry-button {
              display: flex;
              align-items: center;
              gap: 8px;
              background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
              color: white;
              border: none;
              padding: 14px 28px;
              border-radius: 12px;
              font-size: 16px;
              font-weight: 600;
              cursor: pointer;
              transition: all 0.3s ease;
            }
            .retry-button:hover {
              transform: translateY(-2px);
              box-shadow: 0 8px 24px rgba(102, 126, 234, 0.4);
            }
            .auto-retry {
              display: flex;
              align-items: center;
              gap: 12px;
              color: #666;
              font-size: 14px;
            }
            .mini-spinner {
              width: 20px;
              height: 20px;
              border: 2px solid #e0e0e0;
              border-left-color: #2196f3;
              border-radius: 50%;
              animation: spin 1s linear infinite;
            }
            @keyframes spin {
              0% { transform: rotate(0deg); }
              100% { transform: rotate(360deg); }
            }
          `}</style>
        </div>
      </>
    );
  }

  return (
    <div>
      <Head>
        <title>Network Monitor Dashboard</title>
        <meta name="description" content="Control and monitor your network devices with ease" />
        <link rel="icon" href="/favicon.ico" />
        <link rel="preconnect" href="https://fonts.googleapis.com" />
        <link rel="preconnect" href="https://fonts.gstatic.com" crossOrigin="anonymous" />
        <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet" />
      </Head>

      <main>
        {!status.dependenciesOk && <DependencyWarning />}
        {status.dependenciesOk && <NetworkDashboard />}
      </main>
    </div>
  );
}