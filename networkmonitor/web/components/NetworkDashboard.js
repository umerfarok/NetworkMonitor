import React, { useState, useEffect } from 'react';
import { DndProvider, useDrag, useDrop } from 'react-dnd';
import { HTML5Backend } from 'react-dnd-html5-backend';
import {
  Box,
  Card,
  CardContent,
  Typography,
  Grid,
  Select,
  MenuItem,
  Button,
  Slider,
  LinearProgress,
  Alert,
  IconButton,
  Paper,
  Divider,
  FormControl,
  InputLabel,
  TextField,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Snackbar,
  useTheme,
  ThemeProvider,
  createTheme,
  CssBaseline,
  Chip,
  Tooltip,
  Badge,
} from '@mui/material';
import {
  Wifi as WifiIcon,
  WifiOff as WifiOffIcon,
  Speed as SpeedIcon,
  Block as BlockIcon,
  Edit as EditIcon,
  Refresh as RefreshIcon,
  DragIndicator as DragIndicatorIcon,
  Security as SecurityIcon,
  GppBad as GppBadIcon,
  RestartAlt as RestartAltIcon,
  Visibility as VisibilityIcon,
} from '@mui/icons-material';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip as RechartsTooltip, Legend, ResponsiveContainer } from 'recharts';
import { motion, AnimatePresence } from 'framer-motion';

const theme = createTheme({
  palette: {
    primary: {
      main: '#2196f3',
    },
    secondary: {
      main: '#f50057',
    },
    success: {
      main: '#4caf50',
    },
    warning: {
      main: '#ff9800',
    },
    error: {
      main: '#f44336',
    },
    background: {
      default: '#f5f5f5',
      paper: '#ffffff',
    },
  },
  typography: {
    fontFamily: 'Roboto, Arial, sans-serif',
  },
  components: {
    MuiCard: {
      styleOverrides: {
        root: {
          borderRadius: 16,
          boxShadow: '0 4px 6px rgba(0, 0, 0, 0.1)',
        },
      },
    },
    MuiChip: {
      styleOverrides: {
        root: {
          borderRadius: 8,
        },
      },
    },
  },
});

