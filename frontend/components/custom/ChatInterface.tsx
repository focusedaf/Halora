"use client";

import * as React from "react";

import {
  Plus,
  ArrowUp,
  Maximize2,
  Minimize2,
  Image as ImageIcon,
  Paperclip,
  FileText,
  Copy,
  Pencil,
  Check,
} from "lucide-react";

import { Textarea } from "../ui/textarea";
import {
  Message,
  MessageGroup,
  MessageContent,
  MessageFooter,
} from "../ui/message";
import { Bubble, BubbleContent } from "../ui/bubble";
import {
  MessageScrollerProvider,
  MessageScroller,
  MessageScrollerViewport,
  MessageScrollerContent,
  MessageScrollerItem,
  MessageScrollerButton,
} from "../ui/message-scroller";
import { Skeleton } from "../ui/skeleton";
import { Spinner } from "../ui/spinner";

import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "../ui/dropdown-menu";

import {
  analyzeResponse,
  type VerificationResponse,
  type UrlHealthBatchResponse,
} from "@/lib/api";

import VerificationResult, { UrlHealthResult } from "./VerificationResult";

interface ChatInterfaceProps {
  placeholder?: string;
  onSend?: (message: string) => void | Promise<void>;
}

interface ChatMessage {
  id: number;
  content: string;
  verification?: VerificationResponse;
  urlHealth?: UrlHealthBatchResponse | null;
  error?: string;
}

