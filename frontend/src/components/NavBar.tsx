"use client"
import Link from "next/link"
import MaxWidthWrapper from "./MaxWidthWrapper"
import { buttonVariants } from "./ui/button"
import { ArrowRight } from "lucide-react"
import { useAuth } from '../context/AuthContextProvider';
import { Button } from "./ui/button"
import { signOutUser } from "@/firebase/auth"
import { useRouter } from "next/navigation"


const NavBar = () => {
    const { user } = useAuth();
    const router = useRouter()

    async function handleClick() {
        signOutUser();

        router.push('/');
    }

    return (
        <nav className="sticky h-16 inset-x-0 top-0 z-30 w-full border-b border-gray-200 bg-white/75 backdrop-blur-lg transition-all">
            <MaxWidthWrapper>
                <div className="flex h-16 items-center justify-between border-b border-zinc-200">
                    <Link 
                        href="/" 
                        className="flex z-40 font-semibold">
                            <span>DatumEra</span>
                    </Link>

                    <div className="hidden items-center space-x-4 sm:flex">
                        <>
                            {user && <><Link 
                                href="/translate"
                                className={buttonVariants({
                                    variant: 'ghost',
                                    size: 'sm',
                                })}>
                                Translate
                            </Link>
                            <Link 
                                href="/settings"
                                className={buttonVariants({
                                    variant: 'ghost',
                                    size: 'sm',
                                })}>
                                Account settings
                            </Link></>}
                            {!user && <Link
                                href="/login"
                                className={buttonVariants({
                                    variant: 'ghost',
                                    size: 'sm',
                                })}>
                                Sign in
                            </Link>}
                            {!user && <Link
                                href="/register"
                                className={buttonVariants({
                                    size: "sm"
                                })}>
                                Get started{' '}<ArrowRight className='ml-1.5 h-5 w-5' />
                            </Link>}
                            {user && <Button
                                onClick={handleClick}
                                className={buttonVariants({
                                    size: "sm"
                                })}>
                                Sign Out
                            </Button>}
                        </>
                    </div>
                </div>
            </MaxWidthWrapper>
        </nav>
    )
}

export default NavBar