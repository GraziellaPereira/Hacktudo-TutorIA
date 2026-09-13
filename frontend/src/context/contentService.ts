export interface CreateContentRequest {
  teacherId: string | number;

  title: string;

  subject: string;

  educationLevel: string;

  gradeOrPeriod: string;

  targetAudience: string;

  learningGoal: string;

  assessmentFocus: string[];

  contextId?: string;

  classroomId?: string;

  subjectId?: string;

  file: File;
}

export async function createTeacherContent(data: CreateContentRequest) {
  const formData = new FormData();

  formData.append('title', data.title);

  formData.append('subject', data.subject);

  formData.append('education_level', data.educationLevel);

  formData.append('grade_or_period', data.gradeOrPeriod);

  formData.append('target_audience', data.targetAudience);

  formData.append('learning_goal', data.learningGoal);

  data.assessmentFocus.forEach((item) => {
    formData.append('assessment_focus', item);
  });

  if (data.contextId) formData.append('context_id', data.contextId);
  if (data.classroomId) formData.append('classroom_id', data.classroomId);
  if (data.subjectId) formData.append('subject_id', data.subjectId);

  formData.append('file', data.file);

  const response = await fetch(`/api/teachers/${data.teacherId}/contents`, {
    method: 'POST',

    body: formData,
  });

  if (!response.ok) {
    throw new Error('Erro ao importar conteúdo');
  }

  return response.json();
}

export async function getTeacherContents(teacherId: string | number) {
  const response = await fetch(`/api/teachers/${teacherId}/contents`);

  if (!response.ok) {
    throw new Error('Erro ao carregar conteúdos');
  }

  return response.json();
}
