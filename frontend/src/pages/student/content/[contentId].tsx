import { useEffect, useState } from 'react';
import { useRouter } from 'next/router';
import { Handle, MarkerType, Position, ReactFlow, type Edge, type Node } from '@xyflow/react';
import { FlashCard } from 'react-flashcards';
import {
  BookOpen,
  BriefcaseBusiness,
  CheckCircle2,
  GitBranch,
  Lightbulb,
  ListChecks,
  Scale,
} from 'lucide-react';

import styles from '../../../styles/student.module.css';

type Method = 'flashcards' | 'mind_map' | 'infographic';

type MindMapGraphData = {
  title: string;
  summary: string;
  level: number;
};

type MindMapGraphNode = Node<MindMapGraphData>;

type InfographicGraphData = {
  title: string;
  content: string;
  keyPoints: string[];
  iconIndex: number;
};

type InfographicGraphNode = Node<InfographicGraphData>;

const infographicIcons = [
  BookOpen,
  ListChecks,
  GitBranch,
  Lightbulb,
  BriefcaseBusiness,
  Scale,
  CheckCircle2,
];

const methods: Array<{ id: Method; title: string; description: string }> = [
  {
    id: 'flashcards',
    title: 'Flashcards',
    description: 'Revise conceitos com perguntas e respostas.',
  },
  { id: 'mind_map', title: 'Mapa mental', description: 'Visualize relações entre os conceitos.' },
  { id: 'infographic', title: 'Infográfico', description: 'Estude em seções curtas e objetivas.' },
];

function createMindMapGraph(material: any): { nodes: MindMapGraphNode[]; edges: Edge[] } {
  const nodes: MindMapGraphNode[] = [
    {
      id: 'mind-map-root',
      type: 'mindMap',
      position: { x: 0, y: 0 },
      sourcePosition: Position.Bottom,
      targetPosition: Position.Top,
      data: { title: material.title, summary: material.summary, level: 0 },
    },
  ];
  const edges: Edge[] = [];
  const rootNodes = material.mind_map ?? [];
  const branchSpacing = 380;
  const rootOffset = ((rootNodes.length - 1) * branchSpacing) / 2;

  function addChildren(node: any, parentId: string, x: number, y: number, level: number) {
    const children = node.children ?? [];
    const childSpacing = Math.max(220 - level * 18, 150);
    const childOffset = ((children.length - 1) * childSpacing) / 2;

    children.forEach((child: any, index: number) => {
      const childId = `mind-map-${child.id}`;
      const childX = x + index * childSpacing - childOffset;
      const childY = y + 190;
      nodes.push({
        id: childId,
        type: 'mindMap',
        position: { x: childX, y: childY },
        sourcePosition: Position.Bottom,
        targetPosition: Position.Top,
        data: { title: child.title, summary: child.summary, level },
      });
      edges.push({
        id: `${parentId}-${childId}`,
        source: parentId,
        target: childId,
        type: 'smoothstep',
        markerEnd: { type: MarkerType.ArrowClosed, color: '#9db1b8' },
      });
      addChildren(child, childId, childX, childY, level + 1);
    });
  }

  rootNodes.forEach((node: any, index: number) => {
    const nodeId = `mind-map-${node.id}`;
    const x = index * branchSpacing - rootOffset;
    const y = 240;
    nodes.push({
      id: nodeId,
      type: 'mindMap',
      position: { x, y },
      sourcePosition: Position.Bottom,
      targetPosition: Position.Top,
      data: { title: node.title, summary: node.summary, level: 1 },
    });
    edges.push({
      id: `mind-map-root-${nodeId}`,
      source: 'mind-map-root',
      target: nodeId,
      type: 'smoothstep',
      markerEnd: { type: MarkerType.ArrowClosed, color: '#9db1b8' },
    });
    addChildren(node, nodeId, x, y, 2);
  });

  return { nodes, edges };
}

function MindMapGraphNode({ data }: { data: MindMapGraphData }) {
  return (
    <div className={styles.mindMapFlowNode} data-level={data.level}>
      <Handle type="target" position={Position.Top} />
      <strong>{data.title}</strong>
      <span>{data.summary}</span>
      <Handle type="source" position={Position.Bottom} />
    </div>
  );
}

