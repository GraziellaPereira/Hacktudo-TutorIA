import { useState } from 'react';

import styles from '../../../styles/addSubjectModal.module.css';

export default function AddContextModal({ onAdd, onClose }: any) {
  const [name, setName] = useState('');

  const [description, setDescription] = useState('');

  function save() {
    if (!name) {
      return;
    }

    const context = {
      name,

      description,

      subjects: [],
    };

    onAdd(context);
  }

  return (
    <div className={styles.overlay}>
      <div className={styles.modal}>
        <h2>Novo Contexto</h2>

        <label>Nome do contexto</label>

        <input
          placeholder="Ex: Cursos, Provas, Faculdade"

          value={name}

          onChange={(e) => setName(e.target.value)}
        />

        <label>Descrição</label>

        <textarea
          placeholder="Descreva este contexto"

          value={description}

          onChange={(e) => setDescription(e.target.value)}
        />

        <div className={styles.actions}>
          <button
            className={styles.cancel}

            onClick={onClose}
          >
            Cancelar
          </button>

          <button
            className={styles.save}

            onClick={save}
          >
            Adicionar
          </button>
        </div>
      </div>
    </div>
  );
}
