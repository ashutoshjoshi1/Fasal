"use client";

import { createContext, useContext, useMemo, useState } from "react";

const FieldContext = createContext<{ fieldId: string | null; setFieldId: (id: string) => void }>({
  fieldId: null,
  setFieldId: () => {},
});

export const useSelectedField = () => useContext(FieldContext);

export function SelectedFieldProvider({ children }: { children: React.ReactNode }) {
  const [fieldId, setFieldId] = useState<string | null>(null);
  const value = useMemo(() => ({ fieldId, setFieldId }), [fieldId]);
  return <FieldContext.Provider value={value}>{children}</FieldContext.Provider>;
}
