import type { NextApiRequest, NextApiResponse } from 'next';

import { database } from '../../data/database';

export default function handler(req: NextApiRequest, res: NextApiResponse) {
  /*
    LISTAR MATÉRIAS
  */

  if (req.method === 'GET') {
    const subjects: any[] = [];

    database.teachers.forEach((teacher: any) => {
      (teacher.contexts ?? []).forEach((context: any) => {
        (context.subjects ?? []).forEach((subject: any) => {
          subjects.push(subject);
        });
      });
    });

    return res.status(200).json(subjects);
  }

  /*
    CRIAR MATÉRIA
  */

  if (req.method === 'POST') {
    const teacher = database.teachers.find(
      (item: any) => Number(item.id) === Number(req.body.teacherId),
    );

    if (!teacher) {
      return res.status(404).json({
        message: 'Professor não encontrado',
      });
    }

    const context = teacher.contexts?.find(
      (item: any) => Number(item.id) === Number(req.body.contextId),
    );

    if (!context) {
      return res.status(404).json({
        message: 'Contexto não encontrado',
      });
    }

    const newSubject = {
      id: Date.now(),

      contextId: context.id,

      name: req.body.name,

      description: req.body.description,

      importanceLevel: req.body.importanceLevel ?? 'Medium',

      classrooms: req.body.classrooms ?? [],

      files: {
        pdf: 0,

        videos: 0,

        audios: 0,

        powerpoint: 0,
      },

      activities: [],
    };

    context.subjects = context.subjects ?? [];

    context.subjects.push(newSubject);

    console.log('Matéria criada:', newSubject);

    return res.status(201).json(newSubject);
  }

  /*
    ATUALIZAR MATÉRIA
  */

  if (req.method === 'PUT') {
    const subjectId = Number(req.body.id);

    console.log('Atualizando matéria:', subjectId);

    let subject: any = null;

    let subjectContext: any = null;

    /*
      Procurar matéria dentro dos contextos
    */

    for (const teacher of database.teachers) {
      for (const context of teacher.contexts ?? []) {
        const found = (context.subjects ?? []).find((item: any) => Number(item.id) === subjectId);

        if (found) {
          subject = found;

          subjectContext = context;

          break;
        }
      }

      if (subject) {
        break;
      }
    }

    if (!subject) {
      console.log('Matéria não encontrada:', subjectId);

      console.log(JSON.stringify(database.teachers, null, 2));

      return res.status(404).json({
        message: 'Matéria não encontrada',
      });
    }

    /*
      Atualiza campos da matéria
    */

    subject.classrooms = req.body.classrooms ?? subject.classrooms ?? [];

    subject.files = subject.files ?? {
      pdf: 0,

      videos: 0,

      audios: 0,

      powerpoint: 0,
    };

    /*
      Regrava dentro do contexto
    */

    const index = subjectContext.subjects.findIndex((item: any) => Number(item.id) === subjectId);

    if (index !== -1) {
      subjectContext.subjects[index] = subject;
    }

    console.log('Matéria salva:', subject);

    return res.status(200).json(subject);
  }

  return res.status(405).json({
    message: 'Método não permitido',
  });
}
