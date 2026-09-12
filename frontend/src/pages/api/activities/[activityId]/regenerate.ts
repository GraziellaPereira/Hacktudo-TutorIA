import type { NextApiRequest, NextApiResponse } from 'next';

const API_URL = process.env.NEXT_PUBLIC_API_URL ?? 'http://127.0.0.1:8000';

export default async function handler(req: NextApiRequest, res: NextApiResponse) {
  const { activityId } = req.query;
  const contentId = req.body?.contentId;
  if (typeof activityId !== 'string' || typeof contentId !== 'string') {
    return res.status(400).json({ message: 'IDs da questão e do conteúdo são obrigatórios' });
  }

  try {
    const response = await fetch(
      `${API_URL}/teachers/activities/${activityId}/regenerate/${contentId}`,
      { method: 'POST' },
    );
    return res.status(response.status).json(await response.json());
  } catch (error) {
    return res.status(502).json({ message: 'Não foi possível regenerar a questão' });
  }
}