function createInfographicGraph(material: any): {
  nodes: InfographicGraphNode[];
  edges: Edge[];
} {
  const sections = material.infographic_sections ?? [];
  const nodes = sections.map((section: any, index: number) => ({
    id: `infographic-${section.id}`,
    type: 'infographic',
    position: { x: index % 2 === 0 ? -280 : 280, y: index * 190 },
    sourcePosition: Position.Bottom,
    targetPosition: Position.Top,
    data: {
      title: section.title,
      content: section.content,
      keyPoints: section.key_points,
      iconIndex: index,
    },
  }));
  const edges = sections.slice(1).map((section: any, index: number) => ({
    id: `infographic-edge-${sections[index].id}-${section.id}`,
    source: `infographic-${sections[index].id}`,
    target: `infographic-${section.id}`,
    type: 'smoothstep',
    markerEnd: { type: MarkerType.ArrowClosed, color: '#d7dfbd' },
  }));

  return { nodes, edges };
}

function InfographicGraphNode({ data }: { data: InfographicGraphData }) {
  const Icon = infographicIcons[data.iconIndex % infographicIcons.length];

  return (
    <article className={styles.infographicFlowNode}>
      <Handle type="target" position={Position.Top} />
      <header>
        <span>
          <Icon size={18} strokeWidth={2.1} />
        </span>
        <strong>{data.title}</strong>
      </header>
      <p>{data.content}</p>
      <div>
        <small>Pontos-chave</small>
        <ul>
          {data.keyPoints.map((point) => (
            <li key={point}>{point}</li>
          ))}
        </ul>
      </div>
      <Handle type="source" position={Position.Bottom} />
    </article>
  );
}

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
  const [visibleHintCount, setVisibleHintCount] = useState(0);
  const [performance, setPerformance] = useState<any[]>([]);
  const [adaptiveResult, setAdaptiveResult] = useState<any>(null);
  const [cycleAnalysis, setCycleAnalysis] = useState<any>(null);
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

      const methodResponse = await fetch(`/api/students/${studentId}/contents/${contentId}/method`);
      if (methodResponse.ok) {
        const methodResult = await methodResponse.json();
        setMethod(methodResult.preferred_method ?? methodResult.method ?? null);
      }

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
        if (adaptiveResponse.ok) {
          const adaptive = await adaptiveResponse.json();
          setCycleAnalysis({
            correct_answers: assessmentScore + (correct ? 1 : 0),
            errors: data.activities.length - assessmentScore - (correct ? 1 : 0),
            attempts: data.activities.length,
            accuracy: (assessmentScore + (correct ? 1 : 0)) / data.activities.length,
          });
          setAdaptiveResult(adaptive);
          if (adaptive.material) setMaterial(adaptive.material);
          if (adaptive.material_id) setMaterialId(adaptive.material_id);
          if (adaptive.recommended_method) setMethod(adaptive.recommended_method);

          if (adaptive.assessment?.continue && adaptive.assessment.activities?.length > 0) {
            setData((current: any) => ({
              ...current,
              activities: adaptive.assessment.activities,
            }));
            setAssessmentIndex(0);
            setAssessmentScore(0);
            setVisibleHintCount(0);
            setAssessmentStarted(true);
            setAssessmentDone(false);
          } else {
            setAssessmentDone(true);
          }
        } else {
          setAssessmentDone(true);
        }
      } else {
        setAssessmentIndex((index) => index + 1);
        setVisibleHintCount(0);
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
        <p className={styles.subtitle}>
          Conteúdo preparado pelo professor e materiais personalizados pela IA.
        </p>

        {data.content.has_attachment && (
          <div className={styles.contentItem}>
            <strong>Material original do professor</strong>
            <span>{data.content.attachment_name}</span>
            <a
              className={styles.openButton}
              href={`/api/contents/${contentId}/attachment`}
              download={data.content.attachment_name}
            >
              Baixar conteúdo original
            </a>
          </div>
        )}

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

        {adaptiveResult && (
          <div className={styles.contentItem}>
            <strong>
              {adaptiveResult.assessment?.continue
                ? 'Novo ciclo recomendado'
                : (adaptiveResult.message ?? 'Recomendação de estudo')}
            </strong>
            <span>Método recomendado: {adaptiveResult.recommended_method ?? 'Nenhum'}</span>
            <span>{adaptiveResult.reason}</span>
            {adaptiveResult.material_error && (
              <span className={styles.error}>{adaptiveResult.material_error}</span>
            )}
            {adaptiveResult.assessment_error && (
              <span className={styles.error}>{adaptiveResult.assessment_error}</span>
            )}
            {(cycleAnalysis || adaptiveResult.analysis) && (
              <div className={styles.contentList}>
                <strong>Análise do desempenho</strong>
                <span>Acertos: {(cycleAnalysis ?? adaptiveResult.analysis).correct_answers}</span>
                <span>Erros: {(cycleAnalysis ?? adaptiveResult.analysis).errors}</span>
                <span>
                  Precisão: {Math.round((cycleAnalysis ?? adaptiveResult.analysis).accuracy * 100)}%
                </span>
              </div>
            )}
            {adaptiveResult.assessment?.continue && (
              <button
                type="button"
                className={styles.openButton}
                onClick={() => {
                  setAssessmentStarted(false);
                  setAssessmentDone(true);
                }}
              >
                Sair da avaliação adaptativa
              </button>
            )}
          </div>
        )}

        {data.activities.length > 0 && !assessmentStarted && !assessmentDone && (
          <div className={styles.contentList}>
            <h2>Avaliação</h2>
            <p>{data.activities.length} questões estão disponíveis neste ciclo de avaliação.</p>
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
            {data.activities[assessmentIndex].hints?.length > 0 && (
              <div className={styles.contentItem}>
                <button
                  type="button"
                  className={styles.openButton}
                  disabled={
                    working || visibleHintCount >= data.activities[assessmentIndex].hints.length
                  }
                  onClick={() => setVisibleHintCount((count) => count + 1)}
                >
                  {visibleHintCount >= data.activities[assessmentIndex].hints.length
                    ? 'Todas as dicas exibidas'
                    : `Mostrar dica ${visibleHintCount + 1}`}
                </button>
                {data.activities[assessmentIndex].hints
                  .slice(0, visibleHintCount)
                  .map((hint: string, index: number) => (
                    <p key={`${index}-${hint}`}>
                      Dica {index + 1}: {hint}
                    </p>
                  ))}
              </div>
            )}
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
          </div>
        )}
      </section>
    </main>
  );
}