const URL_REGEX = /https?:\/\/[^\s<>"')\]]+|www\.[^\s<>"')\]]+/gi;


function isUrlOnly(text: string) {
  const leftover = text.replace(URL_REGEX, "").replace(/[\s,;|\-–•*]+/g, "");
  return leftover.length === 0;
}

const SINGLE_LINE_HEIGHT = 56;
const COLLAPSED_MAX = 192;
const COLLAPSED_MULTILINE_MIN = 96;
const EXPANDED_MAX = 360;

const ChatInterface = ({
  placeholder = "Ask Halora",
  onSend,
}: ChatInterfaceProps) => {
  const [value, setValue] = React.useState("");
  const [expanded, setExpanded] = React.useState(false);
  const [isMultiline, setIsMultiline] = React.useState(false);
  const [messages, setMessages] = React.useState<ChatMessage[]>([]);
  const [editingId, setEditingId] = React.useState<number | null>(null);
  const [copiedId, setCopiedId] = React.useState<number | null>(null);
  const [isSending, setIsSending] = React.useState(false);

  const textareaRef = React.useRef<HTMLTextAreaElement>(null);
  const fileInputRef = React.useRef<HTMLInputElement>(null);

  const resizeTextarea = React.useCallback(() => {
    const el = textareaRef.current;

    if (!el) return;

    el.style.height = "0px";

    const contentHeight = el.scrollHeight;
    const multiline = contentHeight > SINGLE_LINE_HEIGHT + 4;

    setIsMultiline(multiline);

    if (!multiline) {
      el.style.height = `${SINGLE_LINE_HEIGHT}px`;
      el.style.overflowY = "hidden";

      if (expanded) {
        setExpanded(false);
      }

      return;
    }

    if (expanded) {
      el.style.height = `${EXPANDED_MAX}px`;
      el.style.overflowY = contentHeight > EXPANDED_MAX ? "auto" : "hidden";
      return;
    }

    const nextHeight = Math.min(
      Math.max(contentHeight, COLLAPSED_MULTILINE_MIN),
      COLLAPSED_MAX,
    );

    el.style.height = `${nextHeight}px`;
    el.style.overflowY = contentHeight > COLLAPSED_MAX ? "auto" : "hidden";
  }, [expanded]);

  React.useLayoutEffect(() => {
    resizeTextarea();
  }, [value, expanded, resizeTextarea]);

  const handleSend = async () => {
    const message = value.trim();

    if (!message || isSending) return;

    if (editingId !== null) {
      setMessages((current) =>
        current.map((item) =>
          item.id === editingId
            ? {
                ...item,
                content: message,
                verification: undefined,
                urlHealth: undefined,
                error: undefined,
              }
            : item,
        ),
      );

      setEditingId(null);
      setValue("");
      setExpanded(false);

      requestAnimationFrame(() => {
        textareaRef.current?.focus();
      });

      return;
    }

    const messageId = Date.now();

    const newMessage: ChatMessage = {
      id: messageId,
      content: message,
    };

    setMessages((current) => [...current, newMessage]);
    setValue("");
    setExpanded(false);
    setIsSending(true);

    try {
      const analysis = await analyzeResponse(message, 5);

      setMessages((current) =>
        current.map((item) =>
          item.id === messageId
            ? {
                ...item,
                verification: analysis.verification,
                urlHealth: analysis.urlHealth,
              }
            : item,
        ),
      );

      await onSend?.(message);
    } catch (error) {
      const errorMessage =
        error instanceof Error
          ? error.message
          : "Unable to verify the response.";

      setMessages((current) =>
        current.map((item) =>
          item.id === messageId
            ? {
                ...item,
                error: errorMessage,
              }
            : item,
        ),
      );
    } finally {
      setIsSending(false);

      requestAnimationFrame(() => {
        textareaRef.current?.focus();
      });
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      void handleSend();
    }
  };

  const handleCopy = async (message: ChatMessage) => {
    try {
      await navigator.clipboard.writeText(message.content);
      setCopiedId(message.id);

      window.setTimeout(() => {
        setCopiedId((current) => (current === message.id ? null : current));
      }, 1500);
    } catch {
      return;
    }
  };

  const handleEdit = (message: ChatMessage) => {
    setEditingId(message.id);
    setValue(message.content);
    setExpanded(false);

    requestAnimationFrame(() => {
      textareaRef.current?.focus();
      textareaRef.current?.setSelectionRange(
        message.content.length,
        message.content.length,
      );
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
      <div className="absolute inset-x-0 top-0 bottom-32">
        <MessageScrollerProvider>
          <MessageScroller>
            <MessageScrollerViewport className="px-4">
              <MessageScrollerContent className="mx-auto w-full max-w-3xl gap-6 pb-8 pt-6">
                <MessageGroup className="gap-6">
                  {messages.map((message) => {
                    const urlOnly = isUrlOnly(message.content);

                    const showVerification = !!message.verification && !urlOnly;
                    const showUrlHealth =
                      !!message.urlHealth &&
                      message.urlHealth.results.length > 0;

                    const hasAiResponse =
                      !!message.error || showVerification || showUrlHealth;

                    return (
                      <MessageScrollerItem key={message.id} scrollAnchor>
                        <div className="flex flex-col gap-4">
                          {/* User message: right */}
                          <Message align="end">
                            <MessageContent className="items-end gap-1.5">
                              <Bubble
                                align="end"
                                variant="secondary"
                                className="max-w-[75%]"
                              >
                                <BubbleContent className="rounded-2xl border border-zinc-800 bg-zinc-800 px-4 py-2.5 text-sm leading-6 text-zinc-100">
                                  {message.content}
                                </BubbleContent>
                              </Bubble>

                              <MessageFooter className="px-0">
                                <div className="flex items-center gap-1 pr-1">
                                  <button
                                    type="button"
                                    aria-label={
                                      copiedId === message.id
                                        ? "Copied"
                                        : "Copy message"
                                    }
                                    onClick={() => void handleCopy(message)}
                                    className="flex size-7 items-center justify-center rounded-md text-zinc-500 transition-colors hover:bg-zinc-900 hover:text-zinc-200"
                                  >
                                    {copiedId === message.id ? (
                                      <Check className="size-3.5" />
                                    ) : (
                                      <Copy className="size-3.5" />
                                    )}
                                  </button>

                                  <button
                                    type="button"
                                    aria-label="Edit message"
                                    onClick={() => handleEdit(message)}
                                    className="flex size-7 items-center justify-center rounded-md text-zinc-500 transition-colors hover:bg-zinc-900 hover:text-zinc-200"
                                  >
                                    <Pencil className="size-3.5" />
                                  </button>
                                </div>
                              </MessageFooter>
                            </MessageContent>
                          </Message>

                          {/* AI response: left */}
                          {hasAiResponse && (
                            <Message align="start">
                              <MessageContent className="w-full items-start gap-3">
                                {message.error && (
                                  <div className="w-full max-w-[75%] rounded-xl border border-red-900/60 bg-red-950/30 px-3 py-2 text-xs text-red-300">
                                    {message.error}
                                  </div>
                                )}

                                {showVerification && message.verification && (
                                  <VerificationResult
                                    result={message.verification}
                                  />
                                )}

                                {showUrlHealth && message.urlHealth && (
                                  <UrlHealthResult result={message.urlHealth} />
                                )}
                              </MessageContent>
                            </Message>
                          )}
                        </div>
                      </MessageScrollerItem>
                    );
                  })}

                  {isSending && (
                    <MessageScrollerItem scrollAnchor>
                      <Message align="start">
                        <MessageContent className="max-w-[75%]">
                          <div className="flex items-center gap-2 rounded-2xl border border-zinc-800 bg-zinc-900 px-4 py-3">
                            <Spinner className="size-4 text-zinc-400" />
                            <Skeleton className="h-2.5 w-20 bg-zinc-800" />
                            <Skeleton className="h-2.5 w-10 bg-zinc-800" />
                          </div>
                        </MessageContent>
                      </Message>
                    </MessageScrollerItem>
                  )}
                </MessageGroup>
              </MessageScrollerContent>

              <MessageScrollerButton
                direction="end"
                className="
                  bottom-4
                  size-9
                  rounded-full
                  border
                  border-zinc-700
                  bg-zinc-900
                  text-zinc-300
                  shadow-lg
                  hover:bg-zinc-800
                  hover:text-white
                "
              />
            </MessageScrollerViewport>
          </MessageScroller>
        </MessageScrollerProvider>
      </div>

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
            placeholder={editingId !== null ? "Edit message" : placeholder}
            rows={1}
            className="
              block
              w-full
              resize-none
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
                z-10
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
            disabled={isSending}
            onClick={() => void handleSend()}
            className="
              absolute
              right-3
              bottom-3
              z-10
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
              disabled:cursor-not-allowed
              disabled:opacity-50
            "
          >
            {isSending ? (
              <Spinner className="size-4" />
            ) : (
              <ArrowUp className="size-4" strokeWidth={2.5} />
            )}
          </button>
        </div>
      </div>
    </div>
  );
};

export default ChatInterface;
