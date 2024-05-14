import { useState, useEffect } from 'react';
import { doc, onSnapshot, DocumentData } from 'firebase/firestore';
import { db } from '@/firebase/config';
import { User } from '@/models/user';

export function useUserData(docPath: string) {
  // Explicitly define the type of `data` state to be `DocumentData | null`
  const [data, setData] = useState<User| null>(null);

  useEffect(() => {
    const docRef = doc(db, docPath);
    const unsubscribe = onSnapshot(docRef, (doc) => {
      setData(doc.exists() ? doc.data() as User: null);
    });

    // Cleanup on unmount
    return () => unsubscribe();
  }, [docPath]);

  return data;
}
