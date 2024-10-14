import { createTheme, responsiveFontSizes, ThemeOptions } from '@mui/material/styles';
import NextLink from 'next/link';
import {forwardRef} from "react";

const LinkBehaviour = forwardRef(function LinkBehaviour(props, ref) {
    // @ts-ignore
    return <NextLink ref={ref} {...props} />;
});

const themeOptions: ThemeOptions = {
    palette: {
        mode: 'dark',
        primary: {
            main: '#00FF1A',
            light: 'rgb(51, 255, 71)',
            dark: 'rgb(0, 178, 18)',
            contrastText: 'rgba(0, 0, 0, 0.87)',
        },
        secondary: {
            main: '#00ffff',
            light: 'rgb(51, 255, 255)',
            dark: 'rgb(0, 178, 178)',
            contrastText: 'rgba(0, 0, 0, 0.87)',
        },
        background: {
            default: '#121212',
            paper: '#1e1e1e',
        },
        text: {
            primary: '#ffffff',
            secondary: 'rgba(255, 255, 255, 0.7)',
            disabled: 'rgba(255, 255, 255, 0.5)',
            //hint: 'rgba(255, 255, 255, 0.5)',
        },
        error: {
            main: '#f44336',
            light: 'rgb(246, 104, 94)',
            dark: 'rgb(170, 46, 37)',
            contrastText: '#ffffff',
        },
        warning: {
            main: '#ff9800',
            light: '#ffb74d',
            dark: '#f57c00',
            contrastText: 'rgba(0, 0, 0, 0.87)',
        },
        info: {
            main: '#2196f3',
            light: '#64b5f6',
            dark: '#1976d2',
            contrastText: '#ffffff',
        },
        success: {
            main: '#4caf50',
            light: '#81c784',
            dark: '#388e3c',
            contrastText: 'rgba(0, 0, 0, 0.87)',
        },
    },
    typography: {
        fontFamily: [
            '-apple-system',
            'BlinkMacSystemFont',
            '"Segoe UI"',
            'Roboto',
            '"Helvetica Neue"',
            'Arial',
            'sans-serif',
            '"Apple Color Emoji"',
            '"Segoe UI Emoji"',
            '"Segoe UI Symbol"',
        ].join(','),
    },
    components: {
        MuiLink: {
            defaultProps: {
                component: LinkBehaviour
            }
        },
        MuiButtonBase: {
            defaultProps: {
                LinkComponent: LinkBehaviour
            }
        }
    }
};

let theme = createTheme(themeOptions);

theme = responsiveFontSizes(theme);

export { theme, themeOptions };
