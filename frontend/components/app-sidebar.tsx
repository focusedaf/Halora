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
  SidebarGroupLabel,
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

import { Button } from "./ui/button";
import { User } from "./user-profile";
import { Separator } from "./ui/separator";

import {
  MessageCircle,
  NotebookPenIcon,
  SearchIcon,
  XIcon,
} from "lucide-react";

export function AppSidebar() {
  const [open, setOpen] = React.useState(false);
  const { state } = useSidebar();

  React.useEffect(() => {
    const down = (e: KeyboardEvent) => {
      if (e.key === "k" && (e.metaKey || e.ctrlKey)) {
        e.preventDefault();
        setOpen((open) => !open);
      }
    };

    document.addEventListener("keydown", down);

    return () => {
      document.removeEventListener("keydown", down);
    };
  }, []);

  return (
    <>
      <Sidebar>
        <SidebarHeader className="pt-4 pb-4">
          <SidebarMenu>
            <SidebarMenuItem>
              <div className="flex w-full items-center">
                <SidebarMenuButton
                  size="lg"
                  render={<Link href="/chat" />}
                  className="
                        relative
                        h-auto
                        min-h-[80px]
                        min-w-0
                        flex-1
                        rounded-lg
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
                          text-[25px]
                          font-bold
                          tracking-tight
                          text-slate-100
                        "
                    >
                      Halora
                    </span>

                    <span
                      className="
                          mt-2
                          block
                          whitespace-normal
                          text-[12px]
                          font-semibold
                          leading-4
                          tracking-[0.03em]
                          text-gray-400/70
                        "
                    >
                      Hallucination Detection Framework
                    </span>
                  </div>
                </SidebarMenuButton>

                <Button
                  onClick={() => setOpen(true)}
                  variant="ghost"
                  size="icon"
                  aria-label="Search chats"
                  className="
                      size-9
                      shrink-0
                      self-start
                      mt-2
                      bg-transparent
                      text-gray-400
                      hover:bg-white/5
                      hover:text-white
                    "
                >
                  <SearchIcon className="size-4" />
                </Button>

                {state === "expanded" && (
                  <SidebarTrigger
                    className="
                        size-9
                        shrink-0
                        self-start
                        mt-2
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

                    <Button
                      variant="ghost"
                      size="icon"
                      onClick={() => setOpen(false)}
                      className="shrink-0"
                    >
                      <XIcon className="size-4" />
                    </Button>
                  </div>

                  <CommandList>
                    <CommandEmpty>No chats found.</CommandEmpty>

                    <CommandGroup heading="Recent Chats">
                      <CommandItem>
                        <MessageCircle />
                        <span>Hallucination Detection</span>
                      </CommandItem>

                      <CommandItem>
                        <MessageCircle />
                        <span>RAG Verification Study</span>
                      </CommandItem>

                      <CommandItem>
                        <MessageCircle />
                        <span>Literature Review</span>
                      </CommandItem>

                      <CommandItem>
                        <MessageCircle />
                        <span>Multilingual Hallucination</span>
                      </CommandItem>
                    </CommandGroup>
                  </CommandList>
                </Command>
              </CommandDialog>
            </SidebarMenuItem>
          </SidebarMenu>
        </SidebarHeader>

        <Separator className="my-3" />

        <SidebarContent className="overflow-y-auto">
          <SidebarGroup className="pt-2">
            <SidebarMenu>
              <SidebarMenuItem>
                <SidebarMenuButton
                  className="
                    h-9
                    px-2
                    text-md
                    text-gray-300
                    hover:bg-white/5
                    hover:text-white
                  "
                >
                  <NotebookPenIcon className="size-4" />
                  <span>New Chat</span>
                </SidebarMenuButton>
              </SidebarMenuItem>

              <Separator className="my-3" />

              <SidebarGroupLabel className="px-2 text-md text-gray-500">
                Recent Chats
              </SidebarGroupLabel>

              <SidebarMenuItem>
                <SidebarMenuButton
                  className="
                    h-9
                    px-2
                    text-sm
                    text-gray-300
                    hover:bg-white/5
                    hover:text-white
                  "
                >
                  <MessageCircle className="size-4" />
                  <span className="truncate">Hallucination Detection</span>
                </SidebarMenuButton>
              </SidebarMenuItem>

              <SidebarMenuItem>
                <SidebarMenuButton
                  className="
                    h-9
                    px-2
                    text-sm
                    text-gray-300
                    hover:bg-white/5
                    hover:text-white
                  "
                >
                  <MessageCircle className="size-4" />
                  <span className="truncate">RAG Verification Study</span>
                </SidebarMenuButton>
              </SidebarMenuItem>

              <SidebarMenuItem>
                <SidebarMenuButton
                  className="
                    h-9
                    px-2
                    text-sm
                    text-gray-300
                    hover:bg-white/5
                    hover:text-white
                  "
                >
                  <MessageCircle className="size-4" />
                  <span className="truncate">Literature Review</span>
                </SidebarMenuButton>
              </SidebarMenuItem>

              <SidebarMenuItem>
                <SidebarMenuButton
                  className="
                    h-9
                    px-2
                    text-sm
                    text-gray-300
                    hover:bg-white/5
                    hover:text-white
                  "
                >
                  <MessageCircle className="size-4" />
                  <span className="truncate">Multilingual Hallucination</span>
                </SidebarMenuButton>
              </SidebarMenuItem>
            </SidebarMenu>
          </SidebarGroup>
        </SidebarContent>

        <SidebarFooter>
          <User
            user={{
              name: "Morpheus",
              email: "morpheus@gmail.com",
              avatar: "https://github.com/shadcn.png",
            }}
          />
        </SidebarFooter>
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
