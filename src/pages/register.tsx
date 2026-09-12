import { useState } from 'react';

import { useRouter } from 'next/router';

import { createTeacher } from '../services/teacherService';

import styles from '../styles/register.module.css';

export default function Register() {
  const router = useRouter();

  const [name, setName] = useState('');

  const [description, setDescription] = useState('');

  const [email, setEmail] = useState('');

  const [teacherId, setTeacherId] = useState('');

  const [loading, setLoading] = useState(false);

  async function handleCreateTeacher() {
    if (!name || !description) {
      alert('Preencha nome e descrição');

      return;
    }

    try {
      setLoading(true);

      const response = await createTeacher({
        name,

        description,

        email,
      });

      setTeacherId(response.teacher_id);
    } catch (error) {
      console.error(error);

      alert('Erro ao criar professor');
    } finally {
      setLoading(false);
    }
  }

  function finishRegister() {
    router.push('/');
  }

  return (
    <main className={styles.container}>
      <div className={styles.card}>
        {!teacherId ? (
          <>
            <h1>Cadastro de Professor</h1>

            <input
              placeholder="Nome"

              value={name}

              onChange={(e) => setName(e.target.value)}
            />

            <input
              placeholder="Email"

              value={email}

              onChange={(e) => setEmail(e.target.value)}
            />

            <textarea
              placeholder="Descrição"

              value={description}

              onChange={(e) => setDescription(e.target.value)}
            />

            <button
              onClick={handleCreateTeacher}

              disabled={loading}
            >
              {loading ? 'Criando...' : 'Criar Professor'}
            </button>
          </>
        ) : (
          <>
            <h1>Cadastro realizado!</h1>

            <p>Seu código de acesso:</p>

            <div className={styles.teacherId}>{teacherId}</div>

            <button onClick={() => navigator.clipboard.writeText(teacherId)}>
              📋 Copiar código
            </button>

            <button onClick={finishRegister}>Fechar</button>
          </>
        )}
      </div>
    </main>
  );
}
