const lightCodeTheme = require('prism-react-renderer/themes/github');
const darkCodeTheme = require('prism-react-renderer/themes/dracula');

/** @type {import('@docusaurus/types').DocusaurusConfig} */
module.exports = {
  title: 'MAGDA',
  tagline: 'Library for building Modular and Asynchronous Graphs with Directed and Acyclic edges',
  url: 'https://NeuroSYS-pl.github.io',
  baseUrl: '/magda/',
  onBrokenLinks: 'throw',
  onBrokenMarkdownLinks: 'warn',
  // TODO: Add favicon
  // favicon: 'img/favicon.ico',
  organizationName: 'NeuroSYS-pl',
  projectName: 'magda',
  themeConfig: {
    navbar: {
      title: 'MAGDA',
      // TODO: Add logo
      // logo: {
      //   alt: 'MAGDA Logo',
      //   src: 'img/logo.svg',
      // },
      items: [
        {
          type: 'doc',
          docId: 'intro',
          position: 'left',
          label: 'Tutorial',
        },
        {
          type: 'doc',
          docId: 'api/index',
          position: 'left',
          label: 'API',
        },
        {
          href: 'https://github.com/NeuroSYS-pl/magda',
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
            {
              label: 'Tutorial',
              to: '/docs/intro',
            },
          ],
        },
        {
          title: 'API',
          items: [
            {
              label: 'Module',
              to: '/docs/api/module',
            },
            {
              label: 'Pipeline',
              to: '/docs/api/pipeline',
            },
            {
              label: 'Config',
              to: '/docs/api/config',
            },
          ],
        },
        {
          title: 'More',
          items: [
            {
              label: 'GitHub',
              href: 'https://github.com/NeuroSYS-pl/magda',
            },
          ],
        },
      ],
      logo: {
        alt: 'NeuroSYS',
        src: 'https://neurosys.com/wp-content/themes/neurosys/static/images/logo-white.svg',
        href: 'https://neurosys.com/',
      },
      copyright: `Copyright © ${new Date().getFullYear()} NeuroSYS, Built with Docusaurus.`,
    },
    prism: {
      theme: lightCodeTheme,
      darkTheme: darkCodeTheme,
    },
  },
  presets: [
    [
      '@docusaurus/preset-classic',
      {
        docs: {
          sidebarPath: require.resolve('./sidebars.js'),
          editUrl: 'https://github.com/NeuroSYS-pl/magda/edit/main/website/',
        },
        theme: {
          customCss: require.resolve('./src/css/custom.css'),
        },
      },
    ],
  ],
};
