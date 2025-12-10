import 'vuetify/styles';
import { createVuetify } from 'vuetify';
import { aliases, mdi } from 'vuetify/iconsets/mdi';

// --- 1. LIGHT THEME (Clean & Airy) ---
const skewPlayTheme = {
    dark: false,
    colors: {
        // A neutral, warm gray base is more comfortable than stark white
        background: '#F9FAFB', // Gray 50
        surface: '#FFFFFF',    // Pure White

        // A sophisticated Indigo-Violet for that "ML/AI" vibe
        primary: '#4F46E5',    // Indigo 600
        'primary-darken-1': '#4338CA',

        // Teal is professional for data/secondary actions
        secondary: '#0D9488',  // Teal 600

        accent: '#8B5CF6',     // Violet 500
        error: '#DC2626',      // Red 600 (Less neon than default)
        info: '#2563EB',       // Blue 600
        success: '#16A34A',    // Green 600
        warning: '#D97706',    // Amber 600

        // TEXT: High contrast "Zinc" grays are easier to read
        'on-background': '#18181B', // Zinc 900
        'on-surface': '#27272A',    // Zinc 800
        'on-primary': '#FFFFFF',
        'on-secondary': '#FFFFFF',
    },
    variables: {
        'border-color': '#E4E4E7', // Zinc 200 (Subtle borders)
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