import type { NextApiRequest, NextApiResponse } from 'next';

const API_URL = process.env.NEXT_PUBLIC_API_URL ?? 'http://127.0.0.1:8000';

export default async function handler(req: NextApiRequest, res: NextApiResponse) {
  const { activityId } = req.query;
  if (typeof activityId !== 'string') {
    return res.status(400).json({ message: 'ID da questão inválido' });
  }

  try {
    const response = await fetch(`${API_URL}/teachers/activities/${activityId}/review`, {
      method: 'PATCH',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(req.body),
    });
    return res.status(response.status).json(await response.json());
  } catch (error) {
    return res.status(502).json({ message: 'Não foi possível revisar a questão' });
  }
}
