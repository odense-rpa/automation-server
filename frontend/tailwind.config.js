import daisyui from 'daisyui';

export default {
  content: ['./src/**/*.{vue,js,ts}'],
  plugins: [daisyui],

    daisyui: {
        styled: true,
        themes: true,
        base: true,
        utils: true,
        logs: true,
        rtl: false,
    },

};