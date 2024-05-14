import { auth } from "./config";
import { addSubscriptionToUser, createUser } from "./db";
import { signInWithEmailAndPassword, GoogleAuthProvider, signInWithPopup, signOut, createUserWithEmailAndPassword } from "firebase/auth";

export async function signIn(email: string, password: string) {
    let result = null,
        error = null;
    try {
        result = await signInWithEmailAndPassword(auth, email, password);
    } catch (e) {
        error = e;
    }

    return { result, error };
}

export async function signInWithGoogle() {
    const provider = new GoogleAuthProvider();
    let result, error = null
  try {
    result = await signInWithPopup(auth, provider);
    createUser(result.user.uid, result.user.email ?? '');
  } catch (e) {
    error = e
  }
  return { result, error }
};

export async function signOutUser() {
    let result = null,
    error = null;
  try {
    result = await signOut(auth);
  } catch (e) {
    error = e
  }
  return { result, error }
};

export async function signUp(email: string, password: string) {
    let result = null,
        error = null;
    try {
        result = await createUserWithEmailAndPassword(auth, email, password);
        createUser(result.user.uid, email);
    } catch (e) {
        error = e;
    }

    return { result, error };
}