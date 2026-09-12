import type { NextApiRequest, NextApiResponse } from 'next';

const API_URL = process.env.NEXT_PUBLIC_API_URL ?? 'http://127.0.0.1:8000';

export default async function handler(req: NextApiRequest, res: NextApiResponse) {
  const { studentId } = req.query;

  if (typeof studentId !== 'string') {
    return res.status(400).json({ message: 'ID do aluno inválido' });
  }

  if (req.method !== 'GET') {
    return res.status(405).json({ message: 'Método não permitido' });
  }

  try {
    const response = await fetch(`${API_URL}/students/${studentId}`);
    return res.status(response.status).json(await response.json());
  } catch (error) {
    console.error('Erro ao carregar o aluno:', error);
    return res.status(502).json({ message: 'Não foi possível comunicar com o backend' });
  }
}
