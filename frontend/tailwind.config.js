/** @type {import('tailwindcss').Config} */
export default {
    content: [
        "./index.html",
        "./src/**/*.{svelte,js,ts,jsx,tsx}",
    ],
    theme: {
        extend: {},
    },
    plugins: [
        require('daisyui'),
    ],
    daisyui: {
        themes: [
            {
                light: {
                    ...require("daisyui/src/theming/themes")["light"],
                    primary: "#667eea",
                    secondary: "#764ba2",
                    accent: "#f59e0b",
                    neutral: "#3d4451",
                    "base-100": "#ffffff",
                },
            },
        ],
    },
}
