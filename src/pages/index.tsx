import Link from 'next/link';

import styles from '../styles/home.module.css';

export default function Home() {
  return (
    <main className={styles.container}>
      <div className={styles.card}>
        <h1>📚 Tutor IA</h1>

        <p>Plataforma inteligente para professores organizarem conteúdos e criarem materiais.</p>

        <Link href="/register">
          <button className={styles.button}>Cadastrar Professor</button>
        </Link>
      </div>
    </main>
  );
}
