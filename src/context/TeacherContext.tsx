import { createContext, useContext, useState, useEffect } from 'react';

interface TeacherContextProps {
  teacher: any;

  updateTeacher: (data: any) => void;
}

const TeacherContext = createContext<TeacherContextProps | null>(null);

export function TeacherProvider({ children }: any) {
  const [teacher, setTeacher] = useState({
    id: Date.now(),

    name: '',

    description: '',

    subjects: [],
  });

  const [loaded, setLoaded] = useState(false);

  // Carrega o cache quando estiver no navegador
  useEffect(() => {
    const cache = localStorage.getItem('teacher');

    if (cache) {
      setTeacher(JSON.parse(cache));
    }

    setLoaded(true);
  }, []);

  function updateTeacher(data: any) {
    const updated = {
      ...teacher,

      ...data,
    };

    setTeacher(updated);

    localStorage.setItem(
      'teacher',

      JSON.stringify(updated),
    );
  }

  if (!loaded) {
    return null;
  }

  return (
    <TeacherContext.Provider
      value={{
        teacher,

        updateTeacher,
      }}
    >
      {children}
    </TeacherContext.Provider>
  );
}

export function useTeacher() {
  const context = useContext(TeacherContext);

  if (!context) {
    throw new Error('useTeacher deve estar dentro do TeacherProvider');
  }

  return context;
}
