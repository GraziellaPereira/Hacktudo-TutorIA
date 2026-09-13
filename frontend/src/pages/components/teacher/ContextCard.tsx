import styles from '../../../styles/subjectCard.module.css';

interface ContextCardProps {
  teacher: any;

  context: any;

  onManage: (context: any) => void;

  onOpenFiles: (content: any) => void;
}

export default function ContextCard({
  teacher,

  context,

  onManage,

  onOpenFiles,
}: ContextCardProps) {
  return (
    <div className={styles.card}>
      <div className={styles.header}>
        <h2 className={styles.title}>📚 {context.name}</h2>

        <button
          className={styles.button}

          onClick={() => {
            console.log('GERENCIAR CONTEXTO:', context);

            onManage(context);
          }}
        >
          Gerenciar
        </button>
      </div>

      <p className={styles.description}>{context.description}</p>

      <div className={styles.info}>
        <h3>Turmas/Ano</h3>

        {context.classrooms && context.classrooms.length > 0 ? (
          context.classrooms.map((classroom: any) => (
            <button
              key={classroom.id}

              className={styles.classroomCard}

              type="button"

              onClick={() => {
                onOpenFiles({
                  teacher,

                  subject: classroom.subjects?.[0] ?? '',

                  classroom,

                  context,
                });
              }}
            >
              <span className={styles.classroomCardIcon}>🏫</span>

              <span className={styles.classroomCardContent}>
                <strong>
                  {classroom.name}
                  {classroom.year ? ` - ${classroom.year}` : ''}
                </strong>

                <span>
                  {classroom.subjects?.length
                    ? `${classroom.subjects.length} matéria${classroom.subjects.length > 1 ? 's' : ''}`
                    : 'Nenhuma matéria cadastrada'}
                </span>
              </span>

              <span className={styles.classroomCardArrow} aria-hidden="true">
                →
              </span>
            </button>
          ))
        ) : (
          <p>Nenhuma turma cadastrada</p>
        )}
      </div>
    </div>
  );
}