function LearningMaterial({ material }: { material: any }) {
  const [flashcardsOpen, setFlashcardsOpen] = useState(false);
  const [flashcardIndex, setFlashcardIndex] = useState(0);
  const [infographicOpen, setInfographicOpen] = useState(false);
  const [mindMapOpen, setMindMapOpen] = useState(false);
  const mindMapGraph = material.method === 'mind_map' ? createMindMapGraph(material) : null;
  const infographicGraph =
    material.method === 'infographic' ? createInfographicGraph(material) : null;

  return (
    <div className={styles.materialPanel}>
      <span className={styles.eyebrow}>Material personalizado</span>
      <h2>{material.title}</h2>
      <p>{material.summary}</p>

      {material.method === 'flashcards' && (
        <>
          <button
            type="button"
            className={styles.mindMapExpandButton}
            onClick={() => {
              setFlashcardIndex(0);
              setFlashcardsOpen(true);
            }}
          >
            Abrir flashcards
          </button>
          {flashcardsOpen && (
            <div
              className={styles.mindMapModal}
              role="dialog"
              aria-modal="true"
              aria-labelledby="flashcards-modal-title"
            >
              <section className={styles.mindMapModalPanel}>
                <header className={styles.mindMapModalHeader}>
                  <div>
                    <span className={styles.eyebrow}>Material personalizado</span>
                    <h2 id="flashcards-modal-title">{material.title}</h2>
                  </div>
                  <button
                    type="button"
                    className={styles.mindMapCloseButton}
                    onClick={() => setFlashcardsOpen(false)}
                  >
                    Fechar
                  </button>
                </header>
                <div className={styles.flashcardModalContent}>
                  <div className={styles.flashcardLibrary}>
                    <FlashCard
                      key={material.flashcards[flashcardIndex]?.id ?? flashcardIndex}
                      front={<strong>{material.flashcards[flashcardIndex]?.question}</strong>}
                      back={
                        <div className={styles.flashcardLibraryBack}>
                          <strong>{material.flashcards[flashcardIndex]?.answer}</strong>
                          <span>
                            {material.flashcards[flashcardIndex]?.concept} · dificuldade{' '}
                            {material.flashcards[flashcardIndex]?.difficulty}
                          </span>
                        </div>
                      }
                      timerDuration={0}
                      width="100%"
                      height="100%"
                      currentIndex={flashcardIndex}
                      flipped={false}
                      label={`Cartão ${flashcardIndex + 1}`}
                      showBookMark={false}
                      showTextToSpeech={false}
                      frontStyle={{ background: '#f7d96f' }}
                      backStyle={{ background: '#bde3d0' }}
                      frontContentStyle={{ color: '#33434c', padding: '28px' }}
                      backContentStyle={{ color: '#33434c', padding: '28px' }}
                    />
                    <div className={styles.flashcardNavigation}>
                      <button
                        type="button"
                        disabled={flashcardIndex === 0}
                        onClick={() => setFlashcardIndex((index) => Math.max(0, index - 1))}
                        aria-label="Cartão anterior"
                      >
                        Anterior
                      </button>
                      <span>
                        {flashcardIndex + 1} / {material.flashcards.length}
                      </span>
                      <button
                        type="button"
                        disabled={flashcardIndex === material.flashcards.length - 1}
                        onClick={() =>
                          setFlashcardIndex((index) =>
                            Math.min(material.flashcards.length - 1, index + 1),
                          )
                        }
                        aria-label="Próximo cartão"
                      >
                        Próximo
                      </button>
                    </div>
                  </div>
                </div>
              </section>
            </div>
          )}
        </>
      )}
      {material.method === 'mind_map' && (
        <>
          <button
            type="button"
            className={styles.mindMapExpandButton}
            onClick={() => setMindMapOpen(true)}
          >
            Abrir mapa mental
          </button>
          {mindMapOpen && (
            <div
              className={styles.mindMapModal}
              role="dialog"
              aria-modal="true"
              aria-labelledby="mind-map-modal-title"
            >
              <section className={styles.mindMapModalPanel}>
                <header className={styles.mindMapModalHeader}>
                  <div>
                    <span className={styles.eyebrow}>Material personalizado</span>
                    <h2 id="mind-map-modal-title">{material.title}</h2>
                  </div>
                  <button
                    type="button"
                    className={styles.mindMapCloseButton}
                    onClick={() => setMindMapOpen(false)}
                  >
                    Fechar
                  </button>
                </header>
                <div className={styles.infographicModalContent}>
                  <div className={styles.mindMapFlowCanvas}>
                    {mindMapGraph && (
                      <ReactFlow
                        nodes={mindMapGraph.nodes}
                        edges={mindMapGraph.edges}
                        nodeTypes={mindMapNodeTypes}
                        fitView
                        fitViewOptions={{ padding: 0.2, maxZoom: 1.1 }}
                        minZoom={0.25}
                        maxZoom={1.5}
                        proOptions={{ hideAttribution: true }}
                      />
                    )}
                  </div>
                </div>
              </section>
            </div>
          )}
        </>
      )}
      {material.method === 'infographic' && (
        <>
          <button
            type="button"
            className={styles.mindMapExpandButton}
            onClick={() => setInfographicOpen(true)}
          >
            Abrir infográfico
          </button>
          {infographicOpen && (
            <div
              className={styles.mindMapModal}
              role="dialog"
              aria-modal="true"
              aria-labelledby="infographic-modal-title"
            >
              <section className={styles.mindMapModalPanel}>
                <header className={styles.mindMapModalHeader}>
                  <div>
                    <span className={styles.eyebrow}>Material personalizado</span>
                    <h2 id="infographic-modal-title">{material.title}</h2>
                  </div>
                  <button
                    type="button"
                    className={styles.mindMapCloseButton}
                    onClick={() => setInfographicOpen(false)}
                  >
                    Fechar
                  </button>
                </header>
                <div className={styles.infographicModalContent}>
                  <div className={styles.infographicFlowCanvas}>
                    {infographicGraph && (
                      <ReactFlow
                        nodes={infographicGraph.nodes}
                        edges={infographicGraph.edges}
                        nodeTypes={infographicNodeTypes}
                        fitView
                        fitViewOptions={{ padding: 0.2, maxZoom: 0.95 }}
                        minZoom={0.25}
                        maxZoom={1.25}
                        proOptions={{ hideAttribution: true }}
                      />
                    )}
                  </div>
                </div>
              </section>
            </div>
          )}
        </>
      )}
    </div>
  );
}

const mindMapNodeTypes = { mindMap: MindMapGraphNode };
const infographicNodeTypes = { infographic: InfographicGraphNode };
