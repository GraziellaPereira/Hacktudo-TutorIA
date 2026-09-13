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
    id: string;
    topic: string;
    learning_objective: string;
    question: string;
    options: string[];
    correct_answer: string;
    explanation: string;
    hints: string[];
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
  const [draftTopic, setDraftTopic] = useState('');
  const [draftLearningObjective, setDraftLearningObjective] = useState('');
  const [draftOptions, setDraftOptions] = useState<string[]>([]);
  const [draftCorrectAnswer, setDraftCorrectAnswer] = useState('');
  const [draftExplanation, setDraftExplanation] = useState('');
  const [draftHints, setDraftHints] = useState<string[]>([]);
  const [editingContent, setEditingContent] = useState(false);
  const [draftTitle, setDraftTitle] = useState(analysis.title);
  const [draftSummary, setDraftSummary] = useState(analysis.summary);
  const [draftTopics, setDraftTopics] = useState(analysis.topics);
  const [savingContent, setSavingContent] = useState(false);
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
    setBusyId(selectedActivity.id);
    try {
      const response = await fetch(`/api/activities/${selectedActivity.id}/review`, {
        method: 'PATCH',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          review_status: reviewStatus,
          teacher_modified: Boolean(question),
          question,
          topic: draftTopic,
          learning_objective: draftLearningObjective,
          options: draftOptions,
          correct_answer: draftCorrectAnswer,
          explanation: draftExplanation,
          hints: draftHints,
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
    setBusyId(selectedActivity.id);
    try {
      const response = await fetch(`/api/activities/${selectedActivity.id}/regenerate`, {
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

  function openContentEditor() {
    setDraftTitle(analysis.title);
    setDraftSummary(analysis.summary);
    setDraftTopics(analysis.topics);
    setEditingContent(true);
  }

  async function saveContent() {
    if (!draftTitle.trim()) return;

    setSavingContent(true);

    try {
      const response = await fetch(`/api/contents/${analysis.content_id}`, {
        method: 'PATCH',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          title: draftTitle,
          summary: draftSummary,
          topics: draftTopics,
        }),
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.detail ?? data.message ?? 'Não foi possível editar o conteúdo.');
      }

      setEditingContent(false);
      await onRefresh();
    } finally {
      setSavingContent(false);
    }
  }

  function openActivity(activity: Activity) {
    setSelectedActivity(activity);
    setEditing(false);
    setDraftTopic(activity.topic);
    setDraftLearningObjective(activity.learning_objective);
    setDraftQuestion(activity.question);
    setDraftOptions([...activity.options]);
    setDraftCorrectAnswer(activity.correct_answer);
    setDraftExplanation(activity.explanation);
    setDraftHints([...activity.hints]);
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

      <div className={styles.contentCode}>
        <span>Código para compartilhar com o aluno</span>
        <strong>{analysis.content_id}</strong>
        <button type="button" onClick={() => navigator.clipboard.writeText(analysis.content_id)}>
          Copiar código
        </button>
      </div>

      <div className={styles.section}>
        <h2>Resumo</h2>

        {editingContent ? (
          <textarea
            className={styles.contentEditor}
            value={draftSummary}
            onChange={(event) => setDraftSummary(event.target.value)}
            aria-label="Resumo do conteúdo"
          />
        ) : (
          <p>{analysis.summary || 'Resumo não disponível.'}</p>
        )}
      </div>

      <div className={styles.section}>
        <h2>Tópicos encontrados</h2>
        <div className={styles.topicList}>
          {(editingContent ? draftTopics : analysis.topics).map((topic, topicIndex) => (
            <article className={styles.topic} key={topic.id}>
              {editingContent ? (
                <>
                  <input
                    className={styles.contentTitleEditor}
                    value={topic.name}
                    onChange={(event) =>
                      setDraftTopics((topics) =>
                        topics.map((item, index) =>
                          index === topicIndex ? { ...item, name: event.target.value } : item,
                        ),
                      )
                    }
                  />
                  <textarea
                    className={styles.contentEditor}
                    value={topic.description}
                    onChange={(event) =>
                      setDraftTopics((topics) =>
                        topics.map((item, index) =>
                          index === topicIndex
                            ? { ...item, description: event.target.value }
                            : item,
                        ),
                      )
                    }
                  />
                  <input
                    className={styles.contentTitleEditor}
                    value={topic.learning_objectives.join(', ')}
                    onChange={(event) =>
                      setDraftTopics((topics) =>
                        topics.map((item, index) =>
                          index === topicIndex
                            ? {
                                ...item,
                                learning_objectives: event.target.value
                                  .split(',')
                                  .map((value) => value.trim())
                                  .filter(Boolean),
                              }
                            : item,
                        ),
                      )
                    }
                    aria-label={`Objetivos de ${topic.name}`}
                  />
                  <input
                    className={styles.contentTitleEditor}
                    value={topic.concepts.join(', ')}
                    onChange={(event) =>
                      setDraftTopics((topics) =>
                        topics.map((item, index) =>
                          index === topicIndex
                            ? {
                                ...item,
                                concepts: event.target.value
                                  .split(',')
                                  .map((value) => value.trim())
                                  .filter(Boolean),
                              }
                            : item,
                        ),
                      )
                    }
                    aria-label={`Conceitos de ${topic.name}`}
                  />
                </>
              ) : (
                <>
                  <h3>{topic.name}</h3>
                  <p>{topic.description}</p>
                </>
              )}
            </article>
          ))}
        </div>
      </div>

      <div className={styles.columns}>
        <div className={styles.section}>
          <h2>Objetivos de aprendizagem</h2>
          <ul>
            {analysis.learning_objectives.map((objective) => (
              <li key={objective}>{objective}</li>
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
                key={activity.id}
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
              <>
                <input
                  className={styles.contentTitleEditor}
                  value={draftTopic}
                  onChange={(event) => setDraftTopic(event.target.value)}
                  aria-label="Tópico da questão"
                />
                <input
                  className={styles.contentTitleEditor}
                  value={draftLearningObjective}
                  onChange={(event) => setDraftLearningObjective(event.target.value)}
                  aria-label="Objetivo da questão"
                />
                <textarea
                  className={styles.questionEditor}
                  value={draftQuestion}
                  onChange={(event) => setDraftQuestion(event.target.value)}
                  aria-label="Pergunta"
                />
                <h3>Alternativas</h3>
                {draftOptions.map((option, index) => (
                  <input
                    key={index}
                    className={styles.contentTitleEditor}
                    value={option}
                    onChange={(event) =>
                      setDraftOptions((options) =>
                        options.map((item, optionIndex) =>
                          optionIndex === index ? event.target.value : item,
                        ),
                      )
                    }
                    aria-label={`Alternativa ${index + 1}`}
                  />
                ))}
                <input
                  className={styles.contentTitleEditor}
                  value={draftCorrectAnswer}
                  onChange={(event) => setDraftCorrectAnswer(event.target.value)}
                  aria-label="Resposta correta"
                />
                <textarea
                  className={styles.contentEditor}
                  value={draftExplanation}
                  onChange={(event) => setDraftExplanation(event.target.value)}
                  aria-label="Explicação"
                />
                {draftHints.map((hint, index) => (
                  <textarea
                    key={index}
                    className={styles.contentEditor}
                    value={hint}
                    onChange={(event) =>
                      setDraftHints((hints) =>
                        hints.map((item, hintIndex) =>
                          hintIndex === index ? event.target.value : item,
                        ),
                      )
                    }
                    aria-label={`Dica ${index + 1}`}
                  />
                ))}
              </>
            ) : (
              <p className={styles.modalQuestion}>{selectedActivity.question}</p>
            )}
            <h3>Alternativas</h3>
            <ol className={styles.optionsList}>
              {selectedActivity.options.map((option) => (
                <li key={option}>{option}</li>
              ))}
            </ol>
            {!editing && (
              <>
                <p>
                  <strong>Resposta correta:</strong> {selectedActivity.correct_answer}
                </p>
                <p>
                  <strong>Explicação:</strong> {selectedActivity.explanation}
                </p>
                <div>
                  <strong>Dicas:</strong>
                  <ul>
                    {selectedActivity.hints.map((hint, index) => (
                      <li key={`${index}-${hint}`}>{hint}</li>
                    ))}
                  </ul>
                </div>
              </>
            )}
            <span className={styles.status}>{selectedActivity.review_status}</span>
            <div className={styles.modalActions}>
              {editing ? (
                <button
                  type="button"
                  className={`${styles.modalButton} ${styles.modalSaveButton}`}
                  disabled={busyId !== null}
                  onClick={() => reviewActivity('edited', draftQuestion)}
                >
                  Salvar edição
                </button>
              ) : (
                <button
                  type="button"
                  className={`${styles.modalButton} ${styles.modalEditButton}`}
                  onClick={() => setEditing(true)}
                >
                  Editar
                </button>
              )}
              {selectedActivity.review_status !== 'approved' && (
                <button
                  type="button"
                  className={`${styles.modalButton} ${styles.modalApproveButton}`}
                  disabled={busyId !== null}
                  onClick={() => reviewActivity('approved')}
                >
                  Aprovar
                </button>
              )}
              <button
                type="button"
                className={`${styles.modalButton} ${styles.modalRegenerateButton}`}
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
        {editingContent ? (
          <>
            <input
              className={styles.contentTitleEditor}
              value={draftTitle}
              onChange={(event) => setDraftTitle(event.target.value)}
              aria-label="Título do conteúdo"
            />
            <button
              type="button"
              className={styles.editButton}
              onClick={() => setEditingContent(false)}
              disabled={savingContent}
            >
              Cancelar
            </button>
            <button
              type="button"
              className={styles.approveButton}
              onClick={saveContent}
              disabled={savingContent || !draftTitle.trim()}
            >
              {savingContent ? 'Salvando...' : 'Salvar edição'}
            </button>
          </>
        ) : (
          <button type="button" className={styles.editButton} onClick={openContentEditor}>
            Editar
          </button>
        )}
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
