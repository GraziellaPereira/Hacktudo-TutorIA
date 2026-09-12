import type { NextApiRequest, NextApiResponse } from 'next';

const API_URL = process.env.NEXT_PUBLIC_API_URL ?? 'http://127.0.0.1:8000';

export default async function handler(req: NextApiRequest, res: NextApiResponse) {
  if (req.method !== 'POST') {
    return res.status(405).json({ message: 'Método não permitido' });
  }

  try {
    const response = await fetch(`${API_URL}/students`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        name: req.body.name,
        education_level: req.body.educationLevel,
        grade_or_period: req.body.gradeOrPeriod,
      }),
    });

    return res.status(response.status).json(await response.json());
  } catch (error) {
    console.error('Erro ao comunicar com a API de alunos:', error);
    return res.status(502).json({ message: 'Não foi possível comunicar com o backend' });
  }
}