const DeviceCard = ({
  device,
  onLimitChange,
  onBlock,
  onRename,
  onProtect,
  onUnprotect,
  onCut,
  onRestore,
}) => {
  const [{ isDragging }, drag] = useDrag(() => ({
    type: 'device',
    item: { id: device.ip, device },
    collect: (monitor) => ({
      isDragging: monitor.isDragging(),
    }),
  }));

  const [dialogOpen, setDialogOpen] = useState(false);
  const [newName, setNewName] = useState(device.hostname || '');

  const handleRename = () => {
    onRename(device.ip, newName);
    setDialogOpen(false);
  };
  

  const getStatusColor = () => {
    if (device.attack_status === 'cutting') return 'error';
    if (device.is_protected) return 'success';
    return device.status === 'active' ? 'primary' : 'disabled';
  };

  const getStatusChip = () => {
    if (device.attack_status === 'cutting') {
      return <Chip size="small" color="error" label="Network Cut" />;
    }
    if (device.is_protected) {
      return <Chip size="small" color="success" label="Protected" icon={<SecurityIcon />} />;
    }
    return device.status === 'active' ? (
      <Chip size="small" color="primary" label="Active" />
    ) : (
      <Chip size="small" color="default" label="Inactive" />
    );
  };

  return (
    <motion.div
      ref={drag}
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: -20 }}
      transition={{ duration: 0.3 }}
      style={{ opacity: isDragging ? 0.5 : 1, cursor: 'move' }}
    >
      <Card
        sx={{
          mb: 2,
          bgcolor: 'background.paper',
          '&:hover': { boxShadow: 6 },
          transition: 'all 0.3s',
          position: 'relative',
          overflow: 'visible',
        }}
      >
        <CardContent>
          <Grid container spacing={2} alignItems="center">
            <Grid item>
              <DragIndicatorIcon color="action" />
            </Grid>
            <Grid item>
              <Badge
                color={getStatusColor()}
                variant="dot"
                anchorOrigin={{
                  vertical: 'bottom',
                  horizontal: 'right',
                }}
              >
                {device.status === 'active' ? (
                  <WifiIcon color="primary" />
                ) : (
                  <WifiOffIcon color="error" />
                )}
              </Badge>
            </Grid>
            <Grid item xs>
              <Typography variant="h6">
                {device.hostname || device.ip}
                {getStatusChip()}
              </Typography>
              <Typography variant="body2" color="textSecondary">
                MAC: {device.mac}
              </Typography>
              {device.vendor && (
                <Typography variant="body2" color="textSecondary">
                  Vendor: {device.vendor}
                </Typography>
              )}
            </Grid>
            <Grid item xs={12} md={4}>
              <Typography variant="body2" gutterBottom>
                Current Speed: {device.current_speed?.toFixed(1)} Mbps
              </Typography>
              <LinearProgress
                variant="determinate"
                value={(device.current_speed / (device.speed_limit || 100)) * 100}
                sx={{ mb: 1, height: 8, borderRadius: 4 }}
              />
              <Grid container spacing={1} alignItems="center">
                <Grid item xs>
                  <Slider
                    value={device.speed_limit || 0}
                    onChange={(_, value) => onLimitChange(device.ip, value)}
                    min={0}
                    max={100}
                    valueLabelDisplay="auto"
                    valueLabelFormat={(value) => `${value} Mbps`}
                  />
                </Grid>
                <Grid item>
                  <Tooltip title={device.is_protected ? "Unprotect Device" : "Protect Device"}>
                    <IconButton
                      size="small"
                      onClick={() => device.is_protected ? onUnprotect(device.ip) : onProtect(device.ip)}
                      color={device.is_protected ? "success" : "default"}
                    >
                      <SecurityIcon />
                    </IconButton>
                  </Tooltip>
                  <Tooltip title={device.attack_status === 'cutting' ? "Restore Network" : "Cut Network"}>
                    <IconButton
                      size="small"
                      onClick={() => device.attack_status === 'cutting' ? onRestore(device.ip) : onCut(device.ip)}
                      color={device.attack_status === 'cutting' ? "error" : "default"}
                      disabled={device.is_protected}
                    >
                      {device.attack_status === 'cutting' ? <RestartAltIcon /> : <BlockIcon />}
                    </IconButton>
                  </Tooltip>
                  <Tooltip title="Rename Device">
                    <IconButton
                      size="small"
                      onClick={() => setDialogOpen(true)}
                      color="primary"
                    >
                      <EditIcon />
                    </IconButton>
                  </Tooltip>
                </Grid>
              </Grid>
            </Grid>
          </Grid>
        </CardContent>

        {/* Rename Dialog */}
        <Dialog open={dialogOpen} onClose={() => setDialogOpen(false)}>
          <DialogTitle>Rename Device</DialogTitle>
          <DialogContent>
            <TextField
              autoFocus
              margin="dense"
              label="New Name"
              fullWidth
              value={newName}
              onChange={(e) => setNewName(e.target.value)}
            />
          </DialogContent>
          <DialogActions>
            <Button onClick={() => setDialogOpen(false)}>Cancel</Button>
            <Button onClick={handleRename} color="primary">Rename</Button>
          </DialogActions>
        </Dialog>
      </Card>
    </motion.div>
  );
};

const SpeedGroup = ({ title, devices, onDrop, ...deviceActions }) => {
  const [{ isOver }, drop] = useDrop(() => ({
    accept: 'device',
    drop: (item) => onDrop(item.device, title),
    collect: (monitor) => ({
      isOver: monitor.isOver(),
    }),
  }));

  return (
    <Paper
      ref={drop}
      sx={{
        p: 2,
        minHeight: 200,
        bgcolor: isOver ? 'action.hover' : 'background.paper',
        transition: 'background-color 0.2s',
        borderRadius: 2,
        position: 'relative',
      }}
    >
      <Typography variant="h6" gutterBottom color="primary">
        {title}
        <Chip
          label={`${devices.length} devices`}
          size="small"
          sx={{ ml: 1 }}
        />
      </Typography>
      <Divider sx={{ mb: 2 }} />
      <AnimatePresence>
        {devices.map((device) => (
          <DeviceCard
            key={device.ip}
            device={device}
            {...deviceActions}
          />
        ))}
      </AnimatePresence>
    </Paper>
  );
};

