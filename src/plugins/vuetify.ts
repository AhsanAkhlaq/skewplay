import 'vuetify/styles';
import { createVuetify } from 'vuetify';
import { aliases, mdi } from 'vuetify/iconsets/mdi';

const skewPlayTheme = {
  dark: false,
  colors: {
    background: '#F3E5F5',
    surface: '#FFFFFF',
    primary: '#5E35B1',
    'primary-darken-1': '#45278F',
    secondary: '#7E57C2',
    accent: '#00BFA5',
    error: '#E53935',
    info: '#29B6F6',
    success: '#26A69A',
    warning: '#FFC107',
  },
};

const skewPlayDarkTheme = {
  dark: true,
  colors: {
    background: '#121212',
    surface: '#1E1B2E',
    primary: '#B39DDB',
    secondary: '#9575CD',
    accent: '#26A69A',
    error: '#EF5350',
    info: '#4FC3F7',
    success: '#81C784',
    warning: '#FFD54F',
  },
};

export default createVuetify({
  theme: {
    defaultTheme: 'skewPlayTheme',
    themes: {
      skewPlayTheme,
      skewPlayDarkTheme,
    },
  },
  icons: {
    defaultSet: 'mdi',
    aliases,
    sets: {
      mdi,
    },
  },
});

