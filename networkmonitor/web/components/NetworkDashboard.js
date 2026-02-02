import React, { useState, useEffect, useCallback } from 'react';
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
  Stack,
  Fade,
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
  Fingerprint as FingerprintIcon,
  Business as BusinessIcon,
} from '@mui/icons-material';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip as RechartsTooltip, Legend, ResponsiveContainer } from 'recharts';
import { motion, AnimatePresence } from 'framer-motion';
import {
  TrendingUp,
  Wifi,
  Speed,
  WifiOff,
  Gauge,
  Activity,
  ArrowDown,
  ArrowUp,
  Router,
  Network,
  Cpu,
  RefreshCw,
  MoreVertical,
  Settings
} from 'lucide-react';

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
      animate={{
        opacity: isDragging ? 0.85 : 1,
        y: 0,
        scale: isDragging ? 1.05 : 1,
        rotate: isDragging ? 2 : 0,
        boxShadow: isDragging
          ? '0 30px 60px rgba(33, 150, 243, 0.3), 0 15px 30px rgba(33, 150, 243, 0.2)'
          : 'none',
      }}
      exit={{ opacity: 0, y: -20 }}
      transition={{ duration: 0.3, ease: 'easeOut' }}
      style={{
        cursor: isDragging ? 'grabbing' : 'grab',
        zIndex: isDragging ? 1000 : 1,
        position: 'relative',
      }}
      whileHover={{ scale: 1.01 }}
      whileTap={{ scale: 1.03 }}
    >
      <Card
        sx={{
          mb: 3,
          bgcolor: 'background.paper',
          '&:hover': {
            boxShadow: '0 20px 40px rgba(0,0,0,0.12), 0 8px 16px rgba(0,0,0,0.06)',
            transform: 'translateY(-4px)',
          },
          transition: 'all 0.5s cubic-bezier(0.4, 0, 0.2, 1)',
          position: 'relative',
          overflow: 'visible',
          borderRadius: '24px',
          border: '1px solid rgba(0,0,0,0.08)',
          backgroundImage: 'linear-gradient(135deg, rgba(255,255,255,0.95), rgba(255,255,255,0.85))',
          backdropFilter: 'blur(10px)',
          '&::before': {
            content: '""',
            position: 'absolute',
            top: 0,
            left: 0,
            right: 0,
            bottom: 0,
            borderRadius: '24px',
            padding: '2px',
            background: 'linear-gradient(135deg, rgba(33,150,243,0.3), rgba(21,101,192,0.1))',
            WebkitMask: 'linear-gradient(#fff 0 0) content-box, linear-gradient(#fff 0 0)',
            WebkitMaskComposite: 'xor',
            maskComposite: 'exclude',
          }
        }}
      >
        <CardContent sx={{ p: 4 }}>
          <Grid container spacing={4} alignItems="center">
            <Grid item>
              <Box
                sx={{
                  bgcolor: 'rgba(33,150,243,0.08)',
                  p: 1.5,
                  borderRadius: '16px',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  transform: 'rotate(0deg)',
                  transition: 'transform 0.3s ease',
                  '&:hover': {
                    transform: 'rotate(180deg)',
                    bgcolor: 'rgba(33,150,243,0.12)',
                  }
                }}
              >
                <DragIndicatorIcon
                  color="primary"
                  sx={{
                    opacity: 0.8,
                    transition: 'opacity 0.2s',
                    '&:hover': { opacity: 1 }
                  }}
                />
              </Box>
            </Grid>
            <Grid item>
              <Badge
                color={getStatusColor()}
                variant="dot"
                anchorOrigin={{
                  vertical: 'bottom',
                  horizontal: 'right',
                }}
                sx={{
                  '& .MuiBadge-badge': {
                    height: '16px',
                    width: '16px',
                    borderRadius: '8px',
                    boxShadow: '0 0 0 3px #fff, 0 0 0 6px rgba(0,0,0,0.04)',
                    animation: 'pulse 2s infinite'
                  },
                  '@keyframes pulse': {
                    '0%': { transform: 'scale(1)' },
                    '50%': { transform: 'scale(1.1)' },
                    '100%': { transform: 'scale(1)' }
                  }
                }}
              >
                <Box
                  sx={{
                    bgcolor: device.status === 'active' ? 'primary.lighter' : 'error.lighter',
                    p: 2,
                    borderRadius: '16px',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    transition: 'transform 0.3s ease',
                    '&:hover': {
                      transform: 'scale(1.1)',
                    }
                  }}
                >
                  {device.status === 'active' ? (
                    <WifiIcon color="primary" sx={{ fontSize: 32 }} />
                  ) : (
                    <WifiOffIcon color="error" sx={{ fontSize: 32 }} />
                  )}
                </Box>
              </Badge>
            </Grid>
            <Grid item xs>
              <Typography
                variant="h5"
                sx={{
                  display: 'flex',
                  alignItems: 'center',
                  gap: 2,
                  fontWeight: 600,
                  color: 'text.primary',
                  mb: 1.5,
                  letterSpacing: '-0.5px'
                }}
              >
                {device.hostname || device.ip}
                {getStatusChip()}
              </Typography>
              <Stack spacing={1.5}>
                <Typography
                  variant="body2"
                  sx={{
                    fontFamily: 'Roboto Mono, monospace',
                    letterSpacing: '0.5px',
                    color: 'text.secondary',
                    display: 'flex',
                    alignItems: 'center',
                    gap: 1.5,
                    fontSize: '0.9rem'
                  }}
                >
                  <FingerprintIcon sx={{ fontSize: 22, opacity: 0.9 }} />
                  MAC: {device.mac}
                </Typography>
                {device.vendor && (
                  <Typography
                    variant="body2"
                    sx={{
                      color: 'text.secondary',
                      display: 'flex',
                      alignItems: 'center',
                      gap: 1.5,
                      fontSize: '0.9rem'
                    }}
                  >
                    <BusinessIcon sx={{ fontSize: 18, opacity: 0.8 }} />
                    Vendor: {device.vendor}
                  </Typography>
                )}
              </Stack>
            </Grid>
            <Grid item xs={12} md={4}>
              <Box
                sx={{
                  bgcolor: 'rgba(33,150,243,0.04)',
                  p: 3,
                  borderRadius: '20px',
                  border: '1px solid rgba(33,150,243,0.1)',
                  position: 'relative',
                  overflow: 'hidden',
                  '&::before': {
                    content: '""',
                    position: 'absolute',
                    top: 0,
                    left: 0,
                    right: 0,
                    bottom: 0,
                    background: 'radial-gradient(circle at top right, rgba(33,150,243,0.1), transparent)',
                    opacity: 0.5
                  }
                }}
              >
                <Typography
                  variant="body2"
                  sx={{
                    display: 'flex',
                    alignItems: 'center',
                    gap: 1.5,
                    mb: 2.5,
                    position: 'relative'
                  }}
                >
                  <SpeedIcon sx={{ fontSize: 20, color: 'primary.main' }} />
                  Current Speed:
                  <Box
                    component="span"
                    sx={{
                      fontWeight: 700,
                      color: 'primary.main',
                      bgcolor: 'primary.lighter',
                      px: 1.5,
                      py: 0.75,
                      borderRadius: '8px',
                      fontSize: '0.95rem',
                      boxShadow: '0 2px 8px rgba(33,150,243,0.2)',
                      animation: 'float 3s ease-in-out infinite'
                    }}
                  >
                    {device.current_speed?.toFixed(1)} Mbps
                  </Box>
                </Typography>
                <LinearProgress
                  variant="determinate"
                  value={(device.current_speed / (device.speed_limit || 100)) * 100}
                  sx={{
                    mb: 3,
                    height: 12,
                    borderRadius: 6,
                    bgcolor: 'rgba(0,0,0,0.04)',
                    '& .MuiLinearProgress-bar': {
                      borderRadius: 6,
                      backgroundImage: 'linear-gradient(90deg, #2196f3, #1565c0)',
                      boxShadow: '0 2px 6px rgba(33,150,243,0.3)'
                    }
                  }}
                />
                <Grid container spacing={2} alignItems="center">
                  <Grid item xs>
                    <Slider
                      value={device.speed_limit || 0}
                      onChange={(_, value) => onLimitChange(device.ip, value)}
                      min={0}
                      max={100}
                      valueLabelDisplay="auto"
                      valueLabelFormat={(value) => `${value} Mbps`}
                      sx={{
                        '& .MuiSlider-thumb': {
                          width: 20,
                          height: 20,
                          transition: 'all 0.2s',
                          '&:hover, &.Mui-focusVisible': {
                            boxShadow: '0 0 0 10px rgba(33, 150, 243, 0.2)'
                          }
                        },
                        '& .MuiSlider-track': {
                          height: 8,
                          borderRadius: 4
                        },
                        '& .MuiSlider-rail': {
                          height: 8,
                          borderRadius: 4,
                          opacity: 0.2
                        },
                        '& .MuiSlider-valueLabel': {
                          borderRadius: '10px',
                          padding: '6px 12px',
                          backgroundColor: 'primary.dark',
                          fontSize: '0.85rem',
                          fontWeight: 600
                        }
                      }}
                    />
                  </Grid>
                  <Grid item>
                    <Stack direction="row" spacing={2}>
                      <Tooltip
                        title={device.is_protected ? "Unprotect Device" : "Protect Device"}
                        arrow
                      >
                        <IconButton
                          size="large"
                          onClick={() => device.is_protected ? onUnprotect(device.ip) : onProtect(device.ip)}
                          color={device.is_protected ? "success" : "default"}
                          sx={{
                            bgcolor: device.is_protected ? 'success.lighter' : 'action.hover',
                            '&:hover': {
                              bgcolor: device.is_protected ? 'success.light' : 'action.selected',
                              transform: 'scale(1.1)'
                            },
                            transition: 'all 0.3s',
                            boxShadow: '0 4px 12px rgba(0,0,0,0.1)'
                          }}
                        >
                          <SecurityIcon />
                        </IconButton>
                      </Tooltip>
                      <Tooltip
                        title={device.attack_status === 'cutting' ? "Restore Network" : "Cut Network"}
                        arrow
                      >
                        <IconButton
                          size="large"
                          onClick={() => device.attack_status === 'cutting' ? onRestore(device.ip) : onCut(device.ip)}
                          color={device.attack_status === 'cutting' ? "error" : "default"}
                          disabled={device.is_protected}
                          sx={{
                            bgcolor: device.attack_status === 'cutting' ? 'error.lighter' : 'action.hover',
                            '&:hover': {
                              bgcolor: device.attack_status === 'cutting' ? 'error.light' : 'action.selected',
                              transform: 'scale(1.1)'
                            },
                            transition: 'all 0.3s',
                            boxShadow: '0 4px 12px rgba(0,0,0,0.1)',
                            '&.Mui-disabled': {
                              bgcolor: 'action.disabledBackground',
                              opacity: 0.6
                            }
                          }}
                        >
                          {device.attack_status === 'cutting' ? <RestartAltIcon /> : <BlockIcon />}
                        </IconButton>
                      </Tooltip>
                      <Tooltip title="Rename Device" arrow>
                        <IconButton
                          size="large"
                          onClick={() => setDialogOpen(true)}
                          color="primary"
                          sx={{
                            bgcolor: 'primary.lighter',
                            '&:hover': {
                              bgcolor: 'primary.light',
                              transform: 'scale(1.1)'
                            },
                            transition: 'all 0.3s',
                            boxShadow: '0 4px 12px rgba(33,150,243,0.2)'
                          }}
                        >
                          <EditIcon />
                        </IconButton>
                      </Tooltip>
                    </Stack>
                  </Grid>
                </Grid>
              </Box>
            </Grid>
          </Grid>
        </CardContent>

        <Dialog
          open={dialogOpen}
          onClose={() => setDialogOpen(false)}
          PaperProps={{
            sx: {
              borderRadius: '24px',
              maxWidth: '500px',
              width: '100%',
              backgroundImage: 'linear-gradient(135deg, rgba(255,255,255,0.98), rgba(255,255,255,0.95))',
              boxShadow: '0 32px 64px rgba(0,0,0,0.2)',
              border: '1px solid rgba(33,150,243,0.1)',
              '&::before': {
                content: '""',
                position: 'absolute',
                top: 0,
                left: 0,
                right: 0,
                bottom: 0,
                borderRadius: '24px',
                padding: '2px',
                background: 'linear-gradient(135deg, rgba(33,150,243,0.3), rgba(21,101,192,0.1))',
                WebkitMask: 'linear-gradient(#fff 0 0) content-box, linear-gradient(#fff 0 0)',
                WebkitMaskComposite: 'xor',
                maskComposite: 'exclude',
              }
            }
          }}
          TransitionComponent={Fade}
          TransitionProps={{ timeout: 400 }}
        >
          <DialogTitle
            sx={{
              p: 4,
              pb: 2,
              fontSize: '1.75rem',
              fontWeight: 800,
              color: 'text.primary',
              letterSpacing: '-0.5px'
            }}
          >
            Rename Device
          </DialogTitle>
          <DialogContent sx={{ p: 4, pb: 2 }}>
            <TextField
              autoFocus
              margin="dense"
              label="New Name"
              fullWidth
              value={newName}
              onChange={(e) => setNewName(e.target.value)}
              variant="outlined"
              sx={{
                '& .MuiOutlinedInput-root': {
                  borderRadius: '16px',
                  backgroundColor: 'rgba(255,255,255,0.6)',
                  '&:hover .MuiOutlinedInput-notchedOutline': {
                    borderColor: 'primary.main',
                    borderWidth: '2px'
                  },
                  '&.Mui-focused .MuiOutlinedInput-notchedOutline': {
                    borderColor: 'primary.main',
                    borderWidth: '2px',
                    boxShadow: '0 0 0 4px rgba(33,150,243,0.1)'
                  }
                },
                '& .MuiOutlinedInput-notchedOutline': {
                  borderColor: 'rgba(33,150,243,0.2)',
                  transition: 'all 0.3s'
                },
                '& .MuiInputLabel-root': {
                  fontSize: '0.95rem',
                  fontWeight: 500,
                  '&.Mui-focused': {
                    color: 'primary.main'
                  }
                },
                '& .MuiInputBase-input': {
                  fontSize: '1rem',
                  padding: '16px 20px'
                }
              }}
            />
          </DialogContent>
          <DialogActions sx={{ px: 4, pb: 4, gap: 2 }}>
            <Button
              onClick={() => setDialogOpen(false)}
              variant="outlined"
              sx={{
                borderRadius: '12px',
                px: 4,
                py: 1.5,
                textTransform: 'none',
                fontSize: '0.95rem',
                fontWeight: 600,
                borderWidth: '2px',
                '&:hover': {
                  borderWidth: '2px',
                  bgcolor: 'action.hover',
                  transform: 'translateY(-2px)'
                },
                transition: 'all 0.3s'
              }}
            >
              Cancel
            </Button>
            <Button
              onClick={handleRename}
              color="primary"
              variant="contained"
              sx={{
                borderRadius: '12px',
                px: 4,
                py: 1.5,
                textTransform: 'none',
                fontSize: '0.95rem',
                fontWeight: 600,
                boxShadow: '0 8px 16px rgba(33, 150, 243, 0.3)',
                '&:hover': {
                  boxShadow: '0 12px 20px rgba(33, 150, 243, 0.4)',
                  transform: 'translateY(-2px)'
                },
                transition: 'all 0.3s'
              }}
            >
              Rename
            </Button>
          </DialogActions>
        </Dialog>
      </Card>
    </motion.div>
  );
};