const NetworkDashboard = () => {
  const [interfaces, setInterfaces] = useState([]);
  const [selectedInterface, setSelectedInterface] = useState('');
  const [devices, setDevices] = useState([]);
  const [stats, setStats] = useState({});
  const [notification, setNotification] = useState({ open: false, message: '', severity: 'info' });
  const [speedGroups, setSpeedGroups] = useState({
    unlimited: [],
    limited: [],
  });
  const [chartData, setChartData] = useState([]);
  const [gatewayInfo, setGatewayInfo] = useState(null);

  useEffect(() => {
    fetchInterfaces();
    fetchStatus();
    fetchGatewayInfo();
    const interval = setInterval(() => {
      fetchStats();
      fetchDevices();
      fetchGatewayInfo();
    }, 5000);
    return () => clearInterval(interval);
  }, [selectedInterface]);

  const fetchGatewayInfo = async () => {
    try {
      const response = await fetch('http://localhost:5000/api/network/gateway');
      const data = await response.json();
      if (data.success) {
        setGatewayInfo(data.data);
      }
    } catch (error) {
      console.error('Failed to fetch gateway info:', error);
    }
  };
  const handleSpeedLimit = async (ip, limit) => {
    try {
      const response = await fetch('http://localhost:5000/api/device/limit', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ ip, limit }),
      });
      const data = await response.json();
      if (data.success) {
        showNotification(`Speed limit set to ${limit} Mbps for ${ip}`, 'success');
        fetchDevices(); // Refresh device list
      } else {
        showNotification(data.error || 'Failed to set speed limit', 'error');
      }
    } catch (error) {
      console.error('Error setting speed limit:', error);
      showNotification('Failed to set speed limit', 'error');
    }
  };
  // Add these methods in the NetworkDashboard component

const handleRenameDevice = async (ip, newName) => {
  try {
    const response = await fetch('http://localhost:5000/api/device/rename', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ ip, name: newName }),
    });
    const data = await response.json();
    if (data.success) {
      showNotification(`Device renamed to ${newName}`, 'success');
      fetchDevices();
    } else {
      showNotification(data.error || 'Failed to rename device', 'error');
    }
  } catch (error) {
    console.error('Error renaming device:', error);
    showNotification('Failed to rename device', 'error');
  }
};

const handleDeviceDrop = async (device, group) => {
  try {
    if (group === 'limited' && !device.speed_limit) {
      // Set a default speed limit when moving to limited group
      await handleSpeedLimit(device.ip, 10); // Default 10 Mbps limit
    } else if (group === 'unlimited' && device.speed_limit) {
      // Remove speed limit when moving to unlimited group
      await handleSpeedLimit(device.ip, 0);
    }
    showNotification(`Device moved to ${group} group`, 'success');
    fetchDevices();
  } catch (error) {
    console.error('Error handling device drop:', error);
    showNotification('Failed to move device', 'error');
  }
};

