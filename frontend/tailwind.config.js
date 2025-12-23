/** @type {import('tailwindcss').Config} */
export default {
    content: [
        "./index.html",
        "./src/**/*.{vue,js,ts,jsx,tsx}",
    ],
    darkMode: 'class',
    theme: {
        extend: {
            colors: {
                primary: '#4f46e5',
                'primary-hover': '#4338ca',
                'primary-light': '#e0e7ff',
            },
        },
    },
    plugins: [],
}
