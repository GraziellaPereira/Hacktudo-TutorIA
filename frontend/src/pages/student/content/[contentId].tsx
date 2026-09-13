import { useEffect, useState } from 'react';
import { useRouter } from 'next/router';

import styles from '../../../styles/student.module.css';

type Method = 'flashcards' | 'mind_map' | 'infographic';

const methods: Array<{ id: Method; title: string; description: string }> = [
  {
    id: 'flashcards',
    title: 'Flashcards',
    description: 'Revise conceitos com perguntas e respostas.',
  },
  { id: 'mind_map', title: 'Mapa mental', description: 'Visualize relações entre os conceitos.' },
  { id: 'infographic', title: 'Infográfico', description: 'Estude em seções curtas e objetivas.' },
];

export default function StudentContentPage() {
  const router = useRouter();
  const { contentId } = router.query;
  const [data, setData] = useState<any>(null);
  const [summary, setSummary] = useState<any>(null);
  const [method, setMethod] = useState<Method | null>(null);
  const [material, setMaterial] = useState<any>(null);
  const [materialId, setMaterialId] = useState('');
  const [assessmentStarted, setAssessmentStarted] = useState(false);
  const [assessmentIndex, setAssessmentIndex] = useState(0);
  const [assessmentScore, setAssessmentScore] = useState(0);
  const [assessmentDone, setAssessmentDone] = useState(false);
  const [performance, setPerformance] = useState<any[]>([]);
  const [adaptiveResult, setAdaptiveResult] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [working, setWorking] = useState(false);
  const [error, setError] = useState('');

  useEffect(() => {
    const studentId = localStorage.getItem('student_id');
    if (typeof contentId !== 'string' || !studentId) return;

    async function loadContent() {
      const response = await fetch(`/api/students/${studentId}/contents/${contentId}`);
      const result = await response.json();
      if (!response.ok)
        throw new Error(result.detail ?? result.message ?? 'Erro ao carregar conteúdo');
      setData(result);

      const materialsResponse = await fetch(
        `/api/students/${studentId}/contents/${contentId}/materials`,
      );
      if (materialsResponse.ok) {
        const savedMaterials = await materialsResponse.json();
        if (savedMaterials[0]) {
          setMaterialId(savedMaterials[0].id);
          setMaterial(savedMaterials[0].material);
          setMethod(savedMaterials[0].method);
        }
      }
    }

    loadContent()
      .catch((requestError) => setError(requestError.message))
      .finally(() => setLoading(false));
  }, [contentId]);

  async function chooseMethod(selectedMethod: Method) {
    const studentId = localStorage.getItem('student_id');
    if (!studentId || typeof contentId !== 'string') return;

    setWorking(true);
    setError('');
    try {
      const methodResponse = await fetch(
        `/api/students/${studentId}/contents/${contentId}/method`,
        {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ method: selectedMethod }),
        },
      );
      const methodResult = await methodResponse.json();
      if (!methodResponse.ok) throw new Error(methodResult.detail ?? methodResult.message);
      setMethod(selectedMethod);

      const summaryResponse = await fetch(
        `/api/students/${studentId}/contents/${contentId}/summary`,
        { method: 'POST' },
      );
      const summaryResult = await summaryResponse.json();
      if (!summaryResponse.ok) throw new Error(summaryResult.detail ?? summaryResult.message);
      setSummary(summaryResult.summary);

      const materialsResponse = await fetch(
        `/api/students/${studentId}/contents/${contentId}/materials`,
        { method: 'POST' },
      );
      const materialsResult = await materialsResponse.json();
      if (!materialsResponse.ok) throw new Error(materialsResult.detail ?? materialsResult.message);
      setMaterial(materialsResult.material);
      setMaterialId(materialsResult.id);
    } catch (requestError) {
      setError(
        requestError instanceof Error
          ? requestError.message
          : 'Não foi possível preparar o material',
      );
    } finally {
      setWorking(false);
    }
  }

  async function answerActivity(selectedAnswer: string) {
    const studentId = localStorage.getItem('student_id');
    const activity = data.activities[assessmentIndex];
    if (!studentId || !materialId || !activity || typeof contentId !== 'string') return;

    const correct = selectedAnswer === activity.correct_answer;
    setWorking(true);
    try {
      const response = await fetch(`/api/students/${studentId}/materials/${materialId}/attempt`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          item_id: activity.id,
          item_type: 'activity',
          concept: activity.topic,
          correct,
        }),
      });
      if (!response.ok) throw new Error('Não foi possível registrar a resposta');

      if (correct) setAssessmentScore((score) => score + 1);
      if (assessmentIndex + 1 >= data.activities.length) {
        const performanceResponse = await fetch(`/api/students/${studentId}/performance`);
        if (performanceResponse.ok) setPerformance(await performanceResponse.json());
        const adaptiveResponse = await fetch(
          `/api/students/${studentId}/contents/${contentId}/adaptive`,
          { method: 'POST' },
        );
        if (adaptiveResponse.ok) setAdaptiveResult(await adaptiveResponse.json());
        setAssessmentDone(true);
      } else {
        setAssessmentIndex((index) => index + 1);
      }
    } catch (requestError) {
      setError(requestError instanceof Error ? requestError.message : 'Erro ao responder questão');
    } finally {
      setWorking(false);
    }
  }

  if (loading)
    return (
      <main className={styles.page}>
        <section className={styles.profilePanel}>
          <p>Carregando conteúdo...</p>
        </section>
      </main>
    );
  if (error && !data)
    return (
      <main className={styles.page}>
        <section className={styles.profilePanel}>
          <p className={styles.error}>{error}</p>
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
        <p className={styles.subtitle}>{data.content.original_text}</p>

        <div className={styles.contentList}>
          <h2>Resumo da IA</h2>
          <p>
            {summary?.summary ??
              data.content.summary ??
              'Escolha um método para gerar seu resumo personalizado.'}
          </p>
        </div>

        <div className={styles.contentList}>
          <h2>Tópicos e conceitos</h2>
          {data.topics.map((topic: any) => (
            <article className={styles.contentItem} key={topic.id}>
              <strong>{topic.name}</strong>
              <span>{topic.description}</span>
              <small>{topic.concepts.join(' · ')}</small>
            </article>
          ))}
        </div>

        <div className={styles.contentList}>
          <h2>Como você quer estudar?</h2>
          <div className={styles.methodGrid}>
            {methods.map((item) => (
              <button
                key={item.id}
                type="button"
                className={method === item.id ? styles.methodSelected : styles.methodButton}
                disabled={working}
                onClick={() => chooseMethod(item.id)}
              >
                <strong>{item.title}</strong>
                <span>{item.description}</span>
              </button>
            ))}
          </div>
        </div>

        {working && (
          <p className={styles.loadingMessage}>Preparando seu material personalizado...</p>
        )}
        {error && <p className={styles.error}>{error}</p>}
        {material && <LearningMaterial material={material} />}

        {data.activities.length > 0 && !assessmentStarted && !assessmentDone && (
          <div className={styles.contentList}>
            <h2>Avaliação</h2>
            <p>
              {data.activities.length} questões aprovadas pelo professor estão disponíveis depois do
              estudo.
            </p>
            <button
              type="button"
              className={styles.openButton}
              disabled={!materialId}
              onClick={() => setAssessmentStarted(true)}
            >
              Iniciar avaliação
            </button>
          </div>
        )}

        {assessmentStarted && !assessmentDone && (
          <div className={styles.assessmentPanel}>
            <span className={styles.eyebrow}>Avaliação</span>
            <h2>
              Questão {assessmentIndex + 1} de {data.activities.length}
            </h2>
            <p>{data.activities[assessmentIndex].question}</p>
            <div className={styles.answerList}>
              {data.activities[assessmentIndex].options.map((option: string) => (
                <button
                  key={option}
                  type="button"
                  disabled={working}
                  onClick={() => answerActivity(option)}
                >
                  {option}
                </button>
              ))}
            </div>
          </div>
        )}

        {assessmentDone && (
          <div className={styles.assessmentPanel}>
            <span className={styles.eyebrow}>Resultado</span>
            <h2>Avaliação concluída</h2>
            <p>
              Você acertou {assessmentScore} de {data.activities.length} questões.
            </p>
            {performance.length > 0 && (
              <div className={styles.contentList}>
                <h3>Desempenho por conceito</h3>
                {performance.map((item: any) => (
                  <span key={item.concept}>
                    {item.concept}: {Math.round((1 - item.error_rate) * 100)}% de acerto
                  </span>
                ))}
              </div>
            )}
            {adaptiveResult && (
              <div className={styles.contentItem}>
                <strong>Próximo passo recomendado</strong>
                <span>
                  {adaptiveResult.action ?? adaptiveResult.status ?? 'Continue estudando'}
                </span>
              </div>
            )}
          </div>
        )}
      </section>
    </main>
  );
}

