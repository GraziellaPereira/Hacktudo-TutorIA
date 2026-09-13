export interface TeacherCreateRequest {
  name: string;

  description: string;

  email?: string;
}

export interface TeacherResponse {
  teacher_id: string;
}

// Criar professor

export async function createTeacher(data: TeacherCreateRequest): Promise<TeacherResponse> {
  const response = await fetch('/api/teachers', {
    method: 'POST',

    headers: {
      'Content-Type': 'application/json',
    },

    body: JSON.stringify(data),
  });

  if (!response.ok) {
    throw new Error('Erro ao criar professor');
  }

  return response.json();
}

// Buscar professor pelo Teacher ID

export async function getTeacher(teacherId: string) {
  const response = await fetch(`/api/teachers/${teacherId}`);

  if (!response.ok) {
    throw new Error('Professor não encontrado');
  }

  return response.json();
}

// Atualizar professor

export async function updateProfile(teacherId: string, data: any) {
  const response = await fetch(`/api/profile?teacherId=${encodeURIComponent(teacherId)}`, {
    method: 'PUT',

    headers: {
      'Content-Type': 'application/json',
    },

    body: JSON.stringify({ ...data, teacherId }),
  });

  if (!response.ok) {
    throw new Error('Erro ao atualizar perfil');
  }

  return response.json();
}

// Adicionar matéria

export async function addSubject(data: any) {
  const response = await fetch('/api/subjects', {
    method: 'POST',

    headers: {
      'Content-Type': 'application/json',
    },

    body: JSON.stringify(data),
  });

  if (!response.ok) {
    throw new Error('Erro ao adicionar matéria');
  }

  return response.json();
}
