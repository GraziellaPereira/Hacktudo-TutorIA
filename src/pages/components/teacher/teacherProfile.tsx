import { Teacher } from '../../../types/teacher';

import styles from '../../../styles/teacherProfile.module.css';

interface TeacherProfileProps {
  teacher: Teacher;

  onEdit?: () => void;

  onAddContext?: () => void;
}

export default function TeacherProfile({
  teacher,

  onEdit,

  onAddContext,
}: TeacherProfileProps) {
  const contexts = teacher.contexts ?? [];

  const totalSubjects = contexts.reduce(
    (total: any, context: any) => total + (context.subjects?.length ?? 0),

    0,
  );

  const totalClassrooms = contexts.reduce(
    (total: any, context: any) =>
      total +
      context.subjects.reduce(
        (subjectTotal: any, subject: any) => subjectTotal + subject.classrooms.length,

        0,
      ),

    0,
  );

  const totalStudents = contexts.reduce(
    (total: any, context: any) =>
      total +
      context.subjects.reduce(
        (subjectTotal: any, subject: any) =>
          subjectTotal +
          subject.classrooms.reduce(
            (classTotal: any, classroom: any) => classTotal + classroom.studentsCount,

            0,
          ),

        0,
      ),

    0,
  );

  return (
    <div className={styles.profile}>
      <h1 className={styles.name}>👤 {teacher.name}</h1>

      <p className={styles.description}>{teacher.description}</p>

      <div className={styles.summary}>
        <h2>Resumo</h2>

        <div className={styles.summaryItem}>📚 Matérias: {totalSubjects}</div>

        <div className={styles.summaryItem}>🏫 Turmas/Ano: {totalClassrooms}</div>

        <div className={styles.summaryItem}>👥 Alunos: {totalStudents}</div>
      </div>

      <div className={styles.actions}>
        <button
          className={styles.button}

          onClick={onEdit}
        >
          Editar Perfil
        </button>

        <button
          className={styles.button}

          onClick={onAddContext}
        >
          Adicionar Contexto
        </button>
      </div>
    </div>
  );
}
