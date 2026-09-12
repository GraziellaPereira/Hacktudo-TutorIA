import { useState } from 'react';

import styles from '../../../styles/modal.module.css';

export default function ClassroomManagementModal({
  classrooms = [],
  onUpdate,
  onSave,
  onClose,
}: any) {
  const [classroomList, setClassroomList] = useState<any[]>(classrooms);

  const [selectedClassroom, setSelectedClassroom] = useState<any>(null);

  const [isNewClassroom, setIsNewClassroom] = useState(false);

  const [name, setName] = useState('');

  const [year, setYear] = useState('');

  const [educationLevels, setEducationLevels] = useState<string[]>([]);

  const [subjects, setSubjects] = useState<string[]>([]);

  const [subjectName, setSubjectName] = useState('');

  const [learningObjective, setLearningObjective] = useState('');

  const [questionFocus, setQuestionFocus] = useState('');

  const [studentsCount, setStudentsCount] = useState(0);

  const levels = [
    'Ensino Infantil',
    'Ensino Fundamental I',
    'Ensino Fundamental II',
    'Ensino Médio',
    'Ensino Técnico',
    'Faculdade',
  ];

  function selectClassroom(classroom: any) {
    setIsNewClassroom(false);

    setSelectedClassroom(classroom);

    setName(classroom.name ?? '');

    setYear(classroom.year ?? '');

    setEducationLevels(classroom.educationLevels ?? []);

    setSubjects(classroom.subjects ?? []);

    setLearningObjective(classroom.learningObjective ?? '');

    setQuestionFocus(classroom.questionFocus ?? '');

    setStudentsCount(classroom.studentsCount ?? 0);
  }

  function addClassroom() {
    const newClassroom = {
      id: Date.now(),

      name: 'Nova Turma',

      year: new Date().getFullYear().toString(),

      educationLevels: [],

      subjects: [],

      learningObjective: '',

      questionFocus: '',

      studentsCount: 0,
    };

    setIsNewClassroom(true);

    setSelectedClassroom(newClassroom);

    setName(newClassroom.name);

    setYear(newClassroom.year);

    setEducationLevels([]);

    setSubjects([]);

    setLearningObjective('');

    setQuestionFocus('');

    setStudentsCount(0);
  }

  function toggleLevel(level: string) {
    setEducationLevels((prev) =>
      prev.includes(level) ? prev.filter((item) => item !== level) : [...prev, level],
    );
  }

  function addSubject() {
    if (!subjectName.trim()) {
      return;
    }

    setSubjects((prev) => [...prev, subjectName.trim()]);

    setSubjectName('');
  }

  function removeSubject(subject: string) {
    setSubjects((prev) => prev.filter((item) => item !== subject));
  }

  function saveClassroom() {
    if (
      !selectedClassroom ||
      !name ||
      !year ||
      educationLevels.length === 0 ||
      subjects.length === 0 ||
      !learningObjective ||
      !questionFocus ||
      studentsCount <= 0
    ) {
      alert('Preencha todos os campos obrigatórios.');

      return;
    }

    const classroom = {
      ...selectedClassroom,

      name,

      year,

      educationLevels,

      subjects,

      learningObjective,

      questionFocus,

      studentsCount,
    };

    let updated: any[];

    if (isNewClassroom) {
      updated = [...classroomList, classroom];
    } else {
      updated = classroomList.map((item: any) => (item.id === classroom.id ? classroom : item));
    }

    setClassroomList(updated);

    if (onUpdate) {
      onUpdate(updated);
    }

    if (onSave) {
      onSave(updated);
    }

    setSelectedClassroom(null);

    setIsNewClassroom(false);
  }

  return (
    <div className={styles.overlay}>
      <div className={styles.managerModal}>
        <div className={styles.managerHeader}>
          <h2>Gerenciar Turmas/Ano</h2>

          <button onClick={onClose}>✕</button>
        </div>

        <div className={styles.managerContent}>
          <div className={styles.managerLeft}>
            <div className={styles.managerTitle}>
              <h3>Turmas/Ano</h3>

              <button className={styles.addClassroomButton} onClick={addClassroom}>
                + Adicionar Turma
              </button>
            </div>

            {classroomList.length > 0 ? (
              classroomList.map((classroom: any) => (
                <div
                  key={classroom.id}

                  className={styles.classroomItem}

                  onClick={() => selectClassroom(classroom)}
                >
                  {classroom.name}

                  {' - '}

                  {classroom.year}
                </div>
              ))
            ) : (
              <div className={styles.emptyArea}>Nenhuma turma cadastrada</div>
            )}
          </div>

          <div className={styles.managerRight}>
            {selectedClassroom ? (
              <>
                <h3>{isNewClassroom ? 'Nova Turma/Ano' : 'Editar Turma/Ano'}</h3>

                <label>Nome *</label>

                <input
                  value={name}

                  onChange={(e) => setName(e.target.value)}
                />

                <label>Ano escolar *</label>

                <input
                  value={year}

                  onChange={(e) => setYear(e.target.value)}
                />

                <h4>Ensino *</h4>

                {levels.map((level) => (
                  <label key={level}>
                    <input
                      type="checkbox"

                      checked={educationLevels.includes(level)}

                      onChange={() => toggleLevel(level)}
                    />

                    {level}
                  </label>
                ))}

                <label>Matérias *</label>

                <input
                  placeholder="Digite a matéria"

                  value={subjectName}

                  onChange={(e) => setSubjectName(e.target.value)}
                />

                <button onClick={addSubject}>Adicionar matéria</button>

                <div className={styles.subjectTable}>
                  {subjects.map((subject) => (
                    <div
                      key={subject}

                      className={styles.subjectRow}
                    >
                      <span>📚 {subject}</span>

                      <button
                        className={styles.removeSubject}

                        onClick={() => removeSubject(subject)}
                      >
                        ✕
                      </button>
                    </div>
                  ))}
                </div>

                <label>Objetivo de aprendizagem *</label>

                <textarea
                  value={learningObjective}

                  onChange={(e) => setLearningObjective(e.target.value)}
                />

                <label>Foco das questões *</label>

                <textarea
                  value={questionFocus}

                  onChange={(e) => setQuestionFocus(e.target.value)}
                />

                <label>Quantidade de alunos *</label>

                <input
                  type="number"

                  min="1"

                  value={studentsCount}

                  onChange={(e) => setStudentsCount(Number(e.target.value))}
                />

                <button onClick={saveClassroom}>Salvar</button>
              </>
            ) : (
              <div className={styles.emptyArea}>Selecione uma turma</div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
