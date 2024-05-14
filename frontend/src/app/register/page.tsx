'use client'

import MaxWidthWrapper from "@/components/MaxWidthWrapper"
import Link from "next/link"
import { useState, SyntheticEvent } from "react"
import { useRouter } from "next/navigation"
import { Button } from "@/components/ui/button"
import { Label } from "@/components/ui/label"
import { Input } from "@/components/ui/input"
import { signUp, signInWithGoogle } from "@/firebase/auth"
import { Loader2 } from "lucide-react"
import { Icons } from "@/components/ui/icons"

const Page = () => {
    const [isLoading, setIsLoading] = useState<boolean>(false)
    const [password, setPassword] = useState<string>("")
    const [reenterPassword, setReenterPassword] = useState<string>("")
    const [errorMessage, setErrorMessage] = useState<string | null>(null);
    const [email, setEmail] = useState<string>("");
    const router = useRouter()
  
    async function onSubmit(event: SyntheticEvent) {
      event.preventDefault()
  
      if (password !== reenterPassword) {
        setErrorMessage("Passwords do not match!");
        return;
      } else {
        setErrorMessage(null); // clear the error if passwords do match
      }
  
      setIsLoading(true)
  
      const { result, error } = await signUp(email, password);
  
      if (error) {
        setErrorMessage("Oops! Something went wrong!")
        return
      } else {
        setErrorMessage(null)
      }
  
      setIsLoading(false)
      return router.push("/translate")
    }

    async function googleSignIn() {
        signInWithGoogle();
        router.push("/translate")
    }

    return (
        <>
            <MaxWidthWrapper>
            <div className="container relative hidden h-[800px] flex-col items-center justify-center md:grid lg:max-w-none lg:px-0">
                <div className="lg:p-8">
                <div className="mx-auto flex w-full flex-col justify-center space-y-6 sm:w-[350px]">
                    <div className="flex flex-col space-y-2 text-center">
                    <h1 className="text-2xl font-semibold tracking-tight">
                        Register
                    </h1>
                    <p className="text-sm text-muted-foreground">
                        Enter your email and a password to create your account
                    </p>
                    </div>
                    <div className="grid gap-6">
                    <form onSubmit={onSubmit}>
                        <div className="grid gap-2">
                        <div className="grid gap-1">
                            <Label className="block text-sm font-medium leading-6 text-gray-900" htmlFor="email">
                            Email
                            </Label>
                            <Input
                            id="email"
                            placeholder="Email Address"
                            type="email"
                            autoCapitalize="none"
                            autoComplete="email"
                            autoCorrect="off"
                            disabled={isLoading}
                            onChange={(e) => setEmail(e.target.value)}
                            value={email}
                            />
                        </div>
                        <div className="grid gap-1">
                            <div className="flex items-center justify-between">
                            <Label className="block text-sm font-medium leading-6 text-gray-900" htmlFor="password">
                                Password
                            </Label>
                            </div>
                            <Input
                            id="password"
                            placeholder="Password"
                            type="password"
                            autoCapitalize="none"
                            autoComplete="current-password"
                            autoCorrect="off"
                            required
                            disabled={isLoading}
                            onChange={(e) => setPassword(e.target.value)}
                            value={password}
                            />
                        </div>
                        <div className="grid gap-1">
                        <Label className="block text-sm font-medium leading-6 text-gray-900" htmlFor="reenter-password">
                            Re-enter password
                        </Label>
                        <Input
                            id="reenter-password"
                            placeholder="Password"
                            type="password"
                            autoCapitalize="none"
                            autoComplete="current-password"
                            autoCorrect="off"
                            required
                            value={reenterPassword}
                            onChange={(e) => setReenterPassword(e.target.value)}
                            disabled={isLoading}
                        />
                        {errorMessage && <div className="text-red-500 text-sm mt-1">{errorMessage}</div>}
                        </div>
                        <Button type="submit" disabled={isLoading}>
                            {isLoading && (
                            <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                            )}
                            Create Account
                        </Button>
                        </div>
                    </form>
                    <div className="relative">
                        <div className="absolute inset-0 flex items-center">
                        <span className="w-full border-t" />
                        </div>
                        <div className="relative flex justify-center text-xs uppercase">
                        <span className="bg-background px-2 text-muted-foreground">
                            Or continue with
                        </span>
                        </div>
                    </div>
                    <Button onClick={googleSignIn} variant="outline" type="button" disabled={isLoading}>
                        {isLoading ? (
                        <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                        ) : (
                        <Icons.google className="mr-2 h-4 w-4" />
                        )}{" "}
                        Google
                    </Button>
                    </div>
                    <p className="px-8 text-center text-sm text-muted-foreground">
                    By clicking continue, you agree to our{" "}
                    <Link
                        href="/terms"
                        className="underline underline-offset-4 hover:text-primary"
                    >
                        Terms of Service
                    </Link>{" "}
                    and{" "}
                    <Link
                        href="/privacy"
                        className="underline underline-offset-4 hover:text-primary"
                    >
                        Privacy Policy
                    </Link>
                    .
                    </p>
                </div>
                </div>
                </div>
            </MaxWidthWrapper>
        </>
    )

}

export default Page