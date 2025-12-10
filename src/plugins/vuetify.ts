import 'vuetify/styles';
import { createVuetify } from 'vuetify';
import { aliases, mdi } from 'vuetify/iconsets/mdi';

// Light Theme Configuration
const skewPlayTheme = {
    dark: false,
    colors: {
        background: '#F9FAFB',
        surface: '#FFFFFF',
        primary: '#4F46E5',
        'primary-darken-1': '#4338CA',
        secondary: '#0D9488',
        accent: '#8B5CF6',
        error: '#DC2626',
        info: '#2563EB',
        success: '#16A34A',
        warning: '#D97706',
        'on-background': '#18181B',
        'on-surface': '#27272A',
        'on-primary': '#FFFFFF',
        'on-secondary': '#FFFFFF',
    },
    variables: {
        'border-color': '#E4E4E7',
        'hover-opacity': 0.04,
    },
};

export default createVuetify({
    theme: {
        defaultTheme: 'skewPlayTheme',
        themes: {
            skewPlayTheme,
        },
    },
    icons: {
        defaultSet: 'mdi',
        aliases,
        sets: {
            mdi,
        },
    },
    // --- COMPONENT STYLING UPDATES ---
    defaults: {
        VCard: {
            elevation: 0,
            rounded: 'xl', // Modern "Super Rounded" corners (optional, change to 'lg' if you prefer)
            border: true,  // Very trendy right now (border instead of shadow)
        },
        VBtn: {
            elevation: 0,
            rounded: 'lg', // Slightly squarer buttons look more "Pro"
            fontWeight: '600',
            letterSpacing: '0.3px',
            height: 44,    // Taller buttons are easier to click
        },
        VTextField: {
            variant: 'outlined',
            color: 'primary',
            density: 'comfortable',
            rounded: 'lg',
            bgColor: 'surface', // Ensures inputs pop against the background
        },
        VChip: {
            rounded: 'md',
            fontWeight: '500',
            variant: 'tonal', // "Tonal" looks much more modern than solid/outlined
        },
        VNavigationDrawer: {
            elevation: 0,
            border: 'e',
            color: 'surface', // Ensures sidebar matches card color
        },
        VAppBar: {
            elevation: 0,
            border: 'b', // Adds a subtle line under the header
        }
    },
});