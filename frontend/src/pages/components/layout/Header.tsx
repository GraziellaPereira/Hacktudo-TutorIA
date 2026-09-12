import styles from '../../../styles/header.module.css';

export default function Header() {
  return (
    <header className={styles.header}>
      <div className={styles.logo}>🏫 Logo Escola</div>

      <nav className={styles.nav}>
        <span className={styles.item}>Portal Ensino</span>

        <span className={styles.item}>Dashboard Ensino</span>

        <span className={styles.item}>Professor 👤</span>
      </nav>
    </header>
  );
}
