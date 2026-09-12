import { useEffect, useState } from 'react';

import { useRouter } from 'next/router';

import styles from '../../../styles/student.module.css';

export default function StudentContentPage() {
  const router = useRouter();
  const { contentId } = router.query;
  const [data, setData] = useState<any>(null);
  const [error, setError] = useState('');

  useEffect(() => {
    const studentId = localStorage.getItem('student_id');
    if (typeof contentId !== 'string' || !studentId) return;

    fetch(`/api/students/${studentId}/contents/${contentId}`)
      .then(async (response) => {
        const result = await response.json();
        if (!response.ok)
          throw new Error(result.detail ?? result.message ?? 'Erro ao carregar conteúdo');
        return result;
      })
      .then(setData)
      .catch((requestError) => setError(requestError.message));
  }, [contentId]);

  if (error)
    return (
      <main className={styles.page}>
        <section className={styles.profilePanel}>
          <p className={styles.error}>{error}</p>
        </section>
      </main>
    );
  if (!data)
    return (
      <main className={styles.page}>
        <section className={styles.profilePanel}>
          <p>Carregando conteúdo...</p>
        </section>
      </main>
    );

  return (
    <main className={styles.page}>
      <section className={styles.profilePanel}>
        <button type="button" className={styles.backButton} onClick={() => router.push('/student')}>
          Voltar
        </button>
        <span className={styles.eyebrow}>Conteúdo de aprendizagem</span>
        <h1>{data.content.title}</h1>
        <p className={styles.subtitle}>{data.content.summary || 'Resumo ainda não disponível.'}</p>

        <div className={styles.contentList}>
          <h2>Tópicos</h2>
          {data.topics.map((topic: any) => (
            <article className={styles.contentItem} key={topic.id}>
              <strong>{topic.name}</strong>
              <span>{topic.description}</span>
            </article>
          ))}
        </div>

        {data.activities.length > 0 && (
          <div className={styles.contentList}>
            <h2>Atividades</h2>
            {data.activities.map((activity: any, index: number) => (
              <article className={styles.contentItem} key={activity.id}>
                <strong>Questão {index + 1}</strong>
                <span>{activity.question}</span>
              </article>
            ))}
          </div>
        )}
      </section>
    </main>
  );
}
