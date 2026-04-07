/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./index.html",
    "./src/**/*.{vue,js,ts,jsx,tsx}", // 👉 这一句极其关键！如果没有这一句，Tailwind 什么样式都不会生成！
  ],
  darkMode: 'class',
  corePlugins: {
    preflight: false
  },
  theme: {
    extend: {
      colors: {
        error: '#ba1a1a',
        'tertiary-fixed-dim': '#59d5fb',
        'secondary-fixed': '#dce2f3',
        'surface-container-lowest': '#ffffff',
        'surface-container-low': '#f1f3ff',
        'primary-fixed': '#ffdbd0',
        'inverse-primary': '#ffb59d',
        'on-error-container': '#93000a',
        'on-primary': '#ffffff',
        'surface-container-high': '#e1e8fd',
        'outline-variant': '#e1bfb5',
        'primary-container': '#ff6b35',
        'on-surface': '#141b2b',
        'tertiary-fixed': '#b5ebff',
        outline: '#8d7168',
        'tertiary-container': '#00a7cb',
        'primary-fixed-dim': '#ffb59d',
        'on-secondary-fixed': '#151c27',
        'secondary-container': '#dce2f3',
        'inverse-on-surface': '#edf0ff',
        background: '#f9f9ff',
        'on-tertiary-fixed-variant': '#004e60',
        'on-tertiary-fixed': '#001f28',
        tertiary: '#00677e',
        'on-secondary-container': '#5e6572',
        'surface-tint': '#ab3500',
        'on-surface-variant': '#594139',
        'inverse-surface': '#293040',
        'on-tertiary': '#ffffff',
        'surface-dim': '#d3daef',
        'surface-container-highest': '#dce2f7',
        surface: '#f9f9ff',
        'on-secondary': '#ffffff',
        'on-primary-fixed-variant': '#832600',
        'error-container': '#ffdad6',
        'on-tertiary-container': '#003744',
        secondary: '#585f6c',
        'on-background': '#141b2b',
        'surface-bright': '#f9f9ff',
        'on-primary-container': '#5f1900',
        'surface-container': '#e9edff',
        'on-error': '#ffffff',
        'on-secondary-fixed-variant': '#404754',
        primary: '#ab3500',
        'on-primary-fixed': '#390c00',
        'surface-variant': '#dce2f7',
        'secondary-fixed-dim': '#c0c7d6'
      },
      borderRadius: {
        DEFAULT: '0.25rem',
        lg: '0.5rem',
        xl: '0.75rem',
        full: '9999px'
      },
      fontFamily: {
        headline: ['Plus Jakarta Sans', 'ui-sans-serif', 'system-ui'],
        body: ['Plus Jakarta Sans', 'ui-sans-serif', 'system-ui'],
        label: ['Plus Jakarta Sans', 'ui-sans-serif', 'system-ui']
      },
      fontSize: {
        'label-md': ['14px', { lineHeight: '20px', fontWeight: '500' }],
        'body-md': ['16px', { lineHeight: '24px' }]
      },
      boxShadow: {
        'cta': '0 8px 24px rgba(255,107,53,0.3)'
      }
    }
  },
  plugins: []
};
