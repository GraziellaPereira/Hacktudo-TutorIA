import { LogOut } from 'lucide-react';
import { useRouter } from 'next/router';

import styles from '../../../styles/header.module.css';

export default function Header() {
  const router = useRouter();

  function handleLogout() {
    localStorage.removeItem('student_id');
    localStorage.removeItem('teacher_id');
    localStorage.removeItem('teacher');
    void router.push('/');
  }

  return (
    <header className={styles.header}>
      <div className={styles.logo}>🏫 Logo Escola</div>
      <button type="button" className={styles.logoutButton} onClick={handleLogout}>
        <LogOut size={17} strokeWidth={2.2} aria-hidden="true" />
        <span>Sair</span>
      </button>
    </header>
  );
}