function LearningMaterial({ material }: { material: any }) {
  return (
    <div className={styles.materialPanel}>
      <span className={styles.eyebrow}>Material personalizado</span>
      <h2>{material.title}</h2>
      <p>{material.summary}</p>

      {material.method === 'flashcards' && (
        <div className={styles.materialList}>
          {material.flashcards.map((card: any) => (
            <details className={styles.flashcard} key={card.id}>
              <summary>{card.question}</summary>
              <p>{card.answer}</p>
              <small>
                {card.concept} · dificuldade {card.difficulty}
              </small>
            </details>
          ))}
        </div>
      )}
      {material.method === 'mind_map' && (
        <div className={styles.materialList}>
          {material.mind_map.map((node: any) => (
            <MindMapNode key={node.id} node={node} />
          ))}
        </div>
      )}
      {material.method === 'infographic' && (
        <div className={styles.materialList}>
          {material.infographic_sections.map((section: any) => (
            <article className={styles.contentItem} key={section.id}>
              <strong>{section.title}</strong>
              <span>{section.content}</span>
              <small>{section.key_points.join(' · ')}</small>
            </article>
          ))}
        </div>
      )}
    </div>
  );
}

function MindMapNode({ node }: { node: any }) {
  return (
    <article className={styles.mindMapNode}>
      <strong>{node.title}</strong>
      <span>{node.summary}</span>
      {node.children?.map((child: any) => (
        <MindMapNode key={child.id} node={child} />
      ))}
    </article>
  );
}
