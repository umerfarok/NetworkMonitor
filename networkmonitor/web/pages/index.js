import React, { useState, useEffect } from 'react';
import Head from 'next/head';
import NetworkDashboard from '../components/NetworkDashboard';
import DependencyWarning from '../components/DependencyWarning';

export default function Home() {
  const [status, setStatus] = useState({
    loading: true,
    serverRunning: false,
    dependenciesOk: false,
    error: null
  });

  useEffect(() => {
    checkServerStatus();
  }, []);

  const checkServerStatus = async () => {
    try {
      const response = await fetch('http://localhost:5000/api/status');
      const data = await response.json();
      
      if (data.success) {
        setStatus({
          loading: false,
          serverRunning: true,
          dependenciesOk: data.data.dependencies_ok,
          error: null
        });
      } else {
        setStatus({
          loading: false,
          serverRunning: false,
          dependenciesOk: false,
          error: data.error || "Failed to connect to server"
        });
      }
    } catch (error) {
      setStatus({
        loading: false,
        serverRunning: false,
        dependenciesOk: false,
        error: "Could not connect to server"
      });
    }
  };

  if (status.loading) {
    return (
      <div className="loading-container">
        <div className="loading-spinner"></div>
        <p>Connecting to Network Monitor service...</p>
        <style jsx>{`
          .loading-container {
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            height: 100vh;
            font-family: system-ui, sans-serif;
          }
          .loading-spinner {
            border: 4px solid rgba(0, 0, 0, 0.1);
            width: 36px;
            height: 36px;
            border-radius: 50%;
            border-left-color: #09f;
            animation: spin 1s linear infinite;
            margin-bottom: 20px;
          }
          @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
          }
        `}</style>
      </div>
    );
  }

  if (!status.serverRunning) {
    return (
      <div className="error-container">
        <h1>Cannot Connect to Network Monitor</h1>
        <p>The Network Monitor service is not running or cannot be reached.</p>
        <p className="error-message">Error: {status.error}</p>
        <button onClick={checkServerStatus} className="retry-button">
          Retry Connection
        </button>
        <style jsx>{`
          .error-container {
            max-width: 600px;
            margin: 100px auto;
            padding: 20px;
            text-align: center;
            font-family: system-ui, sans-serif;
          }
          .error-message {
            color: #d32f2f;
            background: #ffebee;
            padding: 10px;
            border-radius: 4px;
            margin: 20px 0;
          }
          .retry-button {
            background: #2196f3;
            color: white;
            border: none;
            padding: 10px 20px;
            border-radius: 4px;
            font-size: 16px;
            cursor: pointer;
          }
          .retry-button:hover {
            background: #1976d2;
          }
        `}</style>
      </div>
    );
  }

  return (
    <div>
      <Head>
        <title>Network Monitor Dashboard</title>
        <meta name="description" content="Network monitoring and control dashboard" />
        <link rel="icon" href="/favicon.ico" />
      </Head>

      <main>
        {/* If dependencies are not OK, show the dependency warning */}
        {!status.dependenciesOk && <DependencyWarning />}
        
        {/* Only show the dashboard if dependencies are OK */}
        {status.dependenciesOk && <NetworkDashboard />}
      </main>
    </div>
  );
}