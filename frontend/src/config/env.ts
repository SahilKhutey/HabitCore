import Constants from 'expo-constants';

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
    API_URL: "http://localhost:8000",
    ENV_NAME: "Development",
  },
};

const getEnvVars = (env = Constants.expoConfig?.extra?.APP_ENV) => {
  if (env === 'production') return ENV.production;
  if (env === 'staging') return ENV.staging;
  return ENV.development;
};

export default getEnvVars();
