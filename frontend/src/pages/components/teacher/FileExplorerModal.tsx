import { useEffect, useState } from 'react';
import { useRouter } from 'next/router';

import styles from '../../../styles/modal.module.css';

import ImportContentModal from './ImportContentModal';
import { getTeacherContents } from '@/context/contentService';

interface FileExplorerModalProps {
  content: {
    teacher: any;

    subject: any;

    classroom: any;

    context: any;

    files?: any[];
  };

  onClose: () => void;
}

export default function FileExplorerModal({ content, onClose }: FileExplorerModalProps) {
  const router = useRouter();
  const {
    teacher,

    subject,

    classroom,

    context,
  } = content ?? {};

  const [files, setFiles] = useState<any[]>(content?.files ?? []);

  const [selectedFile, setSelectedFile] = useState<any>(null);

  const [showImportModal, setShowImportModal] = useState(false);

  const subjectName = typeof subject === 'string' ? subject : (subject?.name ?? 'Matéria');

  async function loadFiles() {
    if (!teacher?.id) {
      return;
    }

    const teacherContents = await getTeacherContents(teacher.id);
    setFiles(teacherContents);
  }

  useEffect(() => {
    loadFiles().catch((error) => {
      console.error(error);
    });
  }, [teacher?.id]);

  function handleImportSuccess(result: { content_id?: string }) {
    if (result.content_id) {
      onClose();
      router.push(`/teacher/content/${result.content_id}/analysis`);
      return;
    }

    loadFiles().catch((error) => console.error(error));
  }

  return (
    <div className={styles.overlay}>
      <div className={styles.managerModal}>
        {/* CABEÇALHO */}

        <div className={styles.managerHeader}>
          <div>
            <h2>📂 Arquivos - {subjectName}</h2>

            <p>
              🏫 {classroom?.name ?? 'Turma'}
              {classroom?.year ? ` - ${classroom.year}` : ''}
            </p>
          </div>

          <button type="button" onClick={onClose} aria-label="Fechar arquivos">
            ✕
          </button>
        </div>

        <div className={styles.managerContent}>
          {/* LISTA DE ARQUIVOS */}

          <div className={styles.managerLeft}>
            <div className={styles.managerTitle}>
              <h3>Arquivos</h3>

              <button
                type="button"

                className={styles.uploadButton}

                onClick={() => setShowImportModal(true)}
              >
                ＋ Importar Arquivo
              </button>
            </div>

            <div className={styles.contentInfo}>
              <span>👨‍🏫 Professor: {teacher?.name ?? 'Professor'}</span>

              <span>📚 {subjectName}</span>

              <span>🏫 {classroom?.name ?? 'Turma'}</span>

              <span>🎓 {context?.name ?? 'Contexto'}</span>
            </div>

            {files.length > 0 ? (
              files.map((file: any) => (
                <div
                  key={file.id}

                  className={
                    selectedFile?.id === file.id
                      ? styles.classroomItemSelected
                      : styles.classroomItem
                  }

                  onClick={() => {
                    setSelectedFile(file);
                    if (file.id) {
                      router.push(`/teacher/content/${file.id}/analysis`);
                    }
                  }}
                >
                  📄 {file.title ?? file.name ?? 'Conteúdo sem título'}
                </div>
              ))
            ) : (
              <div className={styles.emptyArea}>Nenhum arquivo importado.</div>
            )}
          </div>

          {/* DETALHES */}

          <div className={styles.managerRight}>
            {selectedFile ? (
              <>
                <h3>Detalhes do arquivo</h3>

                <p>
                  <strong>Nome:</strong> {selectedFile.title ?? selectedFile.name}
                </p>

                <p>
                  <strong>Tipo:</strong> {selectedFile.type}
                </p>

                <p>
                  <strong>Tamanho:</strong> {selectedFile.size}
                </p>

                <a
                  href={`/api/contents/${selectedFile.id}/attachment`}
                  download
                  className={styles.uploadButton}
                >
                  📤 Baixar anexo
                </a>
              </>
            ) : (
              <div className={styles.emptyArea}>Selecione um arquivo para visualizar.</div>
            )}
          </div>
        </div>
      </div>

      {showImportModal && (
        <ImportContentModal
          content={content}

          onClose={() => setShowImportModal(false)}

          onSuccess={handleImportSuccess}
        />
      )}
    </div>
  );
}
