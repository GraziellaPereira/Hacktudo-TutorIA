import type { NextApiRequest, NextApiResponse } from 'next';

const API_URL = process.env.NEXT_PUBLIC_API_URL?.trim() || 'http://127.0.0.1:8000';

export default async function handler(req: NextApiRequest, res: NextApiResponse) {
  const body = req.body && typeof req.body === 'object' ? req.body : {};
  const teacherId = typeof req.query.teacherId === 'string' ? req.query.teacherId : body.teacherId;
  const contextId = body.contextId;

  if (typeof teacherId !== 'string' || !teacherId.trim()) {
    return res.status(400).json({ message: 'Professor é obrigatório' });
  }

  try {
    if (req.method === 'GET') {
      const response = await fetch(`${API_URL}/teachers/${teacherId}/subjects`);
      return res.status(response.status).json(await response.json());
    }

    if (req.method === 'POST') {
      if (typeof contextId !== 'string' || !contextId.trim()) {
        return res.status(400).json({ message: 'Contexto é obrigatório' });
      }

      const response = await fetch(
        `${API_URL}/teachers/${teacherId}/contexts/${contextId}/subjects`,
        {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(body),
        },
      );
      return res.status(response.status).json(await response.json());
    }

    if (req.method === 'PUT') {
      if (typeof contextId !== 'string' || typeof body.id !== 'string') {
        return res.status(400).json({
          message: 'Professor, contexto e matéria são obrigatórios',
        });
      }

      const response = await fetch(
        `${API_URL}/teachers/${teacherId}/contexts/${contextId}/subjects/${body.id}`,
        {
          method: 'PUT',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(body),
        },
      );
      return res.status(response.status).json(await response.json());
    }

    return res.status(405).json({ message: 'Método não permitido' });
  } catch (error) {
    console.error('Erro ao comunicar com as matérias:', error);
    return res.status(502).json({ message: 'Não foi possível comunicar com o backend' });
  }
}
