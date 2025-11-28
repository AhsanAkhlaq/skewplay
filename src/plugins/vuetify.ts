import 'vuetify/styles';
import { createVuetify } from 'vuetify';
import { aliases, mdi } from 'vuetify/iconsets/mdi';

// --- 1. LIGHT THEME ---
const skewPlayTheme = {
  dark: false,
  colors: {
    background: '#F8FAFC', // Cool Grey
    surface: '#FFFFFF',    // Pure White
    // FIX: Use the DEEP purple here so it stands out against white
    primary: '#5E35B1',    
    'primary-darken-1': '#3700B3',
    secondary: '#00BFA5',  // Teal
    accent: '#7C4DFF',
    error: '#DC2626',
    info: '#0288D1',
    success: '#10B981',
    warning: '#F59E0B',
  },
  variables: {
    'border-color': '#E2E8F0',
    'hover-opacity': 0.04,
  },
};

// --- 2. DARK THEME ---
const skewPlayDarkTheme = {
  dark: true,
  colors: {
    background: '#0F172A', // Dark Navy
    surface: '#1E293B',    // Slate 800
    // FIX: Use the LIGHTER purple here so it pops against the dark background
    primary: '#5E35B1',    // Deep Purple (Brand Color) 
    secondary: '#22D3EE',  // Cyan (Glowing effect)
    accent: '#A78BFA',
    error: '#EF4444',
    info: '#3B82F6',
    success: '#34D399',
    warning: '#FBBF24',
  },
  variables: {
    'border-color': '#334155',
    'hover-opacity': 0.08,
  },
};

export default createVuetify({
  theme: {
    defaultTheme: 'skewPlayDarkTheme',
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
  defaults: {
    VCard: {
      elevation: 0,
      rounded: 'lg',
      border: true,
    },
    VBtn: {
      elevation: 0,
      rounded: 'pill',
      fontWeight: '600',
      letterSpacing: '0.5px',
    },
    VTextField: {
      variant: 'outlined',
      color: 'primary',
      density: 'comfortable',
      rounded: 'lg',
    },
    VChip: {
      rounded: 'lg',
      fontWeight: '500',
    },
    VNavigationDrawer: {
      elevation: 0,
      border: 'e',
    },
  },
});