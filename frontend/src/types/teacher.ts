export interface Teacher {
  id: number;

  name: string;

  description: string;

  contexts: Context[];
}

export interface Context {
  id: number;

  name: string;

  description: string;

  subjects: Subject[];
}

export interface Subject {
  id: number;

  name: string;

  description: string;

  importanceLevel: ImportanceLevel;

  classrooms: Classroom[];

  files: SubjectFiles;
}

export interface Classroom {
  id: number;

  name: string;

  year: string;

  educationLevels: string[];

  observations: string;

  studentsCount: number;
}

export interface SubjectFiles {
  pdf: number;

  powerpoint: number;
}

export type ImportanceLevel = 'Low' | 'Medium' | 'High';
