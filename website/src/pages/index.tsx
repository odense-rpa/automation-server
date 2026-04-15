import type {ReactNode} from 'react';
import clsx from 'clsx';
import Link from '@docusaurus/Link';
import useDocusaurusContext from '@docusaurus/useDocusaurusContext';
import Layout from '@theme/Layout';
import Heading from '@theme/Heading';

import styles from './index.module.css';

type FeatureItem = {
  title: string;
  description: ReactNode;
};

const features: FeatureItem[] = [
  {
    title: 'Web Interface',
    description: 'Monitor running automations, inspect workqueue items, view audit logs, and manage schedules — all from a clean browser-based UI.',
  },
  {
    title: 'Powerful Scheduling',
    description: 'Trigger automations on a cron schedule, at a specific date and time, or based on pending items in a workqueue.',
  },
  {
    title: 'Audit Trail',
    description: 'Every execution is logged. Python\'s standard logging module integrates directly, grouping all output by session for easy inspection.',
  },
];

function HomepageHeader() {
  const {siteConfig} = useDocusaurusContext();
  return (
    <header className={clsx('hero hero--primary', styles.heroBanner)}>
      <div className="container">
        <Heading as="h1" className="hero__title">{siteConfig.title}</Heading>
        <p className="hero__subtitle">{siteConfig.tagline}</p>
        <div className={styles.buttons}>
          <Link className="button button--secondary button--lg" to="/docs/getting-started/installation">
            Get Started
          </Link>
        </div>
      </div>
    </header>
  );
}

function Feature({title, description}: FeatureItem) {
  return (
    <div className={clsx('col col--4')}>
      <div className="text--center padding-horiz--md padding-vert--md">
        <Heading as="h3">{title}</Heading>
        <p>{description}</p>
      </div>
    </div>
  );
}

export default function Home(): ReactNode {
  const {siteConfig} = useDocusaurusContext();
  return (
    <Layout title={siteConfig.title} description={siteConfig.tagline}>
      <HomepageHeader />
      <main>
        <section className={styles.features}>
          <div className="container">
            <div className="row">
              {features.map((props, idx) => (
                <Feature key={idx} {...props} />
              ))}
            </div>
            <div className={clsx('row', styles.screenshotRow)}>
              <div className="col">
                <img src="/automation-server/img/main-interface.png" alt="Automation Server web interface" className={styles.screenshot} />
              </div>
            </div>
          </div>
        </section>
      </main>
    </Layout>
  );
}
