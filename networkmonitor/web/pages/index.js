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
  Snackbar,
  useTheme,
  ThemeProvider,
  createTheme,
  CssBaseline,
} from '@mui/material';
import {
  Wifi as WifiIcon,
  WifiOff as WifiOffIcon,
  Speed as SpeedIcon,
  Delete as DeleteIcon,
  Settings as SettingsIcon,
  NetworkCheck as NetworkCheckIcon,
  Refresh as RefreshIcon,
  DragIndicator as DragIndicatorIcon,
} from '@mui/icons-material';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import { motion } from 'framer-motion';

// Create a custom theme
const theme = createTheme({
  palette: {
    primary: {
      main: '#2196f3',
    },
    secondary: {
      main: '#f50057',
    },
    background: {
      default: '#f5f5f5',
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
  },
});

// Device Card Component with Drag and Drop
const DeviceCard = ({ device, onLimitChange, onDelete, onDrag }) => {
  const [{ isDragging }, drag] = useDrag(() => ({
    type: 'device',
    item: { id: device.ip, device },
    collect: (monitor) => ({
      isDragging: monitor.isDragging(),
    }),
  }));

  return (
    <motion.div
      ref={drag}
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3 }}
      style={{ opacity: isDragging ? 0.5 : 1, cursor: 'move' }}
    >
      <Card 
        sx={{ 
          mb: 2, 
          bgcolor: device.status === 'active' ? 'background.paper' : 'action.disabledBackground',
          '&:hover': { boxShadow: 6 },
          transition: 'box-shadow 0.3s',
        }}
      >
        <CardContent>
          <Grid container spacing={2} alignItems="center">
            <Grid item>
              <DragIndicatorIcon color="action" />
            </Grid>
            <Grid item>
              {device.status === 'active' ? 
                <WifiIcon color="primary" /> : 
                <WifiOffIcon color="error" />
              }
            </Grid>
            <Grid item xs>
              <Typography variant="h6">{device.hostname || device.ip}</Typography>
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
                Current Speed: {device.currentSpeed?.toFixed(1)} Mbps
              </Typography>
              <LinearProgress 
                variant="determinate" 
                value={(device.currentSpeed / (device.speedLimit || 100)) * 100}
                sx={{ mb: 1, height: 8, borderRadius: 4 }}
              />
              <Grid container spacing={1} alignItems="center">
                <Grid item xs>
                  <Slider
                    value={device.speedLimit || 0}
                    onChange={(_, value) => onLimitChange(device.ip, value)}
                    min={0}
                    max={100}
                    valueLabelDisplay="auto"
                    valueLabelFormat={(value) => `${value} Mbps`}
                  />
                </Grid>
                <Grid item>
                  <IconButton 
                    size="small" 
                    onClick={() => onDelete(device.ip)}
                    color="error"
                  >
                    <DeleteIcon />
                  </IconButton>
                </Grid>
              </Grid>
            </Grid>
          </Grid>
        </CardContent>
      </Card>
    </motion.div>
  );
};

