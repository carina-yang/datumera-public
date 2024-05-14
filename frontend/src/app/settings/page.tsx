'use client'
import MaxWidthWrapper from "@/components/MaxWidthWrapper"
import { Button } from "@/components/ui/button";
import { Separator } from "@/components/ui/separator";
import { BuyCreditsDialog } from "@/components/BuyCreditsDialog";
import { useState } from 'react';
import { useAuth } from "@/context/AuthContextProvider";
import { redirect } from 'next/navigation'
import { useUserData } from "@/lib/hooks";

const Settings = () => {
    const { user } = useAuth();
    if (!user || !user.uid) redirect('/')
    const [isLoading, setIsLoading] = useState(false);
    const data = useUserData(`users/${user.uid}`);

    const handleUpgradeClick = async () => {
        setIsLoading(true);
        try {
            const idToken = await user.getIdToken();

            const response = await fetch('http://localhost:8000/create-checkout-session', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${idToken}`,  // Include the ID token in the Authorization header
                },
                body: JSON.stringify({
                    'lookup_key': 'premium'
                })
            });           
            if (response.ok) {
                const checkoutSession = await response.json();
                window.location.href = checkoutSession.url; // Redirect to Stripe checkout
            } else {
                // Handle errors, e.g., show an error message
                const errorResponse = await response.json();
                console.error('Failed to upgrade:', errorResponse.error);
            }            
        } catch (error) {
            console.error('Failed to upgrade:', error);
        } finally {
            setIsLoading(false);
        }
    };


    return (   
    <>
    <MaxWidthWrapper>
      <div className="hidden space-y-6 pb-16 pt-6 md:block">
        <div className="space-y-0.5">
          <h2 className="text-2xl font-bold tracking-tight">Account</h2>
          <p className="text-muted-foreground">
            Manage your account settings.
          </p>
        </div>
        <Separator className="my-4"/>
        <div className="space-y-6">
            <div>
                <h3 className="text-lg font-medium">Account information</h3>
            </div>
            <div>        
            <h3 className="text-sm font-medium">Email</h3>
            <p className="text-sm">
                {data?.email}
            </p>
            </div>
        </div>
        <Separator  className=" my-4"/>
        <div className='space-y-6'>
            <div>
                <h3 className="text-lg font-medium">Billing & plans</h3>
                <p className="text-sm text-muted-foreground">
                    Your plan and credits information is here.
                </p>
            </div>
        <div className='space-y-8'>
            <form>
                <div >
                    <div className='flex flex-col space-y-2'>        
                        <h3 className="text-sm font-medium">Plan</h3>
                        <p className="text-sm">
                            You are currently on the <strong>{ data?.stripePriceId === 'basic' ? `Basic` : `Premium`}</strong> plan. Your free trial will end.
                        </p>
                        <p className="text-sm">You currently have {data?.credits} remaining credits.</p>
                    </div>
                <div className='flex flex-col items-start md:flex-row md:space-x-0 md:justify-start md:gap-4 md:items-center mt-4'>
                    {data?.stripePriceId === 'basic' ? 
                        <Button type='button' onClick={handleUpgradeClick} disabled={isLoading}>
                            Upgrade to PRO
                        </Button> :
                        <Button type='button' onClick={handleUpgradeClick} disabled={isLoading}>
                            Manage Subscription
                        </Button>}
                    <BuyCreditsDialog />
                </div>
                </div>
            </form>
        </div>
      </div>
      </div>
      </MaxWidthWrapper>
    </>
    );
};

export default Settings;