import type { NextApiRequest, NextApiResponse } from 'next';

const API_URL = process.env.NEXT_PUBLIC_API_URL ?? 'http://127.0.0.1:8000';

type ErrorResponse = {
  message: string;
};

export default async function handler(req: NextApiRequest, res: NextApiResponse) {
  const { teacherId } = req.query;

  if (typeof teacherId !== 'string') {
    return res.status(400).json({ message: 'ID do professor inválido' });
  }

  if (req.method !== 'GET' && req.method !== 'PUT') {
    return res.status(405).json({ message: 'Método não permitido' });
  }

  try {
    const response = await fetch(`${API_URL}/teachers/${teacherId}`, {
      method: req.method,
      headers: req.method === 'PUT' ? { 'Content-Type': 'application/json' } : undefined,
      body: req.method === 'PUT' ? JSON.stringify(req.body) : undefined,
    });

    const data = await response.json();

    return res.status(response.status).json(data);
  } catch (error) {
    console.error('Erro ao comunicar com a API de professores:', error);

    return res.status(502).json({
      message: 'Não foi possível comunicar com o backend',
    } satisfies ErrorResponse);
  }
}
