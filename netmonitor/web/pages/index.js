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
} from '@mui/material';
import {
  Wifi as WifiIcon,
  WifiOff as WifiOffIcon,
  Speed as SpeedIcon,
  Delete as DeleteIcon,
  Settings as SettingsIcon,
  NetworkCheck as NetworkCheckIcon,
} from '@mui/icons-material';
import { LineChart } from '@mui/x-charts';

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
    <div ref={drag} style={{ opacity: isDragging ? 0.5 : 1, cursor: 'move' }}>
      <Card 
        sx={{ 
          mb: 2, 
          bgcolor: device.status === 'active' ? 'background.paper' : 'action.disabledBackground',
          '&:hover': { boxShadow: 3 }
        }}
      >
        <CardContent>
          <Grid container spacing={2} alignItems="center">
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
    </div>
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

// Main Dashboard Component
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

  useEffect(() => {
    fetchInterfaces();
    const interval = setInterval(() => {
      fetchStats();
      fetchDevices();
    }, 5000);
    return () => clearInterval(interval);
  }, [selectedInterface]);

  const fetchInterfaces = async () => {
    try {
      const response = await fetch('http://localhost:5000/api/interfaces');
      const data = await response.json();
      if (data.success) {
        setInterfaces(data.data);
        if (data.data.length > 0 && !selectedInterface) {
          setSelectedInterface(data.data[0].name);
        }
      }
    } catch (error) {
      showNotification('Failed to fetch interfaces', 'error');
    }
  };

  const fetchDevices = async () => {
    if (!selectedInterface) return;
    try {
      const response = await fetch(`http://localhost:5000/api/scan/${selectedInterface}`);
      const data = await response.json();
      if (data.success) {
        const updatedDevices = data.data.map(device => ({
          ...device,
          currentSpeed: Math.random() * 100 // Replace with actual speed data
        }));
        setDevices(updatedDevices);
        
        // Update speed groups
        setSpeedGroups({
          unlimited: updatedDevices.filter(d => !d.speedLimit),
          limited: updatedDevices.filter(d => d.speedLimit)
        });
      }
    } catch (error) {
      showNotification('Failed to fetch devices', 'error');
    }
  };

  const fetchStats = async () => {
    if (!selectedInterface) return;
    try {
      const response = await fetch(`http://localhost:5000/api/stats/${selectedInterface}`);
      const data = await response.json();
      if (data.success) {
        setStats(data.data);
      }
    } catch (error) {
      console.error('Failed to fetch stats:', error);
    }
  };

  const handleSpeedLimit = async (ip, limit) => {
    try {
      const response = await fetch('http://localhost:5000/api/limit', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          interface: selectedInterface,
          ip,
          limit: parseInt(limit)
        })
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

  const handleDeviceDrop = (device, groupType) => {
    const limit = groupType === 'limited' ? 50 : 0; // Default limit for limited group
    handleSpeedLimit(device.ip, limit);
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

  // Sample data for the bandwidth chart
  const chartData = {
    xAxis: [{ data: [1, 2, 3, 4, 5, 6, 7, 8, 9, 10] }],
    series: [
      {
        data: stats.bytes_sent ? Array(10).fill().map(() => stats.bytes_sent / 1024 / 1024) : [],
        label: 'Upload (MB/s)',
      },
      {
        data: stats.bytes_recv ? Array(10).fill().map(() => stats.bytes_recv / 1024 / 1024) : [],
        label: 'Download (MB/s)',
      },
    ],
  };

  return (
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
                          <MenuItem key={iface.name} value={iface.name}>
                            {iface.name}
                          </MenuItem>
                        ))}
                      </Select>
                    </FormControl>
                  </Grid>
                  <Grid item xs={12} md={8}>
                    <Grid container spacing={2}>
                      <Grid item xs={6}>
                        <Typography variant="body2" color="textSecondary">
                          Upload Speed
                        </Typography>
                        <Typography variant="h6">
                          {formatBytes(stats.bytes_sent)}/s
                        </Typography>
                      </Grid>
                      <Grid item xs={6}>
                        <Typography variant="body2" color="textSecondary">
                          Download Speed
                        </Typography>
                        <Typography variant="h6">
                          {formatBytes(stats.bytes_recv)}/s
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
                  <LineChart
                    xAxis={chartData.xAxis}
                    series={chartData.series}
                    width={800}
                    height={300}
                  />
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
            />
          </Grid>
          <Grid item xs={12} md={6}>
            <SpeedGroup
              title="Limited Speed Devices"
              devices={speedGroups.limited}
              onDrop={(device) => handleDeviceDrop(device, 'limited')}
            />
          </Grid>
        </Grid>

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
  );
};

export default NetworkDashboard;