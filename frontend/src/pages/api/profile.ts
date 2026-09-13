import type { NextApiRequest, NextApiResponse } from 'next';

const API_URL = process.env.NEXT_PUBLIC_API_URL?.trim() || 'http://127.0.0.1:8000';

export default async function handler(req: NextApiRequest, res: NextApiResponse) {
  const body = req.body && typeof req.body === 'object' ? req.body : {};
  const teacherId = typeof req.query.teacherId === 'string' ? req.query.teacherId : body.teacherId;

  if (typeof teacherId !== 'string' || !teacherId.trim()) {
    return res.status(400).json({ message: 'Professor é obrigatório' });
  }

  if (req.method !== 'GET' && req.method !== 'PUT') {
    return res.status(405).json({ message: 'Método não permitido' });
  }

  try {
    const response = await fetch(`${API_URL}/teachers/${teacherId}`, {
      method: req.method,
      headers: req.method === 'PUT' ? { 'Content-Type': 'application/json' } : undefined,
      body: req.method === 'PUT' ? JSON.stringify(body) : undefined,
    });
    return res.status(response.status).json(await response.json());
  } catch (error) {
    console.error('Erro ao comunicar com o perfil do professor:', error);
    return res.status(502).json({ message: 'Não foi possível comunicar com o backend' });
  }
}
