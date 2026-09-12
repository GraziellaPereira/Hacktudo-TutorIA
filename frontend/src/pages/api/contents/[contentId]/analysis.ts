import type { NextApiRequest, NextApiResponse } from 'next';

const API_URL = process.env.NEXT_PUBLIC_API_URL ?? 'http://127.0.0.1:8000';

export default async function handler(req: NextApiRequest, res: NextApiResponse) {
  const { contentId } = req.query;

  if (typeof contentId !== 'string') {
    return res.status(400).json({ message: 'ID do conteúdo inválido' });
  }

  if (req.method !== 'GET' && req.method !== 'POST') {
    return res.status(405).json({ message: 'Método não permitido' });
  }

  const endpoint = req.method === 'POST' ? 'approve' : 'analysis';

  try {
    const response = await fetch(`${API_URL}/teachers/contents/${contentId}/${endpoint}`, {
      method: req.method,
    });
    const data = await response.json();

    return res.status(response.status).json(data);
  } catch (error) {
    console.error('Erro ao comunicar com a análise do conteúdo:', error);

    return res.status(502).json({
      message: 'Não foi possível comunicar com o backend',
    });
  }
}
