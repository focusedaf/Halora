"use client";

import { Textarea } from "../ui/textarea";
import { Message } from "../ui/message";
import { LucideArrowBigUpDash } from "lucide-react";

interface ChatInterfaceProps {
  placeholder?: string;
  onSend?: (message: string) => void;
}

const ChatInterface = ({
  placeholder = "Say something...",
  onSend,
}: ChatInterfaceProps) => {
  return (
    <div className="flex min-h-screen w-full flex-col items-center justify-end px-4 pb-8">
      <div className="w-full max-w-xl">
        <div className="relative">
          <Textarea
            className="
              w-full
              resize-none
              rounded
              border
              border-zinc-300
              p-3
              pr-12
              shadow-xl
              dark:border-zinc-800
              dark:bg-zinc-900
            "
            placeholder={placeholder}
          />

          <button
            className="
              absolute
              bottom-3
              right-3
              rounded
              p-1
              hover:bg-zinc-800
            "
            type="button"
            onClick={() => onSend?.("hello")}
          >
            <LucideArrowBigUpDash className="h-5 w-5" />
          </button>
        </div>

        <Message />
      </div>
    </div>
  );
};

export default ChatInterface;
