"use client";

import * as React from "react";

import Link from "next/link";

import {
  Sidebar,
  SidebarContent,
  SidebarFooter,
  SidebarGroup,
  SidebarHeader,
  SidebarMenu,
  SidebarMenuItem,
  SidebarMenuButton,
  SidebarTrigger,
  useSidebar,
} from "@/components/ui/sidebar";

import {
  Command,
  CommandDialog,
  CommandEmpty,
  CommandGroup,
  CommandInput,
  CommandItem,
  CommandList,
} from "@/components/ui/command";

import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";

import { User } from "./user-profile";

import {
  BookOpen,
  ChevronDown,
  ListFilter,
  MessageCircle,
  MoreHorizontal,
  NotebookPenIcon,
  Pin,
  PinOff,
  SearchIcon,
  SquarePen,
  XIcon,
} from "lucide-react";

import { cn } from "cn";

type Chat = {
  id: string;
  title: string;
};

const chats: Chat[] = [
  {
    id: "hallucination-detection",
    title: "Hallucination Detection",
  },
  {
    id: "rag-verification",
    title: "RAG Verification Study",
  },
  {
    id: "literature-review",
    title: "Literature Review",
  },
  {
    id: "multilingual-hallucination",
    title: "Multilingual Hallucination",
  },
];

