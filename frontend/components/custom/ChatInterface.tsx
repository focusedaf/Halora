import { Textarea } from "../ui/textarea";
import { Bubble } from "../ui/bubble";
import { Message } from "../ui/message";
import { Spinner } from "../ui/spinner";
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
    <div className="fixed bottom-0 w-full max-w-xl mb-8 relative">
      <div>
        <Textarea
          className="dark:bg-zinc-900 w-full p-3 pr-12 border border-zinc-300 dark:border-zinc-800 rounded shadow-xl resize-none"
          placeholder={placeholder}
        />

        <button
          className="absolute right-3 bottom-3 p-1 rounded hover:bg-zinc-800"
          type="button"
          onClick={() => onSend?.("hello")}
        >
          <LucideArrowBigUpDash className="w-5 h-5" />
        </button>
      </div>

      <Message />
    </div>
  );
};

export default ChatInterface;
