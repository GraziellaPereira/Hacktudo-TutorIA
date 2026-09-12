import type { NextApiRequest, NextApiResponse } from 'next';

import { database } from '../../../data/database';

export default function handler(req: NextApiRequest, res: NextApiResponse) {
  if (req.method === 'POST') {
    const teacher = database.teachers.find((item: any) => item.id === Number(req.body.teacherId));

    if (!teacher) {
      return res.status(404).json({
        message: 'Professor não encontrado',
      });
    }

    const newContext = {
      id: Date.now(),

      name: req.body.name,

      description: req.body.description,

      subjects: [],
    };

    teacher.contexts = teacher.contexts ?? [];

    teacher.contexts.push(newContext);

    return res.status(201).json(newContext);
  }

  if (req.method === 'GET') {
    const contexts: any[] = [];

    database.teachers.forEach((teacher: any) => {
      teacher.contexts?.forEach((context: any) => {
        contexts.push(context);
      });
    });

    return res.status(200).json(contexts);
  }

  return res.status(405).json({
    message: 'Método não permitido',
  });
}
