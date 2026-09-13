import { FormEvent, useState } from 'react';

import Link from 'next/link';

import { useRouter } from 'next/router';

import { getTeacher } from '../services/teacherService';

import styles from '../styles/home.module.css';

export default function Home() {
  const router = useRouter();

  const [activeRole, setActiveRole] = useState<'student' | 'teacher'>('teacher');
  const [accessCode, setAccessCode] = useState('');
  const [studentName, setStudentName] = useState('');
  const [educationLevel, setEducationLevel] = useState('');
  const [gradeOrPeriod, setGradeOrPeriod] = useState('');

  const [loading, setLoading] = useState(false);

  const [error, setError] = useState('');

  const educationLevels = [
    'Ensino Fundamental I',
    'Ensino Fundamental II',
    'Ensino Médio',
    'Ensino Técnico',
    'Faculdade',
  ];

  async function handleLogin(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();

    const code = accessCode.trim();

    if (!code) {
      setError('Digite o código de acesso do professor.');

      return;
    }

    try {
      setLoading(true);

      setError('');

      await getTeacher(code);

      localStorage.setItem('teacher_id', code);

      await router.push('/teacher');
    } catch (loginError) {
      console.error(loginError);

      setError('Código de acesso inválido. Confira o código e tente novamente.');
    } finally {
      setLoading(false);
    }
  }

  async function handleStudentLogin(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();

    if (!studentName.trim() || !educationLevel || !gradeOrPeriod.trim()) {
      setError('Preencha nome, nível de ensino e série/período.');
      return;
    }

    try {
      setLoading(true);
      setError('');

      const response = await fetch('/api/students', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          name: studentName,
          educationLevel,
          gradeOrPeriod,
        }),
      });
      const data = await response.json();

      if (!response.ok) throw new Error(data.detail ?? data.message ?? 'Erro ao criar aluno');

      localStorage.setItem('student_id', data.student_id);
      await router.push('/student');
    } catch (loginError) {
      console.error(loginError);
      setError(loginError instanceof Error ? loginError.message : 'Erro ao criar aluno');
    } finally {
      setLoading(false);
    }
  }

  function selectRole(role: 'student' | 'teacher') {
    setActiveRole(role);
    setError('');
  }

  return (
    <main className={styles.container}>
      <div className={styles.card}>
        <span className={styles.eyebrow}>Acesso à plataforma</span>

        <h1>Tutor IA</h1>

        <div className={styles.tabs} role="tablist" aria-label="Tipo de acesso">
          <button
            type="button"
            role="tab"
            aria-selected={activeRole === 'student'}
            className={activeRole === 'student' ? styles.activeTab : styles.tab}
            onClick={() => selectRole('student')}
          >
            Aluno
          </button>
          <button
            type="button"
            role="tab"
            aria-selected={activeRole === 'teacher'}
            className={activeRole === 'teacher' ? styles.activeTab : styles.tab}
            onClick={() => selectRole('teacher')}
          >
            Professor
          </button>
        </div>

        {activeRole === 'teacher' ? (
          <>
            <p>Entre com seu código de acesso para continuar organizando suas aulas e conteúdos.</p>

            <form className={styles.form} onSubmit={handleLogin}>
              <label htmlFor="access-code">Código de acesso</label>

              <input
                id="access-code"
                type="text"
                placeholder="Ex.: prof-123"
                value={accessCode}
                onChange={(event) => setAccessCode(event.target.value)}
                autoComplete="off"
                disabled={loading}
              />

              {error && <p className={styles.error}>{error}</p>}

              <button className={styles.button} type="submit" disabled={loading}>
                {loading ? 'Validando...' : 'Acessar'}
              </button>
            </form>

            <div className={styles.registerPrompt}>
              <span>Ainda não possui um código?</span>

              <Link href="/register">Cadastrar professor</Link>
            </div>
          </>
        ) : (
          <>
            <p>Informe seus dados para personalizar sua experiência de aprendizagem.</p>

            <form className={styles.form} onSubmit={handleStudentLogin}>
              <label htmlFor="student-name">Nome</label>
              <input
                id="student-name"
                value={studentName}
                onChange={(event) => setStudentName(event.target.value)}
                placeholder="Como você se chama?"
                disabled={loading}
              />

              <label htmlFor="education-level">Nível de ensino</label>
              <select
                id="education-level"
                value={educationLevel}
                onChange={(event) => setEducationLevel(event.target.value)}
                disabled={loading}
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
                disabled={loading}
              />

              {error && <p className={styles.error}>{error}</p>}

              <button className={styles.button} type="submit" disabled={loading}>
                {loading ? 'Entrando...' : 'Entrar como aluno'}
              </button>
            </form>
          </>
        )}
      </div>
    </main>
  );
}
