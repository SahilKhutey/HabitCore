import Constants from 'expo-constants';
import { Platform } from 'react-native';

// In development, we use the local IP address if on mobile, or localhost if on web.
// This ensures the app can connect to the backend from a real device.
const getLocalHost = () => {
  if (Platform.OS === 'web') return 'localhost';
  
  // Try to get the host from debugger or debugger address
  const debuggerHost = Constants.expoConfig?.hostUri?.split(':').shift();
  return debuggerHost || '127.0.0.1'; // Fallback
};

const ENV = {
  staging: {
    API_URL: "https://staging-api.habithero.com",
    ENV_NAME: "Staging",
  },
  production: {
    API_URL: "https://api.habithero.com",
    ENV_NAME: "Production",
  },
  development: {
    API_URL: `http://${getLocalHost()}:8000`, // Backend runs on 8000
    ENV_NAME: "Development",
  },
};

const getEnvVars = (env = Constants.expoConfig?.extra?.APP_ENV) => {
  if (env === 'production') return ENV.production;
  if (env === 'staging') return ENV.staging;
  return ENV.development;
};

export default getEnvVars();
