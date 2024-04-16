'use client'
import { cn } from '@/lib/utils'
import { PaperPlaneIcon, StopIcon } from '@radix-ui/react-icons'
import { AnimatePresence, motion } from 'framer-motion'
import React from 'react'
import TextareaAutosize from 'react-textarea-autosize'
import { Button } from '../ui/button'
import { ChatRequestOptions } from 'ai'
import { useToast } from '../ui/use-toast'

interface ChatBottombarProps {
  input: string;
  handleInputChange: (e: React.ChangeEvent<HTMLTextAreaElement>) => void;
  handleSubmit: (e: React.FormEvent<HTMLFormElement>, chatRequestOptions?: ChatRequestOptions) => void;
  isLoading: boolean;
  stop: () => void;
}

export default function ChatBottombar({
  input,
  handleInputChange,
  handleSubmit,
  isLoading,
  stop,
}: ChatBottombarProps) {
  const [isMobile, setIsMobile] = React.useState(false)
  const {toast}=useToast();
  const inputRef = React.useRef<HTMLTextAreaElement>(null)

  React.useEffect(() => {
    const checkScreenWidth = () => {
      setIsMobile(window.innerWidth <= 768)
    }

    // Initial check
    checkScreenWidth()

    // Event listener for screen width changes
    window.addEventListener('resize', checkScreenWidth)

    // Cleanup the event listener on component unmount
    return () => {
      window.removeEventListener('resize', checkScreenWidth)
    }
  }, [])

  const onSubmit = (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault()
    if(input.trim().length===0){
      toast({
        variant:'destructive',
        description:'Cannot send empty string.'  
      })
    }else{
      handleSubmit(e);
    }
  }

  const handleKeyPress = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      onSubmit(e as unknown as React.FormEvent<HTMLFormElement>)
    }
  }

  return (
    <div className="p-4 flex justify-between w-full items-center gap-2">
      <AnimatePresence initial={false}>
        <motion.div
          key="input"
          className="w-full relative mb-2 items-center"
          layout
          initial={{ opacity: 0, scale: 1 }}
          animate={{ opacity: 1, scale: 1 }}
          exit={{ opacity: 0, scale: 1 }}
          transition={{
            opacity: { duration: 0.05 },
            layout: {
              type: 'spring',
              bounce: 0.15,
            },
          }}
        >
          <form
            onSubmit={onSubmit}
            className="w-full items-center flex relative gap-2"
          >
            {/* <div className="flex">
              <Link
                href="#"
                className={cn(
                  buttonVariants({ variant: 'secondary', size: 'icon' }),
                )}
              >
                <ImageIcon className="w-6 h-6 text-muted-foreground" />
              </Link>
            </div> */}

            <TextareaAutosize
              autoComplete="off"
              value={input}
              ref={inputRef}
              onKeyDown={handleKeyPress}
              onChange={handleInputChange}
              name="message"
              placeholder="Ask MedBot anything..."
              className="border-input max-h-20 px-5 py-4 text-sm shadow-sm placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring disabled:cursor-not-allowed disabled:opacity-50 w-full border rounded-full flex items-center h-14 resize-none overflow-hidden dark:bg-card/35"
            />
            {!isLoading ? (
              <Button
                className={cn("shrink-0",input.trim().length===0&&"cursor-not-allowed")}
                variant="secondary"
                size="icon"
                type="submit"
              >
                <PaperPlaneIcon className=" w-6 h-6 text-muted-foreground" />
              </Button>
            ) : (
              <Button
                className="shrink-0"
                variant="secondary"
                size="icon"
                onClick={stop}
              >
                <StopIcon className="w-6 h-6  text-muted-foreground" />
              </Button>
            )}
          </form>
        </motion.div>
      </AnimatePresence>
    </div>
  )
}
