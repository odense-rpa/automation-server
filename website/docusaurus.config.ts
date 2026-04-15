import {themes as prismThemes} from 'prism-react-renderer';
import type {Config} from '@docusaurus/types';
import type * as Preset from '@docusaurus/preset-classic';

const config: Config = {
  title: 'Automation Server',
  tagline: 'Build, run and monitor Python automations',
  favicon: 'img/favicon.svg',

  future: {
    v4: true,
  },

  url: 'https://odense-rpa.github.io',
  baseUrl: '/automation-server/',
  organizationName: 'odense-rpa',
  projectName: 'automation-server',
  trailingSlash: false,

  onBrokenLinks: 'throw',
  markdown: {
    hooks: {
      onBrokenMarkdownLinks: 'warn',
    },
  },

  i18n: {
    defaultLocale: 'en',
    locales: ['en'],
  },

  presets: [
    [
      'classic',
      {
        docs: {
          path: '../docs',
          routeBasePath: 'docs',
          sidebarPath: './sidebars.ts',
          editUrl: 'https://github.com/odense-rpa/automation-server/tree/main/',
        },
        blog: false,
        theme: {
          customCss: './src/css/custom.css',
        },
      } satisfies Preset.Options,
    ],
  ],

  themeConfig: {
    colorMode: {
      respectPrefersColorScheme: true,
    },
    navbar: {
      title: 'Automation Server',
      logo: {
        alt: 'Automation Server Logo',
        src: 'img/logo.svg',
      },
      items: [
        {
          type: 'docSidebar',
          sidebarId: 'docs',
          position: 'left',
          label: 'Docs',
        },
        {
          href: 'https://github.com/odense-rpa/automation-server',
          label: 'GitHub',
          position: 'right',
        },
      ],
    },
    footer: {
      style: 'dark',
      links: [
        {
          title: 'Docs',
          items: [
            { label: 'Getting Started', to: '/docs/getting-started/installation' },
            { label: 'Guides', to: '/docs/guides/writing-automations' },
            { label: 'Deployment', to: '/docs/deployment/docker' },
          ],
        },
        {
          title: 'Community',
          items: [
            { label: 'Discussions', href: 'https://github.com/odense-rpa/automation-server/discussions' },
            { label: 'Issues', href: 'https://github.com/odense-rpa/automation-server/issues' },
          ],
        },
        {
          title: 'More',
          items: [
            { label: 'GitHub', href: 'https://github.com/odense-rpa/automation-server' },
            { label: 'Changelog', href: 'https://github.com/odense-rpa/automation-server/blob/main/CHANGELOG.md' },
          ],
        },
      ],
      copyright: `Copyright © ${new Date().getFullYear()} Odense RPA. Built with Docusaurus.`,
    },
    prism: {
      theme: prismThemes.github,
      darkTheme: prismThemes.dracula,
      additionalLanguages: ['bash', 'python', 'yaml', 'docker', 'json'],
    },
  } satisfies Preset.ThemeConfig,
};

export default config;
