import '@/styles/globals.css';
import '@xyflow/react/dist/style.css';

import type { AppProps } from 'next/app';

import Layout from './components/layout/Layout';

import { TeacherProvider } from '../context/TeacherContext';

export default function App({ Component, pageProps }: AppProps) {
  return (
    <TeacherProvider>
      <Layout>
        <Component {...pageProps} />
      </Layout>
    </TeacherProvider>
  );
}
