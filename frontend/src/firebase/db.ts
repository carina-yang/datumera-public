// Import the necessary Firebase modules. Assuming Firebase has been initialized elsewhere in your application.
import { collection, doc, getDoc, setDoc, addDoc, updateDoc } from 'firebase/firestore';
import { db } from './config';
import { User } from '@/models/user';
import { PLANS } from '@/models/plans';

// Function to create a user in the Firestore database
export async function createUser(uid: string, email: string) {
  // Create a reference to the specific document in the 'users' collection
  const userRef = doc(db, 'users', uid);

  // Check if the user document already exists
  const docSnap = await getDoc(userRef);
  if (docSnap.exists()) {
    // User already exists, throw an error
    console.log('User already exists')
  } else {
    // User does not exist, create a new document
    const newUser: User = {
      email: email,
      joinDate: new Date(),
      credits: PLANS[0].credits,
      stripePriceId: PLANS[0].priceId
    }

    await setDoc(userRef, newUser);
    console.log('User created successfully')
  }
}

export async function addSubscriptionToUser(userId: string, type: string) {
  try {
    const userRef = doc(db, "users", userId);
    const creditPurchasesCol = collection(userRef, "subscriptions");
    // Assuming subscriptionData.StartDate is a Date object or a date string
    const startDate = new Date();

    // Calculate EndDate by adding one month to StartDate
    let endDate = new Date(startDate);
    endDate.setMonth(startDate.getMonth() + 1);
    const docRef = await addDoc(creditPurchasesCol, {
      Type: type,
      StartDate: startDate,
      EndDate: endDate,
      Status: "active"
    });

    if (type === "basic") {
        const userRef = doc(db, "users", userId);
        await updateDoc(userRef, { credits: 1000 });
    };

    console.log("Credit purchase added with ID: ", docRef.id);
  } catch (e) {
    console.error("Error adding subscription: ", e);
  }
};