const fetchStatus = async () => {
  try {
    const response = await fetch('http://localhost:5000/api/status');
    const data = await response.json();
    if (data.success) {
      // You can add state management for server status if needed
      console.log('Server status:', data.data);
    }
  } catch (error) {
    showNotification('Failed to fetch server status', 'error');
  }
};
  const fetchInterfaces = async () => {
    try {
      const response = await fetch('http://localhost:5000/api/wifi/interfaces');
      const data = await response.json();
      if (data.success) {
        setInterfaces(data.data);
        if (data.data.length > 0 && !selectedInterface) {
          setSelectedInterface(data.data[0]);
        }
      }
    } catch (error) {
      showNotification('Failed to fetch interfaces', 'error');
    }
  };
  const handleProtectDevice = async (ip) => {
    try {
      const response = await fetch('http://localhost:5000/api/device/protect', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ ip }),
      });
      const data = await response.json();
      if (data.success) {
        showNotification(`Device ${ip} protected`, 'success');
        fetchDevices();
      }
    } catch (error) {
      showNotification('Failed to protect device', 'error');
    }
  };
  const fetchDevices = async () => {
    if (!selectedInterface) return;
    try {
      const response = await fetch(`http://localhost:5000/api/devices?interface=${selectedInterface}`);
      const data = await response.json();
      if (data.success) {
        setDevices(data.data);
        updateSpeedGroups(data.data);
      }
    } catch (error) {
      showNotification('Failed to fetch devices', 'error');
    }
  };

  const fetchStats = async () => {
    try {
      const response = await fetch('http://localhost:5000/api/stats/bandwidth');
      const data = await response.json();
      if (data.success) {
        setStats(data.data);
        updateChartData(data.data);
      }
    } catch (error) {
      console.error('Failed to fetch stats:', error);
    }
  };

  const updateSpeedGroups = (devices) => {
    setSpeedGroups({
      unlimited: devices.filter(d => !d.speed_limit),
      limited: devices.filter(d => d.speed_limit)
    });
  };

  const updateChartData = (newStats) => {
    setChartData(prevData => {
      const newData = [
        ...prevData,
        {
          time: new Date().toLocaleTimeString(),
          upload: Object.values(newStats).reduce((sum, device) => sum + (device.current_speed?.upload || 0), 0),
          download: Object.values(newStats).reduce((sum, device) => sum + (device.current_speed?.download || 0), 0),
        }
      ].slice(-10);
      return newData;
    });
  };


  const handleUnprotectDevice = async (ip) => {
    try {
      const response = await fetch('http://localhost:5000/api/device/unprotect', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ ip }),
      });
      const data = await response.json();
      if (data.success) {
        showNotification(`Device ${ip} unprotected`, 'success');
        fetchDevices();
      }
    } catch (error) {
      showNotification('Failed to unprotect device', 'error');
    }
  };

  const handleCutDevice = async (ip) => {
    try {
      const response = await fetch('http://localhost:5000/api/device/cut', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ ip }),
      });
      const data = await response.json();
      if (data.success) {
        showNotification(`Network cut initiated for ${ip}`, 'warning');
        fetchDevices();
      }
    } catch (error) {
      showNotification('Failed to cut device network', 'error');
    }
  };

  const handleRestoreDevice = async (ip) => {
    try {
      const response = await fetch('http://localhost:5000/api/device/restore', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ ip }),
      });
      const data = await response.json();
      if (data.success) {
        showNotification(`Network restored for ${ip}`, 'success');
        fetchDevices();
      }
    } catch (error) {
      showNotification('Failed to restore device network', 'error');
    }
  };
  const showNotification = (message, severity) => {
    setNotification({ open: true, message, severity });
  };

  const formatBytes = (bytes) => {
    if (bytes === 0) return '0 B';
    const k = 1024;
    const sizes = ['B', 'KB', 'MB', 'GB', 'TB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };
  // ... (rest of the previous methods remain the same)

  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <DndProvider backend={HTML5Backend}>
        <Box sx={{ p: 3 }}>
          <Grid container spacing={3}>
            {/* Gateway Info Card */}
            <Grid item xs={12}>
              <Card>
                <CardContent>
                  <Typography variant="h6" gutterBottom>
                    Network Gateway
                  </Typography>
                  <Grid container spacing={2}>
                    <Grid item xs={12} md={6}>
                      <Typography variant="body2" color="textSecondary">
                        IP Address: {gatewayInfo?.ip || 'N/A'}
                      </Typography>
                    </Grid>
                    <Grid item xs={12} md={6}>
                      <Typography variant="body2" color="textSecondary">
                        MAC Address: {gatewayInfo?.mac || 'N/A'}
                      </Typography>
                    </Grid>
                  </Grid>
                </CardContent>
              </Card>
            </Grid>

            {/* ... (rest of the existing components) */}

            {/* Device Groups with new actions */}
            <Grid item xs={12} md={6}>
              <SpeedGroup
                title="Unlimited Speed Devices"
                devices={speedGroups.unlimited}
                onDrop={(device) => handleDeviceDrop(device, 'unlimited')}
                onLimitChange={handleSpeedLimit}
                onProtect={handleProtectDevice}
                onUnprotect={handleUnprotectDevice}
                onCut={handleCutDevice}
                onRestore={handleRestoreDevice}
                onRename={handleRenameDevice}
              />
            </Grid>
            <Grid item xs={12} md={6}>
              <SpeedGroup
                title="Limited Speed Devices"
                devices={speedGroups.limited}
                onDrop={(device) => handleDeviceDrop(device, 'limited')}
                onLimitChange={handleSpeedLimit}
                onProtect={handleProtectDevice}
                onUnprotect={handleUnprotectDevice}
                onCut={handleCutDevice}
                onRestore={handleRestoreDevice}
                onRename={handleRenameDevice}
              />
            </Grid>

            {/* Network Statistics Card */}
            <Grid item xs={12}>
              <Card>
                <CardContent>
                  <Typography variant="h6" gutterBottom>
                    Network Statistics
                  </Typography>
                  <Grid container spacing={3}>
                    <Grid item xs={12} md={3}>
                      <Paper sx={{ p: 2, textAlign: 'center', bgcolor: 'primary.light', color: 'white' }}>
                        <Typography variant="h6">
                          {devices.length}
                        </Typography>
                        <Typography variant="body2">
                          Total Devices
                        </Typography>
                      </Paper>
                    </Grid>
                    <Grid item xs={12} md={3}>
                      <Paper sx={{ p: 2, textAlign: 'center', bgcolor: 'success.light', color: 'white' }}>
                        <Typography variant="h6">
                          {devices.filter(d => d.status === 'active').length}
                        </Typography>
                        <Typography variant="body2">
                          Active Devices
                        </Typography>
                      </Paper>
                    </Grid>
                    <Grid item xs={12} md={3}>
                      <Paper sx={{ p: 2, textAlign: 'center', bgcolor: 'warning.light', color: 'white' }}>
                        <Typography variant="h6">
                          {devices.filter(d => d.speed_limit).length}
                        </Typography>
                        <Typography variant="body2">
                          Limited Devices
                        </Typography>
                      </Paper>
                    </Grid>
                    <Grid item xs={12} md={3}>
                      <Paper sx={{ p: 2, textAlign: 'center', bgcolor: 'error.light', color: 'white' }}>
                        <Typography variant="h6">
                          {devices.filter(d => d.attack_status === 'cutting').length}
                        </Typography>
                        <Typography variant="body2">
                          Cut Devices
                        </Typography>
                      </Paper>
                    </Grid>
                  </Grid>
                </CardContent>
              </Card>
            </Grid>

            {/* Bandwidth Chart */}
            <Grid item xs={12}>
              <Card>
                <CardContent>
                  <Typography variant="h6" gutterBottom>
                    Network Bandwidth Usage
                    <Tooltip title="Real-time bandwidth monitoring">
                      <IconButton size="small" sx={{ ml: 1 }}>
                        <VisibilityIcon />
                      </IconButton>
                    </Tooltip>
                  </Typography>
                  <Box sx={{ width: '100%', height: 300 }}>
                    <ResponsiveContainer>
                      <LineChart data={chartData}>
                        <CartesianGrid strokeDasharray="3 3" />
                        <XAxis
                          dataKey="time"
                          tick={{ fontSize: 12 }}
                          interval="preserveStartEnd"
                        />
                        <YAxis
                          tick={{ fontSize: 12 }}
                          label={{
                            value: 'Speed (Mbps)',
                            angle: -90,
                            position: 'insideLeft',
                            style: { fontSize: 12 }
                          }}
                        />
                        <RechartsTooltip
                          contentStyle={{
                            backgroundColor: 'rgba(255, 255, 255, 0.9)',
                            border: 'none',
                            borderRadius: 8,
                            boxShadow: '0 2px 4px rgba(0,0,0,0.1)'
                          }}
                        />
                        <Legend />
                        <Line
                          type="monotone"
                          dataKey="upload"
                          stroke={theme.palette.primary.main}
                          strokeWidth={2}
                          dot={false}
                          activeDot={{ r: 6 }}
                          name="Upload"
                        />
                        <Line
                          type="monotone"
                          dataKey="download"
                          stroke={theme.palette.secondary.main}
                          strokeWidth={2}
                          dot={false}
                          activeDot={{ r: 6 }}
                          name="Download"
                        />
                      </LineChart>
                    </ResponsiveContainer>
                  </Box>
                </CardContent>
              </Card>
            </Grid>

            {/* Floating Action Button */}
            <Box sx={{ position: 'fixed', bottom: 20, right: 20 }}>
              <motion.div
                whileHover={{ scale: 1.1 }}
                whileTap={{ scale: 0.9 }}
              >
                <Button
                  variant="contained"
                  color="primary"
                  startIcon={<RefreshIcon />}
                  onClick={() => {
                    fetchDevices();
                    fetchStats();
                    fetchGatewayInfo();
                  }}
                  sx={{
                    borderRadius: 28,
                    boxShadow: 3,
                    '&:hover': {
                      boxShadow: 6
                    }
                  }}
                >
                  Refresh
                </Button>
              </motion.div>
            </Box>

            {/* Notifications */}
            <Snackbar
              open={notification.open}
              autoHideDuration={4000}
              onClose={() => setNotification({ ...notification, open: false })}
              anchorOrigin={{ vertical: 'bottom', horizontal: 'left' }}
            >
              <Alert
                elevation={6}
                variant="filled"
                severity={notification.severity}
                onClose={() => setNotification({ ...notification, open: false })}
                sx={{ width: '100%' }}
              >
                {notification.message}
              </Alert>
            </Snackbar>
          </Grid>
        </Box>
      </DndProvider>
    </ThemeProvider>
  );
};

