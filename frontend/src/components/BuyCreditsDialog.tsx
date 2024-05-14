'use client'
import { Button } from "@/components/ui/button"
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog"
import { Label } from "@/components/ui/label"
import { useState } from "react"

export function BuyCreditsDialog() {
    const [chosenCredits, setChosenCredits] = useState(0);

  return (
    <Dialog>
      <DialogTrigger asChild>
        <Button variant="outline">Buy more credits</Button>
      </DialogTrigger>
      <DialogContent className="sm:max-w-[425px]">
        <DialogHeader>
          <DialogTitle>Buy more credits</DialogTitle>
          <DialogDescription>
            You have 10 remaining credits. Click on one of the options below to buy more.
          </DialogDescription>
        </DialogHeader>
        <div className="grid grid-cols-3 gap-4 py-2 px-2">
          <div className="grid items-center gap-2">
            <Label htmlFor="name" className="text-center">
              10,000 credits
            </Label>
            <Button 
              disabled={chosenCredits === 10000} 
              onClick={() => setChosenCredits(10000)}>
                $9
            </Button>
          </div>
          <div className="grid items-center gap-2">
            <Label htmlFor="name" className="text-center">
              20,000 credits
            </Label>
            <Button 
              disabled={chosenCredits === 20000} 
              onClick={() => setChosenCredits(20000)}>
                $19
            </Button>
          </div>
          <div className="grid items-center gap-2">
            <Label htmlFor="username" className="text-center">
                100,000 credits
            </Label>
            <Button 
              disabled={chosenCredits === 100000} 
              onClick={() => setChosenCredits(100000)}>
                $90
            </Button>
          </div>
        </div>
        <DialogFooter>
          <Button type="submit">Go to checkout</Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  )
}
