import { useState } from 'react';

import { updateProfile } from '../../../services/teacherService';

import styles from '../../../styles/modal.module.css';

export default function EditProfileModal({ teacher, onSave, onClose }: any) {
  const [name, setName] = useState(teacher.name);

  const [description, setDescription] = useState(teacher.description);

  async function save() {
    const updated = await updateProfile(teacher.id, {
      name,

      description,
    });

    onSave(updated);
  }

  return (
    <div className={styles.overlay}>
      <div className={styles.modal}>
        <h2>Editar Perfil</h2>

        <input
          value={name}

          onChange={(e) => setName(e.target.value)}

          placeholder="Nome"
        />

        <textarea
          value={description}

          onChange={(e) => setDescription(e.target.value)}

          placeholder="Descrição"
        />

        <div className={styles.actions}>
          <button onClick={onClose}>Cancelar</button>

          <button onClick={save}>Salvar</button>
        </div>
      </div>
    </div>
  );
}
