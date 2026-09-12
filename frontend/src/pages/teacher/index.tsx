import { useEffect, useState } from 'react';

import TeacherProfile from '../components/teacher/teacherProfile';
import ContextCard from '../components/teacher/ContextCard';

import EditProfileModal from '../components/teacher/EditProfileModal';
import AddContextModal from '../components/teacher/AddContextModal';

import ClassroomManagementModal from '../components/teacher/ClassroomManagementModal';
import SubjectManagerModal from '../components/teacher/SubjectManagerModal';
import FileExplorerModal from '../components/teacher/FileExplorerModal';

import styles from '../../styles/teacher.module.css';

import { getTeacher } from '../../services/teacherService';

export default function ProfessorPage() {
  const [teacher, setTeacher] = useState<any>(null);

  const [showEditProfile, setShowEditProfile] = useState(false);

  const [showAddContext, setShowAddContext] = useState(false);

  // Contexto selecionado

  const [selectedContext, setSelectedContext] = useState<any>(null);

  // Matéria selecionada

  const [selectedSubject, setSelectedSubject] = useState<any>(null);

  // Arquivos/conteúdo selecionado

  const [selectedFileContent, setSelectedFileContent] = useState<any>(null);

  // Carregar professor

  useEffect(() => {
    async function loadTeacher() {
      const teacherId = localStorage.getItem('teacher_id');

      if (!teacherId) {
        console.error('Professor não encontrado');
        return;
      }

      const data = await getTeacher(teacherId);

      setTeacher(data);
    }

    loadTeacher();
  }, []);

  // Atualizar perfil

  async function handleUpdateProfile(updatedTeacher: any) {
    const response = await fetch(`/api/teachers/${teacher.id}`, {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(updatedTeacher),
    });

    const data = await response.json();

    setTeacher(data);

    setShowEditProfile(false);
  }
  // Criar contexto

  async function handleAddContext(context: any) {
    const response = await fetch('/api/contexts', {
      method: 'POST',

      headers: {
        'Content-Type': 'application/json',
      },

      body: JSON.stringify({
        ...context,

        teacherId: teacher.id,
      }),
    });

    const newContext = await response.json();

    setTeacher((prev: any) => ({
      ...prev,

      contexts: [
        ...(prev.contexts ?? []),

        {
          ...newContext,

          classrooms: newContext.classrooms ?? [],
        },
      ],
    }));

    setShowAddContext(false);
  }

  // Atualizar turmas do contexto

  function handleUpdateContext(updatedClassrooms: any[]) {
    setTeacher((prev: any) => ({
      ...prev,

      contexts: prev.contexts.map((context: any) =>
        context.id === selectedContext.id
          ? {
              ...context,

              classrooms: updatedClassrooms,
            }
          : context,
      ),
    }));

    setSelectedContext(null);
  }

  // Atualizar matéria

  function handleUpdateSubject(updatedSubject: any) {
    setTeacher((prev: any) => ({
      ...prev,

      contexts: prev.contexts.map((context: any) => ({
        ...context,

        classrooms: (context.classrooms ?? []).map((classroom: any) => ({
          ...classroom,

          subjects: (classroom.subjects ?? []).map((subject: any) =>
            subject.id === updatedSubject.id ? updatedSubject : subject,
          ),
        })),
      })),
    }));

    setSelectedSubject(null);
  }

  if (!teacher) {
    return <p>Carregando professor...</p>;
  }

  return (
    <main className={styles.container}>
      {/* CONTEXTOS */}

      <section className={styles.subjectsArea}>
        <h1>Meus Contextos</h1>

        {teacher.contexts?.map((context: any) => (
          <ContextCard
            key={context.id}

            teacher={teacher}

            context={context}

            onManage={(ctx: any) => {
              console.log('ABRIR CONTEXTO:', ctx);

              setSelectedContext(ctx);
            }}

            onOpenFiles={(content: any) => {
              console.log('ABRIR ARQUIVOS:', content);

              setSelectedFileContent(content);
            }}
          />
        ))}
      </section>

      {/* PERFIL */}

      <section className={styles.profileArea}>
        <h1>Professor</h1>

        <TeacherProfile
          teacher={teacher}

          onEdit={() => setShowEditProfile(true)}

          onAddContext={() => setShowAddContext(true)}
        />
      </section>

      {/* EDITAR PERFIL */}

      {showEditProfile && (
        <EditProfileModal
          teacher={teacher}

          onSave={handleUpdateProfile}

          onClose={() => setShowEditProfile(false)}
        />
      )}

      {/* ADICIONAR CONTEXTO */}

      {showAddContext && (
        <AddContextModal
          onAdd={handleAddContext}

          onClose={() => setShowAddContext(false)}
        />
      )}

      {/* GERENCIAR TURMAS */}

      {selectedContext && (
        <ClassroomManagementModal
          classrooms={selectedContext.classrooms ?? []}

          onClose={() => setSelectedContext(null)}

          onUpdate={handleUpdateContext}
        />
      )}

      {/* GERENCIAR MATÉRIA */}

      {selectedSubject && (
        <SubjectManagerModal
          subject={selectedSubject}

          onClose={() => setSelectedSubject(null)}

          onUpdate={handleUpdateSubject}
        />
      )}

      {/* ARQUIVOS */}

      {selectedFileContent && (
        <FileExplorerModal
          content={selectedFileContent}

          onClose={() => setSelectedFileContent(null)}
        />
      )}
    </main>
  );
}
