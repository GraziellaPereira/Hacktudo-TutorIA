import type { NextApiRequest, NextApiResponse } from 'next';

import { Readable } from 'node:stream';

export const config = {
  api: {
    bodyParser: false,
  },
};

const API_URL = process.env.NEXT_PUBLIC_API_URL ?? 'http://127.0.0.1:8000';

export default async function handler(req: NextApiRequest, res: NextApiResponse) {
  const { teacherId } = req.query;

  if (typeof teacherId !== 'string') {
    return res.status(400).json({ message: 'ID do professor inválido' });
  }

  if (req.method !== 'GET' && req.method !== 'POST') {
    return res.status(405).json({ message: 'Método não permitido' });
  }

  try {
    const requestInit = {
      method: req.method,
    } as RequestInit & { duplex?: 'half' };

    if (req.method === 'POST') {
      requestInit.headers = {
        'content-type': req.headers['content-type'] ?? '',
      };
      requestInit.body = Readable.toWeb(req) as unknown as BodyInit;
      requestInit.duplex = 'half';
    }

    const response = await fetch(`${API_URL}/teachers/${teacherId}/contents`, requestInit);

    const data = await response.json();

    return res.status(response.status).json(data);
  } catch (error) {
    console.error('Erro ao comunicar com a API de conteúdos:', error);

    return res.status(502).json({
      message: 'Não foi possível comunicar com o backend',
    });
  }
}
