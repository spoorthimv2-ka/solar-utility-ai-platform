import type { Config } from 'tailwindcss'

const config: Config = {
  content: [
    './app/**/*.{js,ts,jsx,tsx,mdx}',
    './components/**/*.{js,ts,jsx,tsx,mdx}',
  ],
  theme: {
    extend: {
      colors: {
        background: '#0a0a0a', 
        electricBlue: '#00f0ff', 
      },
      boxShadow: {
        'glow': '0 0 15px -3px rgba(0, 240, 255, 0.4)',
        'glow-hover': '0 0 25px -3px rgba(0, 240, 255, 0.6)',
      }
    },
  },
  plugins: [],
}
export default config