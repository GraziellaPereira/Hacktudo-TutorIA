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
            <div
              key={classroom.id}

              className={styles.classroom}
            >
              <div className={styles.classroomHeader}>
                <strong>
                  🏫 {classroom.name}
                  {classroom.year ? ` - ${classroom.year}` : ''}
                </strong>
              </div>

              <div className={styles.subjectList}>
                <h4>Matérias</h4>

                {classroom.subjects && classroom.subjects.length > 0 ? (
                  classroom.subjects.map((subject: any) => (
                    <div
                      key={subject.id ?? subject}

                      className={styles.subjectRow}
                    >
                      <span>📖 {subject.name ?? subject}</span>

                      <button
                        className={styles.fileButton}

                        onClick={() => {
                          const content = {
                            teacher,

                            subject,

                            classroom,

                            context,
                          };

                          console.log('ABRIR ARQUIVOS:', content);

                          onOpenFiles(content);
                        }}
                      >
                        📂 Arquivos
                      </button>
                    </div>
                  ))
                ) : (
                  <p>Nenhuma matéria cadastrada</p>
                )}
              </div>
            </div>
          ))
        ) : (
          <p>Nenhuma turma cadastrada</p>
        )}
      </div>
    </div>
  );
}