const SpeedGroup = ({ title, devices, onDrop, ...deviceActions }) => {
  const [{ isOver, canDrop }, drop] = useDrop(() => ({
    accept: 'device',
    drop: (item) => onDrop(item.device, title),
    collect: (monitor) => ({
      isOver: monitor.isOver(),
      canDrop: monitor.canDrop(),
    }),
  }));

  const isActive = isOver && canDrop;

  return (
    <Paper
      ref={drop}
      sx={{
        p: 4,
        minHeight: 280,
        bgcolor: isActive
          ? 'rgba(33, 150, 243, 0.08)'
          : canDrop
            ? 'rgba(33, 150, 243, 0.02)'
            : 'background.paper',
        transition: 'all 0.4s cubic-bezier(0.4, 0, 0.2, 1)',
        borderRadius: '24px',
        position: 'relative',
        border: isActive
          ? '2px dashed rgba(33, 150, 243, 0.6)'
          : '1px solid rgba(0,0,0,0.08)',
        backgroundImage: isActive
          ? 'linear-gradient(135deg, rgba(33, 150, 243, 0.1), rgba(21, 101, 192, 0.05))'
          : 'linear-gradient(135deg, rgba(255,255,255,0.95), rgba(255,255,255,0.85))',
        backdropFilter: 'blur(10px)',
        transform: isActive ? 'scale(1.02)' : 'scale(1)',
        boxShadow: isActive
          ? '0 24px 48px rgba(33, 150, 243, 0.25), 0 12px 24px rgba(33, 150, 243, 0.15), inset 0 0 0 2px rgba(33, 150, 243, 0.1)'
          : canDrop
            ? '0 16px 32px rgba(0,0,0,0.08), 0 6px 12px rgba(0,0,0,0.04)'
            : '0 12px 24px rgba(0,0,0,0.06), 0 4px 8px rgba(0,0,0,0.04)',
        '&::before': {
          content: '""',
          position: 'absolute',
          top: 0,
          left: 0,
          right: 0,
          bottom: 0,
          borderRadius: '24px',
          padding: '2px',
          background: isActive
            ? 'linear-gradient(135deg, rgba(33,150,243,0.6), rgba(21,101,192,0.3))'
            : 'linear-gradient(135deg, rgba(33,150,243,0.3), rgba(21,101,192,0.1))',
          WebkitMask: 'linear-gradient(#fff 0 0) content-box, linear-gradient(#fff 0 0)',
          WebkitMaskComposite: 'xor',
          maskComposite: 'exclude',
          animation: isActive ? 'pulse-border 1.5s ease-in-out infinite' : 'none',
        },
        '@keyframes pulse-border': {
          '0%, 100%': {
            opacity: 1,
            transform: 'scale(1)',
          },
          '50%': {
            opacity: 0.7,
            transform: 'scale(1.01)',
          },
        },
        '&:hover': {
          transform: isActive ? 'scale(1.02)' : 'translateY(-4px)',
          boxShadow: '0 24px 48px rgba(33, 150, 243, 0.2), 0 12px 24px rgba(33, 150, 243, 0.15)'
        }
      }}
    >
      <Box sx={{
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        mb: 3
      }}>
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
          <Typography
            variant="h5"
            color="primary"
            sx={{
              fontWeight: 800,
              letterSpacing: '-0.5px',
              background: 'linear-gradient(135deg, #2196f3, #1565c0)',
              WebkitBackgroundClip: 'text',
              WebkitTextFillColor: 'transparent',
              position: 'relative',
              '&::after': {
                content: '""',
                position: 'absolute',
                bottom: -4,
                left: 0,
                width: '40%',
                height: '3px',
                background: 'linear-gradient(90deg, #2196f3, transparent)',
                borderRadius: '2px'
              }
            }}
          >
            {title}
          </Typography>
          <Chip
            label={`${devices.length} devices`}
            size="medium"
            sx={{
              borderRadius: '12px',
              bgcolor: 'primary.lighter',
              color: 'primary.main',
              fontWeight: 600,
              fontSize: '0.85rem',
              height: 32,
              px: 1,
              border: '2px solid',
              borderColor: 'primary.light',
              transition: 'all 0.3s',
              '&:hover': {
                transform: 'translateY(-2px)',
                boxShadow: '0 4px 8px rgba(33, 150, 243, 0.2)'
              }
            }}
          />
        </Box>
        <Box sx={{
          display: 'flex',
          gap: 1,
          position: 'relative',
          '&::before': {
            content: '""',
            position: 'absolute',
            top: '50%',
            left: -20,
            width: '2px',
            height: '40px',
            background: 'linear-gradient(to bottom, transparent, rgba(33,150,243,0.2), transparent)',
            transform: 'translateY(-50%)'
          }
        }}>
          <IconButton
            size="small"
            sx={{
              bgcolor: 'primary.lighter',
              '&:hover': {
                bgcolor: 'primary.light',
                transform: 'scale(1.1)'
              },
              transition: 'all 0.3s'
            }}
          >
            <RefreshCw size={18} />
          </IconButton>
          <IconButton
            size="small"
            sx={{
              bgcolor: 'primary.lighter',
              '&:hover': {
                bgcolor: 'primary.light',
                transform: 'scale(1.1)'
              },
              transition: 'all 0.3s'
            }}
          >
            <Settings size={18} />
          </IconButton>
        </Box>
      </Box>

      <Divider
        sx={{
          mb: 4,
          backgroundImage: 'linear-gradient(90deg, rgba(33,150,243,0.2), transparent)',
          height: '2px',
          border: 'none'
        }}
      />

      <AnimatePresence>
        <Box
          sx={{
            display: 'grid',
            gap: 3,
            position: 'relative',
            '&::before': {
              content: '""',
              position: 'absolute',
              top: 0,
              left: '20px',
              width: '2px',
              height: '100%',
              background: 'linear-gradient(to bottom, transparent, rgba(33,150,243,0.1), transparent)',
              zIndex: 0
            }
          }}
        >
          {devices.map((device) => (
            <motion.div
              key={device.ip}
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              exit={{ opacity: 0, x: 20 }}
              transition={{ duration: 0.4, ease: 'easeOut' }}
            >
              <DeviceCard
                device={device}
                {...deviceActions}
              />
            </motion.div>
          ))}
        </Box>
      </AnimatePresence>

      {devices.length === 0 && (
        <motion.div
          initial={{ opacity: 0, scale: 0.95 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ duration: 0.4, ease: 'easeOut' }}
        >
          <Box
            sx={{
              textAlign: 'center',
              py: 6,
              px: 4,
              bgcolor: isActive
                ? 'rgba(33, 150, 243, 0.12)'
                : 'rgba(33,150,243,0.02)',
              borderRadius: '20px',
              border: isActive
                ? '3px dashed rgba(33, 150, 243, 0.5)'
                : '2px dashed rgba(33,150,243,0.15)',
              transition: 'all 0.3s ease',
              transform: isActive ? 'scale(1.02)' : 'scale(1)',
            }}
          >
            <Box
              sx={{
                width: 80,
                height: 80,
                borderRadius: '50%',
                bgcolor: isActive
                  ? 'rgba(33, 150, 243, 0.15)'
                  : 'rgba(33, 150, 243, 0.06)',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                mx: 'auto',
                mb: 3,
                transition: 'all 0.3s ease',
                animation: isActive ? 'bounce 1s ease infinite' : 'none',
                '@keyframes bounce': {
                  '0%, 100%': { transform: 'translateY(0)' },
                  '50%': { transform: 'translateY(-8px)' },
                },
              }}
            >
              <DragIndicatorIcon
                sx={{
                  fontSize: 40,
                  color: isActive ? 'primary.main' : 'rgba(33,150,243,0.4)',
                  transition: 'all 0.3s ease',
                }}
              />
            </Box>
            <Typography
              variant="h6"
              sx={{
                color: isActive ? 'primary.main' : 'text.secondary',
                fontWeight: 600,
                mb: 1,
                transition: 'all 0.3s ease',
              }}
            >
              {isActive ? 'Drop device here!' : 'No devices in this group'}
            </Typography>
            <Typography
              variant="body2"
              color="text.secondary"
              sx={{
                opacity: 0.7,
                maxWidth: 280,
                mx: 'auto',
              }}
            >
              {isActive
                ? 'Release to add this device to the group'
                : 'Drag and drop devices here to organize them'}
            </Typography>
          </Box>
        </motion.div>
      )}
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
    }, 11000);
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
        // Filter out null/undefined devices and ensure required properties
        const validDevices = data.data.filter(device =>
          device && device.ip && device.mac &&
          (device.status === "active" || device.status === "inactive")
        ).map(device => ({
          ...device,
          hostname: device.hostname || "Unknown Device",
          device_type: device.device_type || "Unknown",
          vendor: device.vendor || "Unknown Vendor",
          status: device.status || "inactive"
        }));

        setDevices(validDevices);
        updateSpeedGroups(validDevices);
        console.log("Processed devices:", validDevices);
      } else {
        console.error("Failed to fetch devices:", data.error);
      }
    } catch (error) {
      console.error("Error fetching devices:", error);
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
    const groups = {
      unlimited: devices.filter(d => !d.speed_limit && d.status === "active"),
      limited: devices.filter(d => d.speed_limit && d.status === "active")
    };
    console.log("Updated speed groups:", groups);
    setSpeedGroups(groups);
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
              <Card
                sx={{
                  borderRadius: '16px',
                  background: 'linear-gradient(145deg, rgba(255,255,255,0.95), rgba(255,255,255,0.9))',
                  backdropFilter: 'blur(10px)',
                  border: '1px solid rgba(0,0,0,0.06)',
                  boxShadow: '0 4px 24px rgba(0,0,0,0.06)',
                  transition: 'all 0.3s ease',
                  '&:hover': {
                    transform: 'translateY(-2px)',
                    boxShadow: '0 8px 32px rgba(0,0,0,0.08)'
                  }
                }}
              >
                <CardContent sx={{ p: 3 }}>
                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, mb: 3 }}>
                    <Box
                      sx={{
                        bgcolor: 'primary.lighter',
                        p: 1.5,
                        borderRadius: '12px',
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'center'
                      }}
                    >
                      <Router size={24} color={theme.palette.primary.main} />
                    </Box>
                    <Box>
                      <Typography
                        variant="h6"
                        sx={{
                          fontWeight: 700,
                          color: 'text.primary',
                          fontSize: '1.25rem',
                          mb: 0.5
                        }}
                      >
                        Network Gateway
                      </Typography>
                      <Typography variant="body2" color="text.secondary">
                        Primary network connection details
                      </Typography>
                    </Box>
                  </Box>

                  <Grid container spacing={3}>
                    <Grid item xs={12} md={6}>
                      <Paper
                        sx={{
                          p: 2.5,
                          borderRadius: '12px',
                          bgcolor: 'background.default',
                          border: '1px solid rgba(0,0,0,0.04)'
                        }}
                      >
                        <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
                          <Box
                            sx={{
                              bgcolor: 'info.lighter',
                              p: 1,
                              borderRadius: '8px'
                            }}
                          >
                            <Network size={20} color={theme.palette.info.main} />
                          </Box>
                          <Box>
                            <Typography
                              variant="body2"
                              color="text.secondary"
                              sx={{ mb: 0.5, fontSize: '0.75rem', textTransform: 'uppercase', letterSpacing: '0.5px' }}
                            >
                              IP Address
                            </Typography>
                            <Typography
                              variant="body1"
                              sx={{
                                fontFamily: 'monospace',
                                fontWeight: 600,
                                color: 'text.primary',
                                fontSize: '1rem'
                              }}
                            >
                              {gatewayInfo?.ip || 'Not Available'}
                            </Typography>
                          </Box>
                        </Box>
                      </Paper>
                    </Grid>

                    <Grid item xs={12} md={6}>
                      <Paper
                        sx={{
                          p: 2.5,
                          borderRadius: '12px',
                          bgcolor: 'background.default',
                          border: '1px solid rgba(0,0,0,0.04)'
                        }}
                      >
                        <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
                          <Box
                            sx={{
                              bgcolor: 'warning.lighter',
                              p: 1,
                              borderRadius: '8px'
                            }}
                          >
                            <Cpu size={20} color={theme.palette.warning.main} />
                          </Box>
                          <Box>
                            <Typography
                              variant="body2"
                              color="text.secondary"
                              sx={{ mb: 0.5, fontSize: '0.75rem', textTransform: 'uppercase', letterSpacing: '0.5px' }}
                            >
                              MAC Address
                            </Typography>
                            <Typography
                              variant="body1"
                              sx={{
                                fontFamily: 'monospace',
                                fontWeight: 600,
                                color: 'text.primary',
                                fontSize: '1rem'
                              }}
                            >
                              {gatewayInfo?.mac || 'Not Available'}
                            </Typography>
                          </Box>
                        </Box>
                      </Paper>
                    </Grid>
                  </Grid>

                  {/* Status Indicator */}
                  <Box
                    sx={{
                      display: 'flex',
                      alignItems: 'center',
                      gap: 1,
                      mt: 2
                    }}
                  >
                    <Box
                      sx={{
                        width: 8,
                        height: 8,
                        borderRadius: '50%',
                        bgcolor: gatewayInfo ? 'success.main' : 'error.main',
                        boxShadow: (theme) =>
                          `0 0 0 3px ${gatewayInfo
                            ? theme.palette.success.lighter
                            : theme.palette.error.lighter
                          }`
                      }}
                    />
                    <Typography
                      variant="caption"
                      color={gatewayInfo ? 'success.main' : 'error.main'}
                      sx={{ fontWeight: 500 }}
                    >
                      {gatewayInfo ? 'Gateway Connected' : 'Gateway Unavailable'}
                    </Typography>
                  </Box>
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
              <Card
                sx={{
                  borderRadius: '16px',
                  background: 'linear-gradient(145deg, rgba(255,255,255,0.95), rgba(255,255,255,0.9))',
                  backdropFilter: 'blur(10px)',
                  border: '1px solid rgba(0,0,0,0.06)',
                  boxShadow: '0 4px 24px rgba(0,0,0,0.06)',
                  transition: 'all 0.3s ease',
                  '&:hover': {
                    transform: 'translateY(-2px)',
                    boxShadow: '0 8px 32px rgba(0,0,0,0.08)'
                  }
                }}
              >
                {/* Rest of the code remains the same until the Limited Devices icon */}
                <CardContent sx={{ p: 3 }}>
                  <Typography
                    variant="h6"
                    gutterBottom
                    sx={{
                      fontWeight: 700,
                      fontSize: '1.25rem',
                      color: 'text.primary',
                      mb: 3,
                      display: 'flex',
                      alignItems: 'center',
                      gap: 1
                    }}
                  >
                    <TrendingUp size={24} />
                    Network Statistics
                  </Typography>

                  <Grid container spacing={3}>
                    <Grid item xs={12} md={3}>
                      <Paper
                        sx={{
                          p: 3,
                          textAlign: 'center',
                          borderRadius: '12px',
                          background: 'linear-gradient(135deg, primary.main, primary.dark)',
                          position: 'relative',
                          overflow: 'hidden',
                          '&::before': {
                            content: '""',
                            position: 'absolute',
                            top: 0,
                            left: 0,
                            right: 0,
                            bottom: 0,
                            background: 'linear-gradient(45deg, #2196f3, #1976d2)',
                            opacity: 1
                          }
                        }}
                      >
                        <Box
                          sx={{
                            position: 'relative',
                            zIndex: 1,
                            display: 'flex',
                            flexDirection: 'column',
                            gap: 1
                          }}
                        >
                          <Box
                            sx={{
                              width: '48px',
                              height: '48px',
                              borderRadius: '50%',
                              bgcolor: 'rgba(255,255,255,0.15)',
                              display: 'flex',
                              alignItems: 'center',
                              justifyContent: 'center',
                              margin: '0 auto 12px'
                            }}
                          >
                            <Wifi size={24} color="white" />
                          </Box>
                          <Typography
                            variant="h4"
                            sx={{
                              color: 'white',
                              fontWeight: 700,
                              textShadow: '0 2px 4px rgba(0,0,0,0.1)'
                            }}
                          >
                            {devices.length}
                          </Typography>
                          <Typography
                            variant="body2"
                            sx={{
                              color: 'rgba(255,255,255,0.9)',
                              fontWeight: 500,
                              textTransform: 'uppercase',
                              letterSpacing: '0.5px'
                            }}
                          >
                            Total Devices
                          </Typography>
                        </Box>
                      </Paper>
                    </Grid>

                    <Grid item xs={12} md={3}>
                      <Paper
                        sx={{
                          p: 3,
                          textAlign: 'center',
                          borderRadius: '12px',
                          position: 'relative',
                          overflow: 'hidden',
                          '&::before': {
                            content: '""',
                            position: 'absolute',
                            top: 0,
                            left: 0,
                            right: 0,
                            bottom: 0,
                            background: 'linear-gradient(45deg, #4caf50, #2e7d32)',
                            opacity: 1
                          }
                        }}
                      >
                        <Box
                          sx={{
                            position: 'relative',
                            zIndex: 1,
                            display: 'flex',
                            flexDirection: 'column',
                            gap: 1
                          }}
                        >
                          <Box
                            sx={{
                              width: '48px',
                              height: '48px',
                              borderRadius: '50%',
                              bgcolor: 'rgba(255,255,255,0.15)',
                              display: 'flex',
                              alignItems: 'center',
                              justifyContent: 'center',
                              margin: '0 auto 12px'
                            }}
                          >
                            <Wifi size={24} color="white" />
                          </Box>
                          <Typography
                            variant="h4"
                            sx={{
                              color: 'white',
                              fontWeight: 700,
                              textShadow: '0 2px 4px rgba(0,0,0,0.1)'
                            }}
                          >
                            {devices.filter(d => d.status === 'active').length}
                          </Typography>
                          <Typography
                            variant="body2"
                            sx={{
                              color: 'rgba(255,255,255,0.9)',
                              fontWeight: 500,
                              textTransform: 'uppercase',
                              letterSpacing: '0.5px'
                            }}
                          >
                            Active Devices
                          </Typography>
                        </Box>
                      </Paper>
                    </Grid>

                    <Grid item xs={12} md={3}>
                      <Paper
                        sx={{
                          p: 3,
                          textAlign: 'center',
                          borderRadius: '12px',
                          position: 'relative',
                          overflow: 'hidden',
                          '&::before': {
                            content: '""',
                            position: 'absolute',
                            top: 0,
                            left: 0,
                            right: 0,
                            bottom: 0,
                            background: 'linear-gradient(45deg, #ff9800, #ed6c02)',
                            opacity: 1
                          }
                        }}
                      >
                        <Box
                          sx={{
                            position: 'relative',
                            zIndex: 1,
                            display: 'flex',
                            flexDirection: 'column',
                            gap: 1
                          }}
                        >
                          <Box
                            sx={{
                              width: '48px',
                              height: '48px',
                              borderRadius: '50%',
                              bgcolor: 'rgba(255,255,255,0.15)',
                              display: 'flex',
                              alignItems: 'center',
                              justifyContent: 'center',
                              margin: '0 auto 12px'
                            }}
                          >
                            <Gauge size={24} color="white" />
                          </Box>
                          <Typography
                            variant="h4"
                            sx={{
                              color: 'white',
                              fontWeight: 700,
                              textShadow: '0 2px 4px rgba(0,0,0,0.1)'
                            }}
                          >
                            {devices.filter(d => d.speed_limit).length}
                          </Typography>
                          <Typography
                            variant="body2"
                            sx={{
                              color: 'rgba(255,255,255,0.9)',
                              fontWeight: 500,
                              textTransform: 'uppercase',
                              letterSpacing: '0.5px'
                            }}
                          >
                            Limited Devices
                          </Typography>
                        </Box>
                      </Paper>
                    </Grid>

                    <Grid item xs={12} md={3}>
                      <Paper
                        sx={{
                          p: 3,
                          textAlign: 'center',
                          borderRadius: '12px',
                          position: 'relative',
                          overflow: 'hidden',
                          '&::before': {
                            content: '""',
                            position: 'absolute',
                            top: 0,
                            left: 0,
                            right: 0,
                            bottom: 0,
                            background: 'linear-gradient(45deg, #f44336, #d32f2f)',
                            opacity: 1
                          }
                        }}
                      >
                        <Box
                          sx={{
                            position: 'relative',
                            zIndex: 1,
                            display: 'flex',
                            flexDirection: 'column',
                            gap: 1
                          }}
                        >
                          <Box
                            sx={{
                              width: '48px',
                              height: '48px',
                              borderRadius: '50%',
                              bgcolor: 'rgba(255,255,255,0.15)',
                              display: 'flex',
                              alignItems: 'center',
                              justifyContent: 'center',
                              margin: '0 auto 12px'
                            }}
                          >
                            <WifiOff size={24} color="white" />
                          </Box>
                          <Typography
                            variant="h4"
                            sx={{
                              color: 'white',
                              fontWeight: 700,
                              textShadow: '0 2px 4px rgba(0,0,0,0.1)'
                            }}
                          >
                            {devices.filter(d => d.attack_status === 'cutting').length}
                          </Typography>
                          <Typography
                            variant="body2"
                            sx={{
                              color: 'rgba(255,255,255,0.9)',
                              fontWeight: 500,
                              textTransform: 'uppercase',
                              letterSpacing: '0.5px'
                            }}
                          >
                            Cut Devices
                          </Typography>
                        </Box>
                      </Paper>
                    </Grid>
                  </Grid>
                </CardContent>
              </Card>
            </Grid>

            {/* Bandwidth Chart */}
            <Grid item xs={12}>
              <Card
                sx={{
                  borderRadius: '16px',
                  background: 'linear-gradient(145deg, rgba(255,255,255,0.95), rgba(255,255,255,0.9))',
                  backdropFilter: 'blur(10px)',
                  border: '1px solid rgba(0,0,0,0.06)',
                  boxShadow: '0 4px 24px rgba(0,0,0,0.06)',
                  transition: 'all 0.3s ease',
                  '&:hover': {
                    transform: 'translateY(-2px)',
                    boxShadow: '0 8px 32px rgba(0,0,0,0.08)'
                  }
                }}
              >
                <CardContent sx={{ p: 3 }}>
                  <Box sx={{
                    display: 'flex',
                    justifyContent: 'space-between',
                    alignItems: 'center',
                    mb: 3
                  }}>
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                      <Activity size={24} className="text-primary" />
                      <Typography
                        variant="h6"
                        sx={{
                          fontWeight: 700,
                          fontSize: '1.25rem',
                          color: 'text.primary'
                        }}
                      >
                        Network Bandwidth Usage
                      </Typography>
                      <Tooltip
                        title="Real-time bandwidth monitoring"
                        arrow
                        placement="right"
                      >
                        <IconButton
                          size="small"
                          sx={{
                            ml: 1,
                            bgcolor: 'primary.lighter',
                            '&:hover': {
                              bgcolor: 'primary.light'
                            }
                          }}
                        >
                          <VisibilityIcon fontSize="small" />
                        </IconButton>
                      </Tooltip>
                    </Box>

                    <Box sx={{ display: 'flex', gap: 2 }}>
                      <Box sx={{
                        display: 'flex',
                        alignItems: 'center',
                        gap: 1,
                        px: 2,
                        py: 1,
                        borderRadius: '8px',
                        bgcolor: 'primary.lighter'
                      }}>
                        <ArrowUp size={16} className="text-primary" />
                        <Typography variant="body2" sx={{ fontWeight: 600, color: 'primary.main' }}>
                          Upload
                        </Typography>
                      </Box>
                      <Box sx={{
                        display: 'flex',
                        alignItems: 'center',
                        gap: 1,
                        px: 2,
                        py: 1,
                        borderRadius: '8px',
                        bgcolor: 'secondary.lighter'
                      }}>
                        <ArrowDown size={16} className="text-secondary" />
                        <Typography variant="body2" sx={{ fontWeight: 600, color: 'secondary.main' }}>
                          Download
                        </Typography>
                      </Box>
                    </Box>
                  </Box>

                  <Box
                    sx={{
                      width: '100%',
                      height: 300,
                      p: 1,
                      bgcolor: 'background.paper',
                      borderRadius: '12px',
                      border: '1px solid rgba(0,0,0,0.04)'
                    }}
                  >
                    <ResponsiveContainer>
                      <LineChart data={chartData}>
                        <CartesianGrid
                          strokeDasharray="3 3"
                          stroke="rgba(0,0,0,0.06)"
                          vertical={false}
                        />
                        <XAxis
                          dataKey="time"
                          tick={{ fontSize: 12, fill: 'text.secondary' }}
                          interval="preserveStartEnd"
                          axisLine={{ stroke: 'rgba(0,0,0,0.1)' }}
                          tickLine={{ stroke: 'rgba(0,0,0,0.1)' }}
                        />
                        <YAxis
                          tick={{ fontSize: 12, fill: 'text.secondary' }}
                          axisLine={{ stroke: 'rgba(0,0,0,0.1)' }}
                          tickLine={{ stroke: 'rgba(0,0,0,0.1)' }}
                          label={{
                            value: 'Speed (Mbps)',
                            angle: -90,
                            position: 'insideLeft',
                            style: {
                              fontSize: 12,
                              fill: 'text.secondary',
                              textTransform: 'uppercase',
                              letterSpacing: '0.5px'
                            }
                          }}
                        />
                        <RechartsTooltip
                          contentStyle={{
                            backgroundColor: 'rgba(255, 255, 255, 0.98)',
                            border: 'none',
                            borderRadius: '12px',
                            boxShadow: '0 4px 16px rgba(0,0,0,0.08)',
                            padding: '12px 16px',
                            fontSize: '12px'
                          }}
                          itemStyle={{
                            padding: '4px 0'
                          }}
                          labelStyle={{
                            fontWeight: 600,
                            marginBottom: '8px'
                          }}
                        />
                        <Legend
                          verticalAlign="top"
                          height={0}
                          content={() => null}
                        />
                        <Line
                          type="monotone"
                          dataKey="upload"
                          stroke={theme.palette.primary.main}
                          strokeWidth={2.5}
                          dot={false}
                          activeDot={{
                            r: 6,
                            strokeWidth: 2,
                            fill: theme.palette.primary.main,
                            stroke: theme.palette.primary.light
                          }}
                          name="Upload"
                        />
                        <Line
                          type="monotone"
                          dataKey="download"
                          stroke={theme.palette.secondary.main}
                          strokeWidth={2.5}
                          dot={false}
                          activeDot={{
                            r: 6,
                            strokeWidth: 2,
                            fill: theme.palette.secondary.main,
                            stroke: theme.palette.secondary.light
                          }}
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