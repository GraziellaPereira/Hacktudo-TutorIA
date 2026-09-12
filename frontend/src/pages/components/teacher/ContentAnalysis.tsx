import { useState } from 'react';

import styles from '../../../styles/contentAnalysis.module.css';

export interface ContentAnalysisData {
  content_id: string;
  title: string;
  summary: string;
  review_status: string;
  topics: Array<{
    id: string;
    name: string;
    description: string;
    learning_objectives: string[];
    concepts: string[];
  }>;
  learning_objectives: string[];
  concepts: string[];
  activities?: Array<{
    activity_id: string;
    question: string;
    options: string[];
    correct_answer: string;
    review_status: string;
  }>;
}

interface ContentAnalysisProps {
  analysis: ContentAnalysisData;
  onApprove: () => Promise<void>;
  onRefresh: () => Promise<void>;
}

type Activity = NonNullable<ContentAnalysisData['activities']>[number];

export default function ContentAnalysis({ analysis, onApprove, onRefresh }: ContentAnalysisProps) {
  const [approving, setApproving] = useState(false);
  const [selectedActivity, setSelectedActivity] = useState<Activity | null>(null);
  const [editing, setEditing] = useState(false);
  const [draftQuestion, setDraftQuestion] = useState('');
  const [busyId, setBusyId] = useState<string | null>(null);

  async function handleApprove() {
    setApproving(true);
    try {
      await onApprove();
    } finally {
      setApproving(false);
    }
  }

  async function reviewActivity(reviewStatus: string, question?: string) {
    if (!selectedActivity) return;
    setBusyId(selectedActivity.activity_id);
    try {
      const response = await fetch(`/api/activities/${selectedActivity.activity_id}/review`, {
        method: 'PATCH',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          review_status: reviewStatus,
          teacher_modified: Boolean(question),
          question,
        }),
      });
      if (!response.ok) throw new Error('Não foi possível atualizar a questão.');
      setSelectedActivity(null);
      setEditing(false);
      await onRefresh();
    } finally {
      setBusyId(null);
    }
  }

  async function regenerateActivity() {
    if (!selectedActivity) return;
    setBusyId(selectedActivity.activity_id);
    try {
      const response = await fetch(`/api/activities/${selectedActivity.activity_id}/regenerate`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ contentId: analysis.content_id }),
      });
      if (!response.ok) throw new Error('Não foi possível regenerar a questão.');
      setSelectedActivity(null);
      await onRefresh();
    } finally {
      setBusyId(null);
    }
  }

  function openActivity(activity: Activity) {
    setSelectedActivity(activity);
    setEditing(false);
    setDraftQuestion(activity.question);
  }

  return (
    <section className={styles.panel}>
      <header className={styles.header}>
        <div>
          <span className={styles.eyebrow}>Análise IA do conteúdo</span>
          <h1>{analysis.title}</h1>
        </div>
        <span className={styles.status}>{analysis.review_status}</span>
      </header>

      <div className={styles.section}>
        <h2>Resumo</h2>
        <p>{analysis.summary || 'Resumo não disponível.'}</p>
      </div>

      <div className={styles.section}>
        <h2>Tópicos encontrados</h2>
        <div className={styles.topicList}>
          {analysis.topics.map((topic) => (
            <article className={styles.topic} key={topic.id}>
              <h3>{topic.name}</h3>
              <p>{topic.description}</p>
            </article>
          ))}
        </div>
      </div>

      <div className={styles.columns}>
        <div className={styles.section}>
          <h2>Objetivos de aprendizagem</h2>
          <ul>
            {analysis.learning_objectives.map((item) => (
              <li key={item}>{item}</li>
            ))}
          </ul>
        </div>
        <div className={styles.section}>
          <h2>Conceitos</h2>
          <ul>
            {analysis.concepts.map((item) => (
              <li key={item}>{item}</li>
            ))}
          </ul>
        </div>
      </div>

      {analysis.activities && analysis.activities.length > 0 && (
        <div className={styles.section}>
          <h2>Questões geradas para revisão</h2>
          <p className={styles.helperText}>
            Clique em uma questão para abrir as opções de revisão.
          </p>
          <div className={styles.topicList}>
            {analysis.activities.map((activity, index) => (
              <article
                className={styles.activityCard}
                key={activity.activity_id}
                role="button"
                tabIndex={0}
                onClick={() => openActivity(activity)}
                onKeyDown={(event) => {
                  if (event.key === 'Enter' || event.key === ' ') openActivity(activity);
                }}
              >
                <h3>Questão {index + 1}</h3>
                <p>{activity.question}</p>
                <span className={styles.status}>{activity.review_status}</span>
              </article>
            ))}
          </div>
        </div>
      )}

      {selectedActivity && (
        <div className={styles.modalOverlay} onClick={() => setSelectedActivity(null)}>
          <div className={styles.activityModal} onClick={(event) => event.stopPropagation()}>
            <div className={styles.modalHeader}>
              <div>
                <span className={styles.eyebrow}>Revisão da questão</span>
                <h2>Questão selecionada</h2>
              </div>
              <button
                type="button"
                className={styles.closeButton}
                onClick={() => setSelectedActivity(null)}
              >
                ×
              </button>
            </div>
            {editing ? (
              <textarea
                className={styles.questionEditor}
                value={draftQuestion}
                onChange={(event) => setDraftQuestion(event.target.value)}
              />
            ) : (
              <p className={styles.modalQuestion}>{selectedActivity.question}</p>
            )}
            <h3>Alternativas</h3>
            <ol className={styles.optionsList}>
              {selectedActivity.options.map((option) => (
                <li key={option}>{option}</li>
              ))}
            </ol>
            <span className={styles.status}>{selectedActivity.review_status}</span>
            <div className={styles.modalActions}>
              {editing ? (
                <button
                  type="button"
                  className={styles.approveButton}
                  disabled={busyId !== null}
                  onClick={() => reviewActivity('edited', draftQuestion)}
                >
                  Salvar edição
                </button>
              ) : (
                <button
                  type="button"
                  className={styles.editButton}
                  onClick={() => setEditing(true)}
                >
                  Editar
                </button>
              )}
              {selectedActivity.review_status !== 'approved' && (
                <button
                  type="button"
                  className={styles.approveButton}
                  disabled={busyId !== null}
                  onClick={() => reviewActivity('approved')}
                >
                  Aprovar
                </button>
              )}
              <button
                type="button"
                className={styles.editButton}
                disabled={busyId !== null}
                onClick={regenerateActivity}
              >
                Regenerar
              </button>
            </div>
          </div>
        </div>
      )}

      <footer className={styles.actions}>
        <button type="button" className={styles.editButton}>
          Editar
        </button>
        <button
          type="button"
          className={styles.approveButton}
          onClick={handleApprove}
          disabled={approving || analysis.review_status === 'approved'}
        >
          {approving
            ? 'Aprovando...'
            : analysis.review_status === 'approved'
              ? 'Conteúdo aprovado'
              : 'Aprovar conteúdo'}
        </button>
      </footer>
    </section>
  );
}
