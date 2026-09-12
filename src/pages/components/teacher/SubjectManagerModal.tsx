import { useEffect, useState } from 'react';

import ClassroomManagementModal from './ClassroomManagementModal';

import styles from '../../../styles/modal.module.css';

export default function SubjectManagerModal({ subject, onClose, onUpdate }: any) {
  const [currentSubject, setCurrentSubject] = useState(subject);

  const [classrooms, setClassrooms] = useState(subject.classrooms ?? []);

  const [showClassroomManager, setShowClassroomManager] = useState(false);

  useEffect(() => {
    setCurrentSubject(subject);

    setClassrooms(subject.classrooms ?? []);
  }, [subject]);

  function addClassroom() {
    const newClassroom = {
      id: Date.now(),

      name: `Turma ${classrooms.length + 1}`,

      year: '',

      educationLevels: [],

      subjects: [],

      learningObjective: '',

      questionFocus: '',

      studentsCount: 0,
    };

    const updatedClassrooms = [...classrooms, newClassroom];

    setClassrooms(updatedClassrooms);

    setCurrentSubject((prev: any) => ({
      ...prev,

      classrooms: updatedClassrooms,
    }));
  }

  async function saveChanges() {
    if (!currentSubject || !currentSubject.id || !('classrooms' in currentSubject)) {
      alert('Selecione uma matéria válida antes de salvar as turmas.');

      return;
    }

    const payload = {
      id: currentSubject.id,

      classrooms: currentSubject.classrooms ?? classrooms,
    };

    console.log('==============================');

    console.log('SALVANDO MATÉRIA');

    console.log('PAYLOAD:', payload);

    console.log('==============================');

    const response = await fetch('/api/subjects', {
      method: 'PUT',

      headers: {
        'Content-Type': 'application/json',
      },

      body: JSON.stringify(payload),
    });

    console.log('STATUS API:', response.status);

    if (!response.ok) {
      const error = await response.json().catch(() => null);

      console.error('Erro ao salvar matéria:', error);

      return;
    }

    const updatedSubject = await response.json();

    setCurrentSubject(updatedSubject);

    setClassrooms(updatedSubject.classrooms ?? []);

    if (onUpdate) {
      onUpdate(updatedSubject);
    }

    onClose();
  }

  const totalStudents = classrooms.reduce(
    (total: number, classroom: any) => total + Number(classroom.studentsCount ?? 0),

    0,
  );

  return (
    <div className={styles.overlay}>
      <div className={styles.modal}>
        <div className={styles.modalHeader}>
          <h2>{currentSubject.name}</h2>

          <button
            className={styles.settingsButton}

            onClick={() => setShowClassroomManager(true)}
          >
            ⚙️
          </button>
        </div>

        <p>{currentSubject.description}</p>

        <div className={styles.info}>
          <strong>Importância:</strong> {currentSubject.importanceLevel}
        </div>

        <hr />

        <h3>Turmas/Ano</h3>

        {classrooms.map((classroom: any) => (
          <div
            key={classroom.id}

            className={styles.classroomItem}
          >
            <span>🏫 {classroom.name}</span>

            <span>{classroom.year || 'Sem ano'}</span>

            <span>👥 {classroom.studentsCount}</span>
          </div>
        ))}

        <button
          className={styles.addButton}

          onClick={addClassroom}
        >
          Adicionar Turma/Ano
        </button>

        <div className={styles.total}>
          <strong>Total de alunos:</strong> {totalStudents}
        </div>

        <div className={styles.actions}>
          <button onClick={onClose}>Fechar</button>

          <button onClick={saveChanges}>Salvar alterações</button>
        </div>

        {showClassroomManager && (
          <ClassroomManagementModal
            classrooms={classrooms}

            onUpdate={(updated: any) => {
              setClassrooms(updated);

              setCurrentSubject((prev: any) => ({
                ...prev,

                classrooms: updated,
              }));
            }}

            onClose={() => {
              setShowClassroomManager(false);
            }}
          />
        )}
      </div>
    </div>
  );
}
