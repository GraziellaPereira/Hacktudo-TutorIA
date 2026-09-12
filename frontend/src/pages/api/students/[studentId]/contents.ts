import type { NextApiRequest, NextApiResponse } from 'next';

const API_URL = process.env.NEXT_PUBLIC_API_URL ?? 'http://127.0.0.1:8000';

export default async function handler(req: NextApiRequest, res: NextApiResponse) {
  const { studentId } = req.query;

  if (typeof studentId !== 'string') {
    return res.status(400).json({ message: 'ID do aluno inválido' });
  }

  try {
    if (req.method === 'GET') {
      const response = await fetch(`${API_URL}/students/${studentId}/contents`);
      return res.status(response.status).json(await response.json());
    }

    if (req.method === 'POST') {
      const contentId = req.body?.contentId;
      if (typeof contentId !== 'string' || !contentId.trim()) {
        return res.status(400).json({ message: 'Código do conteúdo é obrigatório' });
      }

      const response = await fetch(
        `${API_URL}/students/${studentId}/contents/${contentId.trim()}`,
        {
          method: 'POST',
        },
      );
      return res.status(response.status).json(await response.json());
    }

    return res.status(405).json({ message: 'Método não permitido' });
  } catch (error) {
    console.error('Erro ao comunicar com os conteúdos do aluno:', error);
    return res.status(502).json({ message: 'Não foi possível comunicar com o backend' });
  }
}
