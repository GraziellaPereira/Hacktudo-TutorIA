import { useEffect, useState } from 'react';

import { useRouter } from 'next/router';

import ContentAnalysis, { ContentAnalysisData } from '../../../components/teacher/ContentAnalysis';
import styles from '../../../../styles/contentAnalysis.module.css';

export default function ContentAnalysisPage() {
  const router = useRouter();
  const { id } = router.query;
  const [analysis, setAnalysis] = useState<ContentAnalysisData | null>(null);
  const [error, setError] = useState('');

  useEffect(() => {
    if (typeof id !== 'string') return;

    fetch(`/api/contents/${id}/analysis`)
      .then(async (response) => {
        const data = await response.json();
        if (!response.ok)
          throw new Error(data.detail ?? data.message ?? 'Erro ao carregar análise');
        return data;
      })
      .then(setAnalysis)
      .catch((requestError) => setError(requestError.message));
  }, [id]);

  async function approveContent() {
    if (typeof id !== 'string') return;

    const response = await fetch(`/api/contents/${id}/analysis`, { method: 'POST' });
    const data = await response.json();
    if (!response.ok) throw new Error(data.detail ?? data.message ?? 'Erro ao aprovar conteúdo');
    setAnalysis(data);
  }

  async function refreshAnalysis() {
    if (typeof id !== 'string') return;
    const response = await fetch(`/api/contents/${id}/analysis`);
    const data = await response.json();
    if (!response.ok) throw new Error(data.detail ?? data.message ?? 'Erro ao atualizar análise');
    setAnalysis(data);
  }

  if (error)
    return (
      <main className={styles.page}>
        <p>{error}</p>
      </main>
    );
  if (!analysis)
    return (
      <main className={styles.page}>
        <p>Carregando análise da IA...</p>
      </main>
    );

  return (
    <main className={styles.page}>
      <button
        type="button"
        className={styles.backToTeacherButton}
        onClick={() => router.push('/teacher')}
      >
        ← Voltar para área do professor
      </button>
      <ContentAnalysis analysis={analysis} onApprove={approveContent} onRefresh={refreshAnalysis} />
    </main>
  );
}
