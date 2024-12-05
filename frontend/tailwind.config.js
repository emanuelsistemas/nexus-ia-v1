const { fontFamily } = require("tailwindcss/defaultTheme");

module.exports = {
  content: ["./src/**/*.{js,jsx,ts,tsx}"],
  darkMode: "class",
  theme: {
    extend: {
      colors: {
        background: "#0A0820",
        card: "#221941",
        primary: "#7C3AED",
        secondary: "#4C1D95",
        accent: "#8B5CF6",
        border: "#2D2160",
      },
      fontFamily: {
        sans: ["Inter", ...fontFamily.sans],
        display: ["Clash Display", ...fontFamily.sans],
      },
      typography: (theme) => ({
        DEFAULT: {
          css: {
            color: theme("colors.gray.200"),
            a: {
              color: theme("colors.primary"),
              "&:hover": {
                color: theme("colors.accent"),
              },
            },
            h1: {
              color: theme("colors.white"),
            },
            h2: {
              color: theme("colors.white"),
            },
            h3: {
              color: theme("colors.white"),
            },
            h4: {
              color: theme("colors.white"),
            },
            strong: {
              color: theme("colors.white"),
            },
            code: {
              color: theme("colors.accent"),
            },
            figcaption: {
              color: theme("colors.gray.400"),
            },
            blockquote: {
              color: theme("colors.gray.200"),
            },
          },
        },
      }),
    },
  },
  plugins: [
    require("@tailwindcss/typography"),
  ],
};

