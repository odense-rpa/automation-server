import type {ReactNode} from 'react';
import Link from '@docusaurus/Link';
import useDocusaurusContext from '@docusaurus/useDocusaurusContext';
import Layout from '@theme/Layout';
import Heading from '@theme/Heading';

import styles from './index.module.css';

export default function Home(): ReactNode {
  const {siteConfig} = useDocusaurusContext();
  return (
    <Layout title={siteConfig.title} description={siteConfig.tagline}>
      <main className={styles.hero}>
        <Heading as="h1">{siteConfig.title}</Heading>
        <p className={styles.tagline}>{siteConfig.tagline}</p>
        <Link className="button button--primary button--lg" to="/docs/getting-started/installation">
          Get Started
        </Link>
      </main>
    </Layout>
  );
}
