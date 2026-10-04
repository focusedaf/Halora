"use client";

import * as React from "react";

import {
  Plus,
  ArrowUp,
  ArrowDown,
  Maximize2,
  Minimize2,
  Image as ImageIcon,
  Paperclip,
  FileText,
} from "lucide-react";

import { Textarea } from "../ui/textarea";
import { Message } from "../ui/message";

import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "../ui/dropdown-menu";

interface ChatInterfaceProps {
  placeholder?: string;
  onSend?: (message: string) => void;
}

const SINGLE_LINE_HEIGHT = 56;
const COLLAPSED_MAX = 192;
const EXPANDED_MIN = 192;
const EXPANDED_MAX = 360;

const ChatInterface = ({
  placeholder = "Ask Halora",
  onSend,
}: ChatInterfaceProps) => {
  const [value, setValue] = React.useState("");
  const [expanded, setExpanded] = React.useState(false);
  const [isMultiline, setIsMultiline] = React.useState(false);
  const [showScrollButton, setShowScrollButton] = React.useState(false);

  const messagesRef = React.useRef<HTMLDivElement>(null);
  const textareaRef = React.useRef<HTMLTextAreaElement>(null);
  const fileInputRef = React.useRef<HTMLInputElement>(null);

 
  const resizeTextarea = React.useCallback(() => {
    const el = textareaRef.current;

    if (!el) return;

    el.style.height = "0px";

    const contentHeight = el.scrollHeight;

    const minHeight = SINGLE_LINE_HEIGHT;
    const maxHeight = expanded ? EXPANDED_MAX : COLLAPSED_MAX;

    const nextHeight = Math.min(Math.max(contentHeight, minHeight), maxHeight);

    el.style.height = `${nextHeight}px`;

    const multiline = contentHeight > SINGLE_LINE_HEIGHT + 4;

    setIsMultiline(multiline);

    el.style.overflowY = contentHeight > maxHeight ? "auto" : "hidden";
  }, [expanded]);

  React.useLayoutEffect(() => {
    resizeTextarea();
  }, [value, expanded, resizeTextarea]);

  const handleSend = () => {
    const message = value.trim();

    if (!message) return;

    onSend?.(message);

    setValue("");
    setExpanded(false);

    requestAnimationFrame(() => {
      textareaRef.current?.focus();
    });
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  const handleScroll = () => {
    const container = messagesRef.current;

    if (!container) return;

    const distanceFromBottom =
      container.scrollHeight - container.scrollTop - container.clientHeight;

    setShowScrollButton(distanceFromBottom > 120);
  };

  const scrollToBottom = () => {
    const container = messagesRef.current;

    if (!container) return;

    container.scrollTo({
      top: container.scrollHeight,
      behavior: "smooth",
    });
  };

  const openFilePicker = () => {
    fileInputRef.current?.click();
  };

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const files = e.target.files;

    if (!files?.length) return;

    console.log("Selected files:", Array.from(files));

    e.target.value = "";
  };

  return (
    <div className="relative flex min-h-screen w-full flex-col items-center justify-end px-4 pb-8">
   
      <div
        ref={messagesRef}
        onScroll={handleScroll}
        className="
          absolute
          inset-x-0
          top-0
          bottom-32
          overflow-y-auto
          px-4
          scrollbar-thin
          scrollbar-track-transparent
          scrollbar-thumb-zinc-700
          hover:scrollbar-thumb-zinc-600
        "
      >
        <div className="mx-auto w-full max-w-3xl pb-8">
          <Message />
        </div>
      </div>

     
      {showScrollButton && (
        <button
          type="button"
          aria-label="Scroll to bottom"
          onClick={scrollToBottom}
          className="
            absolute
            bottom-28
            left-1/2
            z-20
            flex
            size-9
            -translate-x-1/2
            items-center
            justify-center
            rounded-full
            border
            border-zinc-700
            bg-zinc-900
            text-zinc-300
            shadow-lg
            transition-all
            hover:bg-zinc-800
            hover:text-white
            active:scale-95
          "
        >
          <ArrowDown className="size-4" />
        </button>
      )}

    
      <div className="relative z-30 w-full max-w-3xl">
        <input
          ref={fileInputRef}
          type="file"
          multiple
          className="hidden"
          onChange={handleFileChange}
        />

        <div
          className="
            relative
            w-full
            rounded-[28px]
            border
            border-zinc-800
            bg-zinc-900
            shadow-lg
            transition-[height,border-radius]
            duration-150
          "
        >
          
          <Textarea
            ref={textareaRef}
            value={value}
            onChange={(e) => setValue(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder={placeholder}
            rows={1}
            className="
              block
              w-full
              resize-none
              overflow-y-hidden
              rounded-[28px]
              border-0
              bg-transparent
              py-4
              pl-14
              pr-28
              text-base
              leading-6
              text-zinc-100
              shadow-none
              outline-none
              placeholder:text-zinc-400
              placeholder:text-xl
              focus-visible:border-0
              focus-visible:ring-0
              scrollbar-thin
              scrollbar-track-transparent
              scrollbar-thumb-zinc-700
              hover:scrollbar-thumb-zinc-600
            "
            style={{
              minHeight: SINGLE_LINE_HEIGHT,
              maxHeight: expanded ? EXPANDED_MAX : COLLAPSED_MAX,
            }}
          />

        
          <DropdownMenu>
            <DropdownMenuTrigger
              render={
                <button
                  type="button"
                  aria-label="Add attachment"
                  className="
                    absolute
                    bottom-3
                    left-3
                    flex
                    size-8
                    items-center
                    justify-center
                    rounded-full
                    text-zinc-300
                    outline-none
                    transition-all
                    hover:bg-zinc-800
                    hover:text-white
                    data-[state=open]:bg-zinc-800
                    data-[state=open]:text-white
                  "
                >
                  <Plus className="size-5" />
                </button>
              }
            />

            <DropdownMenuContent
              side="top"
              align="start"
              sideOffset={10}
              className="w-52 rounded-xl border-zinc-800 bg-zinc-900 p-1.5"
            >
              <DropdownMenuItem
                onClick={openFilePicker}
                className="gap-3 rounded-lg py-2.5"
              >
                <Paperclip className="size-4 text-zinc-400" />

                <div className="flex flex-col">
                  <span>Upload files</span>
                  <span className="text-xs text-zinc-500">
                    Documents and files
                  </span>
                </div>
              </DropdownMenuItem>

              <DropdownMenuItem
                onClick={openFilePicker}
                className="gap-3 rounded-lg py-2.5"
              >
                <ImageIcon className="size-4 text-zinc-400" />

                <div className="flex flex-col">
                  <span>Upload images</span>
                  <span className="text-xs text-zinc-500">PNG, JPG, WEBP</span>
                </div>
              </DropdownMenuItem>

              <DropdownMenuSeparator className="bg-zinc-800" />

              <DropdownMenuItem
                onClick={openFilePicker}
                className="gap-3 rounded-lg py-2.5"
              >
                <FileText className="size-4 text-zinc-400" />

                <div className="flex flex-col">
                  <span>Add document</span>
                  <span className="text-xs text-zinc-500">PDF, DOCX, TXT</span>
                </div>
              </DropdownMenuItem>
            </DropdownMenuContent>
          </DropdownMenu>

       
          {isMultiline && (
            <button
              type="button"
              aria-label={expanded ? "Collapse composer" : "Expand composer"}
              onClick={() => setExpanded((current) => !current)}
              className="
                absolute
                right-3
                top-3
                flex
                size-8
                items-center
                justify-center
                rounded-full
                text-zinc-400
                outline-none
                transition-colors
                hover:bg-zinc-800
                hover:text-white
              "
            >
              {expanded ? (
                <Minimize2 className="size-4" />
              ) : (
                <Maximize2 className="size-4" />
              )}
            </button>
          )}

        
          <button
            type="button"
            aria-label="Send message"
            onClick={handleSend}
            className="
              absolute
              bottom-3
              right-3
              flex
              size-8
              items-center
              justify-center
              rounded-full
              bg-blue-600
              text-white
              outline-none
              transition-all
              hover:bg-blue-500
              active:scale-95
            "
          >
            <ArrowUp className="size-4" strokeWidth={2.5} />
          </button>
        </div>
      </div>
    </div>
  );
};

export default ChatInterface;