export default NetworkDashboard;


export const formatBytes = (bytes) => {
  if (bytes === 0) return '0 B';
  const k = 1024;
  const sizes = ['B', 'KB', 'MB', 'GB', 'TB'];
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
};

export const formatSpeed = (speed) => {
  return `${speed?.toFixed(1) || 0} Mbps`;
};

export const getDeviceTypeIcon = (deviceType) => {
  const types = {
    smartphone: '📱',
    laptop: '💻',
    desktop: '🖥️',
    tablet: '📱',
    'smart tv': '📺',
    printer: '🖨️',
    console: '🎮',
    unknown: '❓'
  };
  return types[deviceType?.toLowerCase()] || types.unknown;
};

export const calculateNetworkStats = (devices) => {
  return {
    total: devices.length,
    active: devices.filter(d => d.status === 'active').length,
    limited: devices.filter(d => d.speed_limit).length,
    protected: devices.filter(d => d.is_protected).length,
    cutting: devices.filter(d => d.attack_status === 'cutting').length,
    totalBandwidth: devices.reduce((sum, device) => sum + (device.current_speed || 0), 0)
  };
};

export const API_BASE_URL = 'http://localhost:5000';

export const API_ENDPOINTS = {
  INTERFACES: '/api/wifi/interfaces',
  DEVICES: '/api/devices',
  STATS: '/api/stats/bandwidth',
  STATUS: '/api/status',
  GATEWAY: '/api/network/gateway',
  DEVICE: {
    LIMIT: '/api/device/limit',
    PROTECT: '/api/device/protect',
    UNPROTECT: '/api/device/unprotect',
    CUT: '/api/device/cut',
    RESTORE: '/api/device/restore',
    RENAME: '/api/device/rename'
  }
};

export const REFRESH_INTERVAL = 5000; // 5 seconds

export const SPEED_LIMITS = {
  DEFAULT: 10,
  MIN: 0,
  MAX: 100
};

export const DEVICE_GROUPS = {
  UNLIMITED: 'unlimited',
  LIMITED: 'limited'
};

export const CHART_CONFIG = {
  HEIGHT: 300,
  DATA_POINTS: 10
};

export const NOTIFICATION_DURATION = 4000; // 4 seconds