import { FormEvent, useEffect, useState } from 'react';
import { useRouter } from 'next/router';

import styles from '../styles/student.module.css';

interface Student {
  id: string;
  name: string;
  education_level: string;
  grade_or_period: string;
  created_at: string;
}

interface StudentContent {
  id: string;
  title: string;
  subject: string;
  education_level: string;
  grade_or_period: string;
}

const educationLevels = [
  'Ensino Fundamental I',
  'Ensino Fundamental II',
  'Ensino Médio',
  'Ensino Técnico',
  'Faculdade',
];

export default function StudentPage() {
  const router = useRouter();
  const [student, setStudent] = useState<Student | null>(null);
  const [contents, setContents] = useState<StudentContent[]>([]);
  const [contentId, setContentId] = useState('');
  const [contentError, setContentError] = useState('');
  const [addingContent, setAddingContent] = useState(false);
  const [name, setName] = useState('');
  const [educationLevel, setEducationLevel] = useState('');
  const [gradeOrPeriod, setGradeOrPeriod] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  useEffect(() => {
    const studentId = localStorage.getItem('student_id');
    if (!studentId) return;

    fetch(`/api/students/${studentId}`)
      .then(async (response) => {
        if (!response.ok) throw new Error('Aluno não encontrado');
        return response.json();
      })
      .then(async (profile) => {
        setStudent(profile);
        const contentsResponse = await fetch(`/api/students/${studentId}/contents`);
        if (contentsResponse.ok) setContents(await contentsResponse.json());
      })
      .catch(() => localStorage.removeItem('student_id'));
  }, []);

  async function handleAddContent(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const studentId = student?.id;
    if (!studentId || !contentId.trim()) return;

    setAddingContent(true);
    setContentError('');
    try {
      const response = await fetch(`/api/students/${studentId}/contents`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ contentId }),
      });
      const data = await response.json();
      if (!response.ok)
        throw new Error(data.detail ?? data.message ?? 'Não foi possível adicionar o conteúdo');
      setContents((current) =>
        current.some((item) => item.id === data.id) ? current : [data, ...current],
      );
      setContentId('');
    } catch (requestError) {
      setContentError(
        requestError instanceof Error ? requestError.message : 'Erro ao adicionar conteúdo',
      );
    } finally {
      setAddingContent(false);
    }
  }

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setError('');

    if (!name.trim() || !educationLevel || !gradeOrPeriod.trim()) {
      setError('Preencha nome, nível de ensino e série/período.');
      return;
    }

    setLoading(true);
    try {
      const response = await fetch('/api/students', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ name, educationLevel, gradeOrPeriod }),
      });
      const data = await response.json();
      if (!response.ok) throw new Error(data.detail ?? data.message ?? 'Erro ao criar aluno');

      localStorage.setItem('student_id', data.student_id);
      const profileResponse = await fetch(`/api/students/${data.student_id}`);
      setStudent(await profileResponse.json());
    } catch (requestError) {
      setError(requestError instanceof Error ? requestError.message : 'Erro ao criar aluno');
    } finally {
      setLoading(false);
    }
  }

  if (student) {
    return (
      <main className={styles.page}>
        <section className={styles.profilePanel}>
          <span className={styles.eyebrow}>Contexto do aluno</span>
          <h1>Olá, {student.name}</h1>
          <p className={styles.subtitle}>Seu perfil de aprendizagem está pronto.</p>

          <div className={styles.contextGrid}>
            <div>
              <span>Nível de ensino</span>
              <strong>{student.education_level}</strong>
            </div>
            <div>
              <span>Série ou período</span>
              <strong>{student.grade_or_period}</strong>
            </div>
          </div>

          <div className={styles.emptyState}>
            <h2>Conteúdos de aprendizagem</h2>
            <p>Use o código compartilhado pelo professor para acessar um conteúdo aprovado.</p>
            <form className={styles.contentForm} onSubmit={handleAddContent}>
              <label htmlFor="content-id">Código do conteúdo</label>
              <div className={styles.contentInputRow}>
                <input
                  id="content-id"
                  value={contentId}
                  onChange={(event) => setContentId(event.target.value)}
                  placeholder="Cole o content_id aqui"
                />
                <button type="submit" disabled={addingContent}>
                  {addingContent ? 'Adicionando...' : 'Adicionar'}
                </button>
              </div>
              {contentError && <p className={styles.error}>{contentError}</p>}
            </form>

            {contents.length > 0 && (
              <div className={styles.contentList}>
                {contents.map((content) => (
                  <article key={content.id} className={styles.contentItem}>
                    <div>
                      <strong>{content.title}</strong>
                      <span>
                        {content.subject} · {content.grade_or_period}
                      </span>
                    </div>
                    <small>{content.id}</small>
                    <button
                      type="button"
                      className={styles.openButton}
                      onClick={() => router.push(`/student/content/${content.id}`)}
                    >
                      Abrir conteúdo
                    </button>
                  </article>
                ))}
              </div>
            )}
          </div>
        </section>
      </main>
    );
  }

  return (
    <main className={styles.page}>
      <section className={styles.formPanel}>
        <span className={styles.eyebrow}>Área do aluno</span>
        <h1>Criar meu contexto</h1>
        <p className={styles.subtitle}>
          Informe seus dados para personalizar sua experiência de aprendizagem.
        </p>

        <form onSubmit={handleSubmit}>
          <label htmlFor="student-name">Nome</label>
          <input
            id="student-name"
            value={name}
            onChange={(event) => setName(event.target.value)}
            placeholder="Como você se chama?"
          />

          <label htmlFor="education-level">Nível de ensino</label>
          <select
            id="education-level"
            value={educationLevel}
            onChange={(event) => setEducationLevel(event.target.value)}
          >
            <option value="">Selecione seu nível</option>
            {educationLevels.map((level) => (
              <option key={level} value={level}>
                {level}
              </option>
            ))}
          </select>

          <label htmlFor="grade-period">Série ou período</label>
          <input
            id="grade-period"
            value={gradeOrPeriod}
            onChange={(event) => setGradeOrPeriod(event.target.value)}
            placeholder="Ex.: 3º ano"
          />

          {error && <p className={styles.error}>{error}</p>}

          <button type="submit" disabled={loading}>
            {loading ? 'Salvando contexto...' : 'Entrar como aluno'}
          </button>
        </form>
      </section>
    </main>
  );
}
