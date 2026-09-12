import type { NextApiRequest, NextApiResponse } from 'next';

const API_URL = process.env.NEXT_PUBLIC_API_URL ?? 'http://127.0.0.1:8000';

export default async function handler(req: NextApiRequest, res: NextApiResponse) {
  if (req.method !== 'POST' && req.method !== 'PUT') {
    return res.status(405).json({
      message: 'Método não permitido',
    });
  }

  const { teacherId, contextId, name, description = '', classrooms = [], subjects = [] } = req.body;

  if (req.method === 'PUT') {
    if (typeof teacherId !== 'string' || typeof contextId !== 'string') {
      return res.status(400).json({ message: 'Professor e contexto são obrigatórios' });
    }

    try {
      const response = await fetch(`${API_URL}/teachers/${teacherId}/contexts/${contextId}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ classrooms, subjects }),
      });
      return res.status(response.status).json(await response.json());
    } catch (error) {
      return res.status(502).json({ message: 'Não foi possível comunicar com o backend' });
    }
  }

  if (typeof teacherId !== 'string' || typeof name !== 'string' || !name.trim()) {
    return res.status(400).json({
      message: 'Professor e nome do contexto são obrigatórios',
    });
  }

  try {
    const response = await fetch(`${API_URL}/teachers/${teacherId}/contexts`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ name, description }),
    });

    const data = await response.json();

    return res.status(response.status).json(data);
  } catch (error) {
    console.error('Erro ao comunicar com a API de contextos:', error);

    return res.status(502).json({
      message: 'Não foi possível comunicar com o backend',
    });
  }
}
