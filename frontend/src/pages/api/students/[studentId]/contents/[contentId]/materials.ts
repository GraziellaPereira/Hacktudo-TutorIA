import type { NextApiRequest, NextApiResponse } from 'next';

const API_URL = process.env.NEXT_PUBLIC_API_URL ?? 'http://127.0.0.1:8000';

export default async function handler(req: NextApiRequest, res: NextApiResponse) {
  const { studentId, contentId } = req.query;
  if (typeof studentId !== 'string' || typeof contentId !== 'string') {
    return res.status(400).json({ message: 'IDs inválidos' });
  }

  try {
    const response = await fetch(
      `${API_URL}/students/${studentId}/contents/${contentId}/materials`,
      {
        method: req.method,
      },
    );
    return res.status(response.status).json(await response.json());
  } catch (error) {
    return res.status(502).json({ message: 'Não foi possível carregar o material' });
  }
}