// Speed Group Component with Drop functionality
const SpeedGroup = ({ title, devices, onDrop }) => {
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
      }}
    >
      <Typography variant="h6" gutterBottom>
        {title}
      </Typography>
      <Divider sx={{ mb: 2 }} />
      {devices.map((device) => (
        <DeviceCard
          key={device.ip}
          device={device}
          onLimitChange={(ip, limit) => console.log('Limit changed:', ip, limit)}
          onDelete={(ip) => console.log('Delete:', ip)}
        />
      ))}
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
    limited: []
  });
  const [chartData, setChartData] = useState([]);

  useEffect(() => {
    fetchInterfaces();
    fetchStatus();
    const interval = setInterval(() => {
      fetchStats();
      fetchDevices();
    }, 5000);
    return () => clearInterval(interval);
  }, [selectedInterface]);

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

  const fetchStatus = async () => {
    try {
      const response = await fetch('http://localhost:5000/api/status');
      const data = await response.json();
      if (data.success) {
        // You can use this data to show server status, OS type, etc.
        console.log('Server status:', data.data);
      }
    } catch (error) {
      showNotification('Failed to fetch server status', 'error');
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

  const handleSpeedLimit = async (ip, limit) => {
    try {
      const response = await fetch('http://localhost:5000/api/device/limit', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ ip, limit })
      });
      const data = await response.json();
      if (data.success) {
        showNotification(`Speed limit set for ${ip}`, 'success');
        fetchDevices();
      }
    } catch (error) {
      showNotification('Failed to set speed limit', 'error');
    }
  };

  const handleRemoveLimit = async (ip) => {
    try {
      const response = await fetch(`http://localhost:5000/api/device/limit/${ip}`, {
        method: 'DELETE'
      });
      const data = await response.json();
      if (data.success) {
        showNotification(`Speed limit removed for ${ip}`, 'success');
        fetchDevices();
      }
    } catch (error) {
      showNotification('Failed to remove speed limit', 'error');
    }
  };

  const handleDeviceDrop = (device, groupType) => {
    const limit = groupType === 'limited' ? 50 : null; // Default limit for limited group
    if (limit) {
      handleSpeedLimit(device.ip, limit);
    } else {
      handleRemoveLimit(device.ip);
    }
  };

  const showNotification = (message, severity = 'info') => {
    setNotification({ open: true, message, severity });
  };

  const formatBytes = (bytes) => {
    if (!bytes) return '0 B';
    const sizes = ['B', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(1024));
    return `${(bytes / Math.pow(1024, i)).toFixed(2)} ${sizes[i]}`;
  };

  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <DndProvider backend={HTML5Backend}>
        <Box sx={{ p: 3 }}>
          <Grid container spacing={3}>
            {/* Header Section */}
            <Grid item xs={12}>
              <Card>
                <CardContent>
                  <Grid container spacing={2} alignItems="center">
                    <Grid item xs={12} md={4}>
                      <FormControl fullWidth>
                        <InputLabel>Network Interface</InputLabel>
                        <Select
                          value={selectedInterface}
                          onChange={(e) => setSelectedInterface(e.target.value)}
                          label="Network Interface"
                        >
                          {interfaces.map((iface) => (
                            <MenuItem key={iface} value={iface}>
                              {iface}
                            </MenuItem>
                          ))}
                        </Select>
                      </FormControl>
                    </Grid>
                    <Grid item xs={12} md={8}>
                      <Grid container spacing={2}>
                        <Grid item xs={6}>
                          <Typography variant="body2" color="textSecondary">
                            Total Upload Speed
                          </Typography>
                          <Typography variant="h6">
                            {formatBytes(chartData[chartData.length - 1]?.upload || 0)}/s
                          </Typography>
                        </Grid>
                        <Grid item xs={6}>
                          <Typography variant="body2" color="textSecondary">
                            Total Download Speed
                          </Typography>
                          <Typography variant="h6">
                            {formatBytes(chartData[chartData.length - 1]?.download || 0)}/s
                          </Typography>
                        </Grid>
                      </Grid>
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
                    Bandwidth Usage
                  </Typography>
                  <Box sx={{ width: '100%', height: 300 }}>
                    <ResponsiveContainer width="100%" height="100%">
                      <LineChart data={chartData}>
                        <CartesianGrid strokeDasharray="3 3" />
                        <XAxis dataKey="time" />
                        <YAxis />
                        <Tooltip />
                        <Legend />
                        <Line type="monotone" dataKey="upload" stroke="#8884d8" name="Upload (MB/s)" />
                        <Line type="monotone" dataKey="download" stroke="#82ca9d" name="Download (MB/s)" />
                      </LineChart>
                    </ResponsiveContainer>
                  </Box>
                </CardContent>
              </Card>
            </Grid>

            {/* Device Groups */}
            <Grid item xs={12} md={6}>
              <SpeedGroup
                title="Unlimited Speed Devices"
                devices={speedGroups.unlimited}
                onDrop={(device) => handleDeviceDrop(device, 'unlimited')}
                onLimitChange={handleSpeedLimit}
                onDelete={handleRemoveLimit}
              />
            </Grid>
            <Grid item xs={12} md={6}>
              <SpeedGroup
                title="Limited Speed Devices"
                devices={speedGroups.limited}
                onDrop={(device) => handleDeviceDrop(device, 'limited')}
                onLimitChange={handleSpeedLimit}
                onDelete={handleRemoveLimit}
              />
            </Grid>
          </Grid>

          {/* Floating Action Button for Refresh */}
          <Box
            sx={{
              position: 'fixed',
              bottom: 20,
              right: 20,
            }}
          >
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
                }}
                sx={{ borderRadius: 28 }}
              >
                Refresh
              </Button>
            </motion.div>
          </Box>

          {/* Notifications */}
          <Snackbar
            open={notification.open}
            autoHideDuration={6000}
            onClose={() => setNotification({ ...notification, open: false })}
          >
            <Alert severity={notification.severity} onClose={() => setNotification({ ...notification, open: false })}>
              {notification.message}
            </Alert>
          </Snackbar>
        </Box>
      </DndProvider>
    </ThemeProvider>
  );
};

export default NetworkDashboard;
