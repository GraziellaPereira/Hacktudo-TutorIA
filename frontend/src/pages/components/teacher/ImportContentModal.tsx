import { useState } from 'react';

import styles from '../../../styles/modal.module.css';

import { createTeacherContent } from '@/context/contentService';

export default function ImportContentModal({ content, onClose, onSuccess }: any) {
  const { teacher, subject, classroom } = content;

  const [title, setTitle] = useState('');

  const [targetAudience, setTargetAudience] = useState('');

  const [file, setFile] = useState<File | null>(null);

  const [loading, setLoading] = useState(false);

  async function handleSave() {
    if (!file) {
      alert('Selecione um arquivo.');

      return;
    }

    if (!title) {
      alert('Informe o título.');

      return;
    }

    try {
      setLoading(true);

      const result = await createTeacherContent({
        teacherId: teacher.id,

        title,

        subject: typeof subject === 'string' ? subject : subject.name,

        educationLevel: classroom.educationLevels?.[0] ?? '',

        gradeOrPeriod: `${classroom.name} - ${classroom.year}`,

        targetAudience,

        learningGoal: classroom.learningObjective ?? '',

        assessmentFocus: classroom.questionFocus ? [classroom.questionFocus] : [],

        file,
      });

      alert('Arquivo importado com sucesso!');

      if (onSuccess) {
        onSuccess(result);
      }

      onClose();
    } catch (error) {
      console.error(error);

      alert('Erro ao importar arquivo.');
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className={styles.overlay}>
      <div className={styles.managerModal}>
        <div className={styles.managerHeader}>
          <h2>📥 Importar Conteúdo</h2>

          <button onClick={onClose}>✕</button>
        </div>

        <div className={styles.managerRight}>
          <label>Professor</label>

          <input value={teacher?.name ?? ''} disabled />

          <label>Matéria</label>

          <input
            value={typeof subject === 'string' ? subject : (subject?.name ?? '')}

            disabled
          />

          <label>Turma</label>

          <input
            value={`${classroom.name} - ${classroom.year}`}

            disabled
          />

          <label>Nível de ensino</label>

          <input
            value={classroom.educationLevels?.[0] ?? ''}

            disabled
          />

          <label>Título *</label>

          <input
            value={title}

            onChange={(e) => setTitle(e.target.value)}
          />

          <label>Público alvo *</label>

          <input
            value={targetAudience}

            onChange={(e) => setTargetAudience(e.target.value)}
          />

          <label>Arquivo *</label>

          <input
            type="file"

            onChange={(e) => setFile(e.target.files?.[0] ?? null)}
          />

          <button
            onClick={handleSave}

            disabled={loading}
          >
            {loading ? 'Processando conteúdo...' : 'Salvar conteúdo'}
          </button>

          {loading && <p>IA analisando o arquivo. Isso pode levar alguns instantes.</p>}
        </div>
      </div>
    </div>
  );
}
