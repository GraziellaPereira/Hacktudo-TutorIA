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

  const subjects = Array.from(
    new Map(
      contexts
        .flatMap((context: any) => [
          ...(Array.isArray(context.subjects) ? context.subjects : []),
          ...(Array.isArray(context.classrooms) ? context.classrooms : []).flatMap(
            (classroom: any) => (Array.isArray(classroom.subjects) ? classroom.subjects : []),
          ),
        ])
        .map((subject: any, index: number) => [
          String(subject.id ?? `${subject.name ?? 'subject'}-${index}`),
          subject,
        ]),
    ).values(),
  );

  const classrooms = Array.from(
    new Map(
      contexts
        .flatMap((context: any) => [
          ...(Array.isArray(context.classrooms) ? context.classrooms : []),
          ...subjects.flatMap((subject: any) =>
            Array.isArray(subject.classrooms) ? subject.classrooms : [],
          ),
        ])
        .map((classroom: any, index: number) => [
          String(classroom.id ?? `${classroom.name ?? 'classroom'}-${index}`),
          classroom,
        ]),
    ).values(),
  );

  const totalStudents = classrooms.reduce(
    (total: number, classroom: any) => total + Number(classroom.studentsCount ?? 0),
    0,
  );

  return (
    <div className={styles.profile}>
      <h1 className={styles.name}>👤 {teacher.name}</h1>

      <p className={styles.description}>{teacher.description}</p>

      <div className={styles.summary}>
        <h2>Resumo</h2>

        <div className={styles.summaryItem}>📚 Matérias: {subjects.length}</div>

        <div className={styles.summaryItem}>🏫 Turmas/Ano: {classrooms.length}</div>

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
