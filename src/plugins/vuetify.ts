import 'vuetify/styles';
import { createVuetify } from 'vuetify';
import { aliases, mdi } from 'vuetify/iconsets/mdi';

// --- 1. LIGHT THEME ---
const skewPlayTheme = {
  dark: false,
  colors: {
    background: '#F8FAFC', // Slate 50
    surface: '#FFFFFF',    // White
    primary: '#4F46E5',    // Indigo 600
    'primary-darken-1': '#4338ca',
    secondary: '#0EA5E9',  // Sky 500
    accent: '#8B5CF6',     // Violet 500
    error: '#EF4444',
    info: '#3B82F6',
    success: '#10B981',
    warning: '#F59E0B',

    // TEXT COLORS
    'on-background': '#0F172A', // Slate 900
    'on-surface': '#1E293B',    // Slate 800
    'on-primary': '#FFFFFF',    // White
    'on-secondary': '#FFFFFF',  // White
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
    background: '#0F172A', // Slate 900
    surface: '#1E293B',    // Slate 800
    primary: '#6366F1',    // Indigo 500
    secondary: '#38BDF8',  // Sky 400
    accent: '#A78BFA',     // Violet 400
    error: '#F87171',
    info: '#60A5FA',
    success: '#34D399',
    warning: '#FBBF24',

    // TEXT COLORS
    'on-background': '#F8FAFC', // Slate 50
    'on-surface': '#E2E8F0',    // Slate 200
    'on-primary': '#FFFFFF',    // White
    'on-secondary': '#0F172A',  // Slate 900
  },
  variables: {
    'border-color': '#334155',
    'hover-opacity': 0.08,
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