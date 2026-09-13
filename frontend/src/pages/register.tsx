import { useState } from 'react';

import { useRouter } from 'next/router';

import { createTeacher } from '../services/teacherService';

import styles from '../styles/register.module.css';

export default function Register() {
  const router = useRouter();

  const [name, setName] = useState('');

  const [description, setDescription] = useState('');

  const [email, setEmail] = useState('');

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

      alert(`Cadastro realizado! Seu código de acesso é: ${response.teacher_id}`);

      await router.push('/');
    } catch (error) {
      console.error(error);

      alert('Erro ao criar professor');
    } finally {
      setLoading(false);
    }
  }

  return (
    <main className={styles.container}>
      <div className={styles.card}>
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
      </div>
    </main>
  );
}
