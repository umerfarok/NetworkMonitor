import { useState, useEffect } from 'react';
import {
  Alert,
  AlertTitle,
  Box,
  Button,
  Card,
  CardContent,
  Chip,
  Collapse,
  Divider,
  Link,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  Paper,
  Stack,
  Switch,
  Typography,
  IconButton,
  useMediaQuery,
  useTheme,
} from '@mui/material';
import {
  ErrorOutline as ErrorIcon,
  Close as CloseIcon,
  Warning as WarningIcon,
  Info as InfoIcon,
  Check as CheckIcon,
  Download as DownloadIcon,
  ArrowRight as ArrowRightIcon,
  Refresh as RefreshIcon,
  Settings as SettingsIcon,
  BugReport as BugIcon,
  LightbulbOutlined as TipIcon,
  AdminPanelSettings as AdminIcon,
} from '@mui/icons-material';
import { motion, AnimatePresence } from 'framer-motion';
import React from 'react';

const DependencyWarning = ({ missingDependencies }) => {
  if (!missingDependencies || missingDependencies.length === 0) {
    return null;
  }

  return (
    <div className="rounded-md bg-yellow-50 p-4 mb-4">
      <div className="flex">
        <div className="flex-shrink-0">
          <svg className="h-5 w-5 text-yellow-400" viewBox="0 0 20 20" fill="currentColor">
            <path fillRule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clipRule="evenodd" />
          </svg>
        </div>
        <div className="ml-3">
          <h3 className="text-sm font-medium text-yellow-800">
            Missing Dependencies Detected
          </h3>
          <div className="mt-2 text-sm text-yellow-700">
            <p>
              The following dependencies need to be installed for NetworkMonitor to function properly:
            </p>
            <ul className="list-disc list-inside mt-2">
              {missingDependencies.map((dep, index) => (
                <li key={index} className="ml-4">{dep}</li>
              ))}
            </ul>
            <div className="mt-4 p-4 bg-white rounded border border-yellow-200">
              <h4 className="font-medium mb-2">Installation Instructions:</h4>
              <ol className="list-decimal list-inside space-y-2">
                {missingDependencies.includes('Python 3.9+') && (
                  <li className="ml-4">
                    Install Python 3.9 or later:
                    <ul className="list-disc list-inside ml-8 mt-1">
                      <li>Download from <a href="https://python.org" className="text-blue-600 hover:underline" target="_blank" rel="noopener noreferrer">python.org</a></li>
                      <li>During installation, check "Add Python to PATH"</li>
                    </ul>
                  </li>
                )}
                {missingDependencies.includes('Npcap') && (
                  <li className="ml-4">
                    Install Npcap:
                    <ul className="list-disc list-inside ml-8 mt-1">
                      <li>Download from <a href="https://npcap.com" className="text-blue-600 hover:underline" target="_blank" rel="noopener noreferrer">npcap.com</a></li>
                      <li>Run installer as administrator</li>
                      <li>Select "Install Npcap in WinPcap API-compatible Mode"</li>
                    </ul>
                  </li>
                )}
                {missingDependencies.includes('Python packages') && (
                  <li className="ml-4">
                    Install Python packages:
                    <ul className="list-disc list-inside ml-8 mt-1">
                      <li>Open Command Prompt as administrator</li>
                      <li>Run: <code className="bg-gray-100 px-2 py-1">pip install -r "C:\Program Files\NetworkMonitor\requirements.txt"</code></li>
                    </ul>
                  </li>
                )}
              </ol>
            </div>
            <p className="mt-4">
              After installing the dependencies, restart NetworkMonitor.
              If you continue to see this warning, check the troubleshooting guide in the documentation.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default DependencyWarning;