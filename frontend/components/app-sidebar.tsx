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
} from "@/components/ui/sidebar";
import {
  Empty,
  EmptyContent,
  EmptyDescription,
  EmptyHeader,
  EmptyMedia,
  EmptyTitle,
} from "@/components/ui/empty";
import {
  InputGroup,
  InputGroupAddon,
  InputGroupInput,
} from "@/components/ui/input-group";
import {
  Command,
  CommandDialog,
  CommandEmpty,
  CommandGroup,
  CommandInput,
  CommandItem,
  CommandList,
  CommandSeparator,
  CommandShortcut,
} from "@/components/ui/command";
import { Kbd } from "./ui/kbd";
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar";
import { User } from "./user-profile";
import { Button } from "./ui/button";
import { IconCloud } from "@tabler/icons-react";
import {
  SearchIcon,
  BellIcon,
  CalculatorIcon,
  CalendarIcon,
  ClipboardPasteIcon,
  CodeIcon,
  CopyIcon,
  CreditCardIcon,
  FileTextIcon,
  FolderIcon,
  FolderPlusIcon,
  HelpCircleIcon,
  HomeIcon,
  ImageIcon,
  InboxIcon,
  LayoutGridIcon,
  ListIcon,
  PlusIcon,
  ScissorsIcon,
  SettingsIcon,
  TrashIcon,
  UserIcon,
  ZoomInIcon,
  ZoomOutIcon,
  XIcon,
  MessageCircle,
  NotebookPenIcon,
} from "lucide-react";
import { IconOrbit } from "@tabler/icons-react";

export function AppSidebar() {
  const [open, setOpen] = React.useState(false);

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
    <Sidebar>
      <SidebarHeader className="pt-3">
        <SidebarMenu>
          <SidebarMenuItem>
            <SidebarMenuButton
              size="lg"
              render={<Link href="/chat" />}
              className="
                relative
                h-[58px]
                rounded-lg
                hover:bg-transparent
                hover:text-inherit
                active:bg-transparent
                active:text-inherit
              "
            >
              <div
                className="
                  relative
                  flex
                  size-9
                  shrink-0
                  items-center
                  justify-center
                  overflow-hidden
                  rounded-xl
                  bg-gradient-to-br
                  from-amber-300
                  via-yellow-400
                  to-orange-500
                  text-lg
                  shadow-[0_0_24px_rgba(251,191,36,0.25)]
                  ring-1
                  ring-amber-300/40
                "
              >
                <span className="relative z-10">
                  <IconOrbit />
                </span>

                <div
                  className="
                    absolute
                    inset-0
                    bg-gradient-to-br
                    from-white/30
                    via-transparent
                    to-transparent
                  "
                />
              </div>

              <div className="grid min-w-0 flex-1 text-left leading-tight">
                <span
                  className="
                    text-[15px]
                    font-semibold
                    tracking-tight
                    text-slate-100
                  "
                >
                  Halora
                </span>

                <span
                  className="
                    mt-0.5
                    truncate
                    text-[10px]
                    font-medium
                    tracking-[0.04em]
                    text-gray-400/70
                  "
                >
                  Hallucination Detection Framework
                </span>
              </div>

              <div className="flex flex-col gap-4 ">
                <Button
                  onClick={() => setOpen(true)}
                  variant="ghost"
                  size="icon"
                  className="w-fit bg-transparent"
                >
                  <SearchIcon />
                </Button>

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
                      <CommandEmpty>No results found.</CommandEmpty>
                      <CommandGroup heading="Recent Chats">
                        <CommandItem>
                          <MessageCircle />
                          <span>Home</span>
                        </CommandItem>
                        <CommandItem>
                          <MessageCircle />
                          <span>Inbox</span>
                        </CommandItem>
                        <CommandItem>
                          <MessageCircle />
                          <span>Documents</span>
                        </CommandItem>
                        <CommandItem>
                          <MessageCircle />
                          <span>Folders</span>
                        </CommandItem>
                      </CommandGroup>
                    </CommandList>
                  </Command>
                </CommandDialog>
              </div>
            </SidebarMenuButton>
          </SidebarMenuItem>
        </SidebarMenu>
      </SidebarHeader>

      <SidebarContent>
        <SidebarGroup className="pt-1">
          <SidebarMenu>
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
                <NotebookPenIcon className="size-4" />
                <span>New Chat</span>
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
  );
}
