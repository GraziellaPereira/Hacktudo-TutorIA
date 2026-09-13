import type { NextApiRequest, NextApiResponse } from 'next';

const API_URL = process.env.NEXT_PUBLIC_API_URL ?? 'http://127.0.0.1:8000';

export default async function handler(req: NextApiRequest, res: NextApiResponse) {
  const { contentId } = req.query;
  if (typeof contentId !== 'string') {
    return res.status(400).json({ message: 'ID do conteúdo inválido' });
  }

  if (req.method !== 'GET') {
    return res.status(405).json({ message: 'Método não permitido' });
  }

  try {
    const response = await fetch(`${API_URL}/teachers/contents/${contentId}/attachment`);
    const contentType = response.headers.get('content-type');
    if (!response.ok) {
      return res.status(response.status).json(await response.json());
    }

    if (contentType) res.setHeader('Content-Type', contentType);
    const disposition = response.headers.get('content-disposition');
    if (disposition) res.setHeader('Content-Disposition', disposition);
    return res.status(response.status).send(Buffer.from(await response.arrayBuffer()));
  } catch {
    return res.status(502).json({ message: 'Não foi possível baixar o anexo' });
  }
}
