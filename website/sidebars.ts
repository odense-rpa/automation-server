import type {SidebarsConfig} from '@docusaurus/plugin-content-docs';

const sidebars: SidebarsConfig = {
  docs: [
    {
      type: 'category',
      label: 'Getting Started',
      collapsed: false,
      items: [
        'getting-started/installation',
        'getting-started/quick-start',
        'getting-started/configuration',
      ],
    },
    {
      type: 'category',
      label: 'Guides',
      items: [
        'guides/setup-a-process',
        'guides/writing-automations',
        'guides/scheduling',

        'guides/logging-and-audit',
      ],
    },
    'api',
    'contributing',
  ],
};

export default sidebars;
