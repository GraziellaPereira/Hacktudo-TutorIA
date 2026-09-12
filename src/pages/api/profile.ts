import type { NextApiRequest, NextApiResponse } from 'next';

import { database } from '../../data/database';

export default function handler(req: NextApiRequest, res: NextApiResponse) {
  // Buscar professor
  if (req.method === 'GET') {
    const teacher = database.teachers[0];

    return res.status(200).json({
      ...teacher,

      contexts: teacher.contexts ?? [],
    });
  }

  // Atualizar professor
  if (req.method === 'PUT') {
    const teacher = database.teachers[0];

    const { name, description, contexts } = req.body;

    database.teachers[0] = {
      ...teacher,

      name: name ?? teacher.name,

      description: description ?? teacher.description,

      contexts: contexts ?? teacher.contexts ?? [],
    };

    return res.status(200).json(database.teachers[0]);
  }

  return res.status(405).json({
    message: 'Método não permitido',
  });
}
