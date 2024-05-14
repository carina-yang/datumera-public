export interface User {
    email: string;
    joinDate: Date;
    stripePriceId: string;
    credits: number;
    stripeCustomerId?: string;
    stripeSubscriptionId?: string;
    stripeCurrentPeriodEnd?: Date;
  }