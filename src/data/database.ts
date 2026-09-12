const initialDatabase = {
  teachers: [
    {
      id: 1,

      name: 'Mariana Oliveira',

      description: 'Professora de Ciências',

      contexts: [] as any[],
    },
  ],

  contexts: [] as any[],
};

const globalDatabase = globalThis as typeof globalThis & {
  database?: typeof initialDatabase;
};

export const database = globalDatabase.database ?? initialDatabase;

if (!globalDatabase.database) {
  globalDatabase.database = database;
}
