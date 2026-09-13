import type { NextApiRequest, NextApiResponse } from 'next';

const API_URL = process.env.NEXT_PUBLIC_API_URL?.trim() || 'http://127.0.0.1:8000';

export default async function handler(req: NextApiRequest, res: NextApiResponse) {
  const { contentId } = req.query;

  if (typeof contentId !== 'string') {
    return res.status(400).json({ message: 'ID do conteúdo inválido' });
  }

  if (req.method !== 'PATCH') {
    return res.status(405).json({ message: 'Método não permitido' });
  }

  try {
    const response = await fetch(`${API_URL}/teachers/contents/${contentId}`, {
      method: 'PATCH',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(req.body),
    });

    return res.status(response.status).json(await response.json());
  } catch (error) {
    console.error('Erro ao comunicar com a edição do conteúdo:', error);

    return res.status(502).json({
      message: 'Não foi possível comunicar com o backend',
    });
  }
}