export function AppSidebar() {
  const [open, setOpen] = React.useState(false);
  const [recentsOpen, setRecentsOpen] = React.useState(true);
  const [pinnedChats, setPinnedChats] = React.useState<string[]>([]);
  const [sidebarWidth, setSidebarWidth] = React.useState(260);

  const { state } = useSidebar();
  const resizing = React.useRef(false);

  /* Ctrl/Cmd + K */
  React.useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key.toLowerCase() === "k" && (e.ctrlKey || e.metaKey)) {
        e.preventDefault();
        setOpen((current) => !current);
      }
    };

    document.addEventListener("keydown", handleKeyDown);

    return () => {
      document.removeEventListener("keydown", handleKeyDown);
    };
  }, []);

  /* Sidebar resizing */
  React.useEffect(() => {
    const handlePointerMove = (e: PointerEvent) => {
      if (!resizing.current) return;

      const width = Math.min(Math.max(e.clientX, 220), 420);

      setSidebarWidth(width);
    };

    const handlePointerUp = () => {
      resizing.current = false;
      document.body.style.cursor = "";
      document.body.style.userSelect = "";
    };

    window.addEventListener("pointermove", handlePointerMove);
    window.addEventListener("pointerup", handlePointerUp);

    return () => {
      window.removeEventListener("pointermove", handlePointerMove);
      window.removeEventListener("pointerup", handlePointerUp);
    };
  }, []);

  const startResize = (e: React.PointerEvent<HTMLDivElement>) => {
    if (state === "collapsed") return;

    e.preventDefault();

    resizing.current = true;
    document.body.style.cursor = "col-resize";
    document.body.style.userSelect = "none";
  };

  const togglePin = (chatId: string) => {
    setPinnedChats((current) =>
      current.includes(chatId)
        ? current.filter((id) => id !== chatId)
        : [...current, chatId],
    );
  };

  const pinned = chats.filter((chat) => pinnedChats.includes(chat.id));
  const recent = chats.filter((chat) => !pinnedChats.includes(chat.id));

  const renderChat = (chat: Chat) => {
    const isPinned = pinnedChats.includes(chat.id);

    return (
      <SidebarMenuItem key={chat.id}>
        <div className="group/chat relative flex w-full items-center">
          <SidebarMenuButton
            className="
            h-9
            min-w-0
            flex-1
            rounded-lg
            px-2
            pr-16
            text-sm
            text-gray-300
            hover:bg-white/10
            hover:text-white
          "
          >
            <MessageCircle className="size-4 shrink-0" />
            <span className="truncate">{chat.title}</span>
          </SidebarMenuButton>

          <div
            className="
            absolute
            right-1
            top-1/2
            flex
            -translate-y-1/2
            items-center
            gap-1
          "
          >
           
            <DropdownMenu>
              <DropdownMenuTrigger
                render={
                  <button
                    type="button"
                    aria-label={`Options for ${chat.title}`}
                    className="
                    flex
                    size-7
                    items-center
                    justify-center
                    rounded-md
                    border-0
                    bg-transparent
                    p-0
                    text-gray-400
                    opacity-0
                    outline-none
                    transition-opacity
                    group-hover/chat:opacity-100
                    focus-visible:opacity-100
                    hover:text-white
                  "
                  >
                    <MoreHorizontal className="size-4" />
                  </button>
                }
              />

              <DropdownMenuContent
                side="right"
                align="start"
                sideOffset={6}
                className="w-44"
              >
                <DropdownMenuItem>Rename</DropdownMenuItem>

                <DropdownMenuSeparator />

                <DropdownMenuItem variant="destructive">
                  Delete
                </DropdownMenuItem>
              </DropdownMenuContent>
            </DropdownMenu>

            
            <button
              type="button"
              onClick={() => togglePin(chat.id)}
              aria-label={
                isPinned ? `Unpin ${chat.title}` : `Pin ${chat.title}`
              }
              className="
              flex
              size-7
              items-center
              justify-center
              rounded-md
              bg-transparent
              text-gray-400
              opacity-0
              outline-none
              transition-opacity
              group-hover/chat:opacity-100
              focus-visible:opacity-100
              hover:text-white
            "
            >
              {isPinned ? (
                <PinOff className="size-3.5" />
              ) : (
                <Pin className="size-3.5" />
              )}
            </button>
          </div>
        </div>
      </SidebarMenuItem>
    );
  };

  return (
    <>
      <Sidebar
        style={
          {
            "--sidebar-width": `${sidebarWidth}px`,
          } as React.CSSProperties
        }
      >
        <SidebarHeader className="shrink-0 px-2 pt-3 pb-2">
          <SidebarMenu>
            <SidebarMenuItem>
              <div className="flex w-full items-start">
                {/* Halora */}
                <SidebarMenuButton
                  size="lg"
                  render={<Link href="/chat" />}
                  className="
                    relative
                    h-auto
                    min-h-[64px]
                    min-w-0
                    flex-1
                    rounded-lg
                    px-2
                    hover:bg-transparent
                    hover:text-inherit
                    active:bg-transparent
                    active:text-inherit
                  "
                >
                  <div className="min-w-0 flex-1 text-left leading-tight">
                    <span
                      className="
                        block
                        text-[24px]
                        font-bold
                        tracking-tight
                        text-slate-100
                      "
                    >
                      Halora
                    </span>

                    <span
                      className="
                        mt-1.5
                        block
                        whitespace-normal
                        text-[11px]
                        font-medium
                        leading-4
                        tracking-[0.03em]
                        text-gray-400/70
                      "
                    >
                      Hallucination Detection Framework
                    </span>
                  </div>
                </SidebarMenuButton>

               
                <button
                  type="button"
                  onClick={() => setOpen(true)}
                  aria-label="Search chats"
                  className="
                    mt-1
                    flex
                    size-9
                    shrink-0
                    items-center
                    justify-center
                    rounded-md
                    bg-transparent
                    text-gray-400
                    transition-colors
                    hover:bg-white/5
                    hover:text-white
                  "
                >
                  <SearchIcon className="size-4" />
                </button>

               
                {state === "expanded" && (
                  <SidebarTrigger
                    className="
                      mt-1
                      size-9
                      shrink-0
                      text-gray-400
                      hover:bg-white/5
                      hover:text-white
                    "
                  />
                )}
              </div>

              <CommandDialog
                open={open}
                onOpenChange={setOpen}
                className="w-[700px]! max-w-[90vw]! p-4"
              >
                <Command>
                  <div className="flex items-center gap-2 p-1">
                    <div className="flex-1">
                      <CommandInput placeholder="Search..." />
                    </div>

                    <button
                      type="button"
                      onClick={() => setOpen(false)}
                      aria-label="Close search"
                      className="
                        flex
                        size-8
                        shrink-0
                        items-center
                        justify-center
                        rounded-md
                        text-gray-400
                        hover:bg-white/5
                        hover:text-white
                      "
                    >
                      <XIcon className="size-4" />
                    </button>
                  </div>

                  <CommandList>
                    <CommandEmpty>No chats found.</CommandEmpty>

                    <CommandGroup heading="Recent Chats">
                      {chats.map((chat) => (
                        <CommandItem key={chat.id}>
                          <MessageCircle />
                          <span>{chat.title}</span>
                        </CommandItem>
                      ))}
                    </CommandGroup>
                  </CommandList>
                </Command>
              </CommandDialog>
            </SidebarMenuItem>
          </SidebarMenu>
        </SidebarHeader>

        <SidebarContent className="min-h-0 overflow-hidden px-2">
          <SidebarGroup className="flex min-h-0 flex-1 flex-col pt-1">
           
            <SidebarMenu className="shrink-0 gap-0.5">
              <SidebarMenuItem>
                <SidebarMenuButton
                  className="
                    h-9
                    px-2
                    text-sm
                    font-medium
                    text-gray-200
                    hover:bg-transparent
                    hover:text-white
                  "
                >
                  <NotebookPenIcon className="size-[17px]" />
                  <span>New Chat</span>
                </SidebarMenuButton>
              </SidebarMenuItem>

              <SidebarMenuItem>
                <SidebarMenuButton
                  className="
                    h-9
                    px-2
                    text-sm
                    font-medium
                    text-gray-200
                    hover:bg-transparent
                    hover:text-white
                  "
                >
                  <BookOpen className="size-[17px]" />
                  <span>Library</span>
                </SidebarMenuButton>
              </SidebarMenuItem>
            </SidebarMenu>

           
            <div
              className="
                mt-4
                min-h-0
                flex-1
                overflow-y-auto
                overscroll-contain
                pr-1
                scrollbar-thin
                scrollbar-track-transparent
                scrollbar-thumb-white/10
                hover:scrollbar-thumb-white/20
              "
            >
            
              <div className="flex items-center justify-between px-2">
                <button
                  type="button"
                  onClick={() => setRecentsOpen((current) => !current)}
                  className="
                    flex
                    items-center
                    gap-1
                    bg-transparent
                    text-sm
                    font-medium
                    text-gray-300
                    outline-none
                    hover:text-white
                  "
                >
                  <span>Recents</span>

                  <ChevronDown
                    className={cn(
                      "size-3.5 transition-transform duration-200",
                      recentsOpen && "rotate-180",
                    )}
                  />
                </button>

                <div className="flex items-center gap-0.5">
                 
                  <button
                    type="button"
                    aria-label="Recent chat options"
                    className="
                      flex
                      size-7
                      items-center
                      justify-center
                      rounded-md
                      text-gray-400
                      hover:bg-transparent
                      hover:text-white
                    "
                  >
                    <MoreHorizontal className="size-4" />
                  </button>

              
                  <button
                    type="button"
                    aria-label="Filter recent chats"
                    className="
                      flex
                      size-7
                      items-center
                      justify-center
                      rounded-md
                      text-gray-400
                      hover:bg-transparent
                      hover:text-white
                    "
                  >
                    <ListFilter className="size-4" />
                  </button>

               
                  <button
                    type="button"
                    aria-label="New chat"
                    className="
                      flex
                      size-7
                      items-center
                      justify-center
                      rounded-md
                      text-gray-400
                      hover:bg-transparent
                      hover:text-white
                    "
                  >
                    <SquarePen className="size-4" />
                  </button>
                </div>
              </div>

              {recentsOpen && (
                <div className="mt-2">
                  {pinned.length > 0 && (
                    <>
                      <div className="px-2 pb-2 text-[13px] font-medium text-gray-500">
                        Pinned
                      </div>

                      <SidebarMenu className="gap-0.5">
                        {pinned.map(renderChat)}
                      </SidebarMenu>

                      <div className="my-3 h-px bg-white/5" />
                    </>
                  )}

                  <SidebarMenu className="gap-0.5">
                    {recent.map(renderChat)}
                  </SidebarMenu>
                </div>
              )}
            </div>
          </SidebarGroup>
        </SidebarContent>

        <SidebarFooter className="shrink-0 p-2">
          <User
            user={{
              name: "Morpheus",
              email: "morpheus@gmail.com",
              avatar: "https://github.com/shadcn.png",
            }}
          />
        </SidebarFooter>

       
        {state === "expanded" && (
          <div
            onPointerDown={startResize}
            className="
              absolute
              right-0
              top-0
              z-50
              h-full
              w-1
              cursor-col-resize
              touch-none
              hover:bg-white/10
              active:bg-white/20
            "
          />
        )}
      </Sidebar>

      
      {state === "collapsed" && (
        <SidebarTrigger
          className="
            fixed
            top-4
            z-50
            size-9
            rounded-md
            border
            bg-background
            text-gray-400
            shadow-sm
            hover:bg-white/5
            hover:text-white
          "
        />
      )}
    </>
  );
}
