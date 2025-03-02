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

const DependencyWarning = () => {
  const [dependencies, setDependencies] = useState({
    missingDeps: [],
    warnings: [],
    npcapStatus: null,
    isAdmin: false,
    instructions: {}
  });
  const [expanded, setExpanded] = useState(false);
  const [showMoreDetails, setShowMoreDetails] = useState(false);
  const [isNpcapFixed, setIsNpcapFixed] = useState(false);
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down('sm'));

  useEffect(() => {
    fetchDependencyStatus();
  }, []);

  const fetchDependencyStatus = async () => {
    try {
      const response = await fetch('http://localhost:5000/api/dependencies/check');
      if (response.ok) {
        const data = await response.json();
        setDependencies(data);
        setIsNpcapFixed(!data.missingDeps.includes('Npcap packet capture library'));
      }
    } catch (error) {
      console.error('Failed to fetch dependency status', error);
    }
  };

  const handleRefreshStatus = async () => {
    try {
      const response = await fetch('http://localhost:5000/api/dependencies/recheck', {
        method: 'POST'
      });
      if (response.ok) {
        await fetchDependencyStatus();
      }
    } catch (error) {
      console.error('Failed to refresh dependency status', error);
    }
  };

  const handleFixNpcap = async () => {
    try {
      const response = await fetch('http://localhost:5000/api/dependencies/fix-npcap', {
        method: 'POST'
      });
      if (response.ok) {
        await fetchDependencyStatus();
        setIsNpcapFixed(true);
      }
    } catch (error) {
      console.error('Failed to fix Npcap', error);
    }
  };

  const hasNpcapIssue = dependencies.missingDeps.includes('Npcap packet capture library');
  const hasAdminIssue = dependencies.warnings.some(w => w.includes('administrative privileges'));
  const hasMissingDeps = dependencies.missingDeps.length > 0;

  const getSeverity = () => {
    if (hasNpcapIssue) return 'error';
    if (hasAdminIssue) return 'warning';
    if (dependencies.warnings.length > 0) return 'info';
    return 'success';
  };

  const getTitle = () => {
    if (hasNpcapIssue) return 'Network Monitoring Unavailable';
    if (hasAdminIssue) return 'Limited Functionality';
    if (dependencies.warnings.length > 0) return 'Minor Issues Detected';
    return 'All Dependencies Installed';
  };

  const getSeverityIcon = () => {
    switch (getSeverity()) {
      case 'error': return <ErrorIcon fontSize="large" color="error" />;
      case 'warning': return <WarningIcon fontSize="large" color="warning" />;
      case 'info': return <InfoIcon fontSize="large" color="info" />;
      case 'success': return <CheckIcon fontSize="large" color="success" />;
      default: return <InfoIcon fontSize="large" />;
    }
  };

  return (
    <AnimatePresence>
      <motion.div
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        exit={{ opacity: 0, y: -20 }}
        transition={{ duration: 0.3 }}
      >
        <Card
          elevation={3}
          sx={{
            mb: 4,
            overflow: 'hidden',
            border: '1px solid',
            borderColor: theme.palette[getSeverity()].light,
            borderRadius: '16px',
            boxShadow: `0 6px 16px rgba(0, 0, 0, 0.08)`,
            background: `linear-gradient(to right bottom, ${theme.palette.background.paper}, ${theme.palette[getSeverity()].lighter})`,
          }}
        >
          <CardContent sx={{ p: 0 }}>
            <Box
              sx={{
                p: 3,
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'space-between',
                borderBottom: '1px solid',
                borderColor: theme.palette[getSeverity()].lighter,
                position: 'relative',
                '&::before': {
                  content: '""',
                  position: 'absolute',
                  top: 0,
                  left: 0,
                  width: '100%',
                  height: '100%',
                  background: `linear-gradient(90deg, ${theme.palette[getSeverity()].lighter} 0%, transparent 100%)`,
                  opacity: 0.4,
                  zIndex: 0,
                }
              }}
            >
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, position: 'relative', zIndex: 1 }}>
                <Box
                  sx={{
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    width: 48,
                    height: 48,
                    borderRadius: '12px',
                    backgroundColor: theme.palette[getSeverity()].lighter,
                  }}
                >
                  {getSeverityIcon()}
                </Box>
                <Box>
                  <Typography variant="h6" component="h2" sx={{ fontWeight: 600 }}>
                    {getTitle()}
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    {hasMissingDeps
                      ? `${dependencies.missingDeps.length} missing dependencies detected`
                      : dependencies.warnings.length > 0
                      ? `${dependencies.warnings.length} warnings found`
                      : 'Network Monitor is ready to use'}
                  </Typography>
                </Box>
              </Box>

              <Stack direction="row" spacing={1} sx={{ position: 'relative', zIndex: 1 }}>
                <Button
                  size="small"
                  startIcon={<RefreshIcon />}
                  onClick={handleRefreshStatus}
                  variant="outlined"
                  color={getSeverity()}
                  sx={{ borderRadius: '8px' }}
                >
                  Refresh
                </Button>
                <Button
                  size="small"
                  onClick={() => setExpanded(!expanded)}
                  variant="contained"
                  color={getSeverity()}
                  sx={{ borderRadius: '8px' }}
                >
                  {expanded ? 'Hide Details' : 'View Details'}
                </Button>
              </Stack>
            </Box>

            <Collapse in={expanded}>
              <Box sx={{ p: 3 }}>
                {hasNpcapIssue && (
                  <Paper
                    elevation={0}
                    sx={{
                      p: 3,
                      mb: 3,
                      borderRadius: '12px',
                      border: '1px solid',
                      borderColor: theme.palette.error.light,
                      backgroundColor: theme.palette.error.lighter,
                    }}
                  >
                    <Stack direction="row" spacing={2} alignItems="flex-start">
                      <ErrorIcon color="error" sx={{ mt: 0.5 }} />
                      <Box>
                        <Typography variant="subtitle1" fontWeight={600} gutterBottom>
                          Npcap Packet Capture Library Issue
                        </Typography>
                        
                        <Typography variant="body2" paragraph>
                          Npcap is required for network scanning and monitoring. {dependencies.npcapStatus?.status === 'not_installed' ? 
                            'It is not currently installed on your system.' : 
                            'It is installed but not properly configured.'}
                        </Typography>

                        <Stack spacing={2}>
                          {dependencies.npcapStatus?.status === 'not_installed' ? (
                            <Box>
                              <Typography variant="subtitle2" gutterBottom>
                                Installation Steps:
                              </Typography>
                              <List dense disablePadding>
                                <ListItem>
                                  <ListItemIcon sx={{ minWidth: 36 }}>
                                    <ArrowRightIcon fontSize="small" />
                                  </ListItemIcon>
                                  <ListItemText 
                                    primary={
                                      <>
                                        Download Npcap from the <Link href="https://npcap.com/#download" target="_blank" rel="noopener">official website</Link>
                                      </>
                                    }
                                  />
                                </ListItem>
                                <ListItem>
                                  <ListItemIcon sx={{ minWidth: 36 }}>
                                    <ArrowRightIcon fontSize="small" />
                                  </ListItemIcon>
                                  <ListItemText primary="Run the installer with administrator privileges" />
                                </ListItem>
                                <ListItem>
                                  <ListItemIcon sx={{ minWidth: 36 }}>
                                    <ArrowRightIcon fontSize="small" />
                                  </ListItemIcon>
                                  <ListItemText primary="Be sure to check the 'Install Npcap in WinPcap API-compatible Mode' option" />
                                </ListItem>
                                <ListItem>
                                  <ListItemIcon sx={{ minWidth: 36 }}>
                                    <ArrowRightIcon fontSize="small" />
                                  </ListItemIcon>
                                  <ListItemText primary="After installation, restart Network Monitor" />
                                </ListItem>
                              </List>
                            </Box>
                          ) : (
                            <Box>
                              <Typography variant="subtitle2" gutterBottom>
                                Configuration Issue:
                              </Typography>
                              <List dense disablePadding>
                                <ListItem>
                                  <ListItemIcon sx={{ minWidth: 36 }}>
                                    <ArrowRightIcon fontSize="small" />
                                  </ListItemIcon>
                                  <ListItemText primary="Npcap is installed but cannot be accessed by Network Monitor" />
                                </ListItem>
                                <ListItem>
                                  <ListItemIcon sx={{ minWidth: 36 }}>
                                    <ArrowRightIcon fontSize="small" />
                                  </ListItemIcon>
                                  <ListItemText 
                                    primary={
                                      <>
                                        Try reinstalling Npcap with the "WinPcap API-compatible Mode" option enabled
                                      </>
                                    }
                                  />
                                </ListItem>
                                <ListItem>
                                  <ListItemIcon sx={{ minWidth: 36 }}>
                                    <ArrowRightIcon fontSize="small" />
                                  </ListItemIcon>
                                  <ListItemText primary="Make sure you're running Network Monitor with administrator privileges" />
                                </ListItem>
                              </List>
                              
                              <Button
                                variant="contained"
                                color="primary"
                                startIcon={<SettingsIcon />}
                                onClick={handleFixNpcap}
                                sx={{ mt: 2, borderRadius: '8px' }}
                              >
                                Attempt Automatic Fix
                              </Button>
                              
                              {isNpcapFixed && (
                                <Alert severity="success" sx={{ mt: 2 }}>
                                  Fix attempted! Please restart Network Monitor.
                                </Alert>
                              )}
                            </Box>
                          )}
                        </Stack>
                        
                        <Box sx={{ mt: 2, p: 2, bgcolor: 'background.paper', borderRadius: '8px' }}>
                          <Typography variant="body2" color="text.secondary" sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                            <TipIcon fontSize="small" color="info" />
                            <span>
                              <strong>Tip:</strong> If you continue to have issues, try running Network Monitor as an administrator.
                            </span>
                          </Typography>
                        </Box>
                      </Box>
                    </Stack>
                  </Paper>
                )}

                {hasAdminIssue && (
                  <Paper
                    elevation={0}
                    sx={{
                      p: 3,
                      mb: 3,
                      borderRadius: '12px',
                      border: '1px solid',
                      borderColor: theme.palette.warning.light,
                      backgroundColor: theme.palette.warning.lighter,
                    }}
                  >
                    <Stack direction="row" spacing={2} alignItems="flex-start">
                      <AdminIcon color="warning" sx={{ mt: 0.5 }} />
                      <Box>
                        <Typography variant="subtitle1" fontWeight={600} gutterBottom>
                          Administrator Privileges Required
                        </Typography>
                        <Typography variant="body2" paragraph>
                          Some features of Network Monitor require administrator privileges to function properly.
                        </Typography>
                        <Typography variant="body2">
                          To run as administrator:
                        </Typography>
                        <List dense disablePadding>
                          <ListItem>
                            <ListItemIcon sx={{ minWidth: 36 }}>
                              <ArrowRightIcon fontSize="small" />
                            </ListItemIcon>
                            <ListItemText primary="Right-click the Network Monitor shortcut" />
                          </ListItem>
                          <ListItem>
                            <ListItemIcon sx={{ minWidth: 36 }}>
                              <ArrowRightIcon fontSize="small" />
                            </ListItemIcon>
                            <ListItemText primary="Select 'Run as administrator'" />
                          </ListItem>
                        </List>
                      </Box>
                    </Stack>
                  </Paper>
                )}

                {dependencies.missingDeps
                  .filter(dep => !dep.includes('Npcap'))
                  .map((dep) => (
                    <Paper
                      key={dep}
                      elevation={0}
                      sx={{
                        p: 3,
                        mb: 2,
                        borderRadius: '12px',
                        border: '1px solid',
                        borderColor: theme.palette.info.light,
                        backgroundColor: theme.palette.info.lighter,
                      }}
                    >
                      <Stack direction="row" spacing={2}>
                        <InfoIcon color="info" />
                        <Box>
                          <Typography variant="subtitle1" fontWeight={600}>
                            Missing Dependency: {dep}
                          </Typography>
                          <Typography variant="body2" sx={{ mt: 1 }}>
                            {dependencies.instructions[dep] || `Install ${dep} to enable all features.`}
                          </Typography>
                        </Box>
                      </Stack>
                    </Paper>
                  ))}

                {dependencies.warnings
                  .filter(warning => !warning.includes('administrative privileges'))
                  .map((warning, index) => (
                    <Paper
                      key={index}
                      elevation={0}
                      sx={{
                        p: 3,
                        mb: 2,
                        borderRadius: '12px',
                        border: '1px solid',
                        borderColor: theme.palette.info.light,
                        backgroundColor: theme.palette.info.lighter,
                      }}
                    >
                      <Stack direction="row" spacing={2}>
                        <InfoIcon color="info" />
                        <Typography variant="body2">{warning}</Typography>
                      </Stack>
                    </Paper>
                  ))}

                {showMoreDetails && dependencies.npcapStatus && (
                  <Paper
                    elevation={0}
                    sx={{
                      p: 3,
                      mt: 2,
                      borderRadius: '12px',
                      border: '1px solid',
                      borderColor: theme.palette.divider,
                      backgroundColor: theme.palette.background.default,
                    }}
                  >
                    <Typography variant="subtitle2" gutterBottom>
                      Npcap Detailed Information
                    </Typography>
                    <Box component="pre" sx={{ 
                      p: 2, 
                      bgcolor: 'background.paper', 
                      borderRadius: '8px',
                      overflowX: 'auto',
                      fontSize: '0.85rem',
                      fontFamily: 'monospace'
                    }}>
                      {JSON.stringify(dependencies.npcapStatus, null, 2)}
                    </Box>
                  </Paper>
                )}

                <Box sx={{ display: 'flex', justifyContent: 'space-between', mt: 2 }}>
                  <Button
                    size="small"
                    color="inherit"
                    onClick={() => setShowMoreDetails(!showMoreDetails)}
                    startIcon={<BugIcon />}
                  >
                    {showMoreDetails ? 'Hide Technical Details' : 'Show Technical Details'}
                  </Button>
                  
                  <Button
                    size="small"
                    color={getSeverity()}
                    variant="outlined"
                    onClick={handleRefreshStatus}
                    startIcon={<RefreshIcon />}
                    sx={{ borderRadius: '8px' }}
                  >
                    Check Again
                  </Button>
                </Box>
              </Box>
            </Collapse>
          </CardContent>
        </Card>
      </motion.div>
    </AnimatePresence>
  );
};

export default DependencyWarning;