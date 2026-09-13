import Header from './Header';

import { useRouter } from 'next/router';

interface LayoutProps {
  children: React.ReactNode;
}

export default function Layout({ children }: LayoutProps) {
  const router = useRouter();

  return (
    <>
      {router.pathname !== '/' && <Header />}

      <main>{children}</main>
    </>
  );
}
