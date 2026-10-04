"use client"
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

              <span className="mb-5">
                <div className="flex flex-col gap-4">
                  <Button
                    onClick={() => setOpen(true)}
                    variant="ghost"
                    size="icon"
                    className="w-fit bg-transparent"
                  >
                    <SearchIcon />
                  </Button>
                  <CommandDialog open={open} onOpenChange={setOpen}>
                    <Command>
                      <CommandInput placeholder="Type a command or search..." />
                      <CommandList>
                        <CommandEmpty>No results found.</CommandEmpty>
                        <CommandGroup heading="Navigation">
                          <CommandItem>
                            <HomeIcon />
                            <span>Home</span>
                            <CommandShortcut>⌘H</CommandShortcut>
                          </CommandItem>
                          <CommandItem>
                            <InboxIcon />
                            <span>Inbox</span>
                            <CommandShortcut>⌘I</CommandShortcut>
                          </CommandItem>
                          <CommandItem>
                            <FileTextIcon />
                            <span>Documents</span>
                            <CommandShortcut>⌘D</CommandShortcut>
                          </CommandItem>
                          <CommandItem>
                            <FolderIcon />
                            <span>Folders</span>
                            <CommandShortcut>⌘F</CommandShortcut>
                          </CommandItem>
                        </CommandGroup>
                        <CommandSeparator />
                        <CommandGroup heading="Actions">
                          <CommandItem>
                            <PlusIcon />
                            <span>New File</span>
                            <CommandShortcut>⌘N</CommandShortcut>
                          </CommandItem>
                          <CommandItem>
                            <FolderPlusIcon />
                            <span>New Folder</span>
                            <CommandShortcut>⇧⌘N</CommandShortcut>
                          </CommandItem>
                          <CommandItem>
                            <CopyIcon />
                            <span>Copy</span>
                            <CommandShortcut>⌘C</CommandShortcut>
                          </CommandItem>
                          <CommandItem>
                            <ScissorsIcon />
                            <span>Cut</span>
                            <CommandShortcut>⌘X</CommandShortcut>
                          </CommandItem>
                          <CommandItem>
                            <ClipboardPasteIcon />
                            <span>Paste</span>
                            <CommandShortcut>⌘V</CommandShortcut>
                          </CommandItem>
                          <CommandItem>
                            <TrashIcon />
                            <span>Delete</span>
                            <CommandShortcut>⌫</CommandShortcut>
                          </CommandItem>
                        </CommandGroup>
                        <CommandSeparator />
                        <CommandGroup heading="View">
                          <CommandItem>
                            <LayoutGridIcon />
                            <span>Grid View</span>
                          </CommandItem>
                          <CommandItem>
                            <ListIcon />
                            <span>List View</span>
                          </CommandItem>
                          <CommandItem>
                            <ZoomInIcon />
                            <span>Zoom In</span>
                            <CommandShortcut>⌘+</CommandShortcut>
                          </CommandItem>
                          <CommandItem>
                            <ZoomOutIcon />
                            <span>Zoom Out</span>
                            <CommandShortcut>⌘-</CommandShortcut>
                          </CommandItem>
                        </CommandGroup>
                        <CommandSeparator />
                        <CommandGroup heading="Account">
                          <CommandItem>
                            <UserIcon />
                            <span>Profile</span>
                            <CommandShortcut>⌘P</CommandShortcut>
                          </CommandItem>
                          <CommandItem>
                            <CreditCardIcon />
                            <span>Billing</span>
                            <CommandShortcut>⌘B</CommandShortcut>
                          </CommandItem>
                          <CommandItem>
                            <SettingsIcon />
                            <span>Settings</span>
                            <CommandShortcut>⌘S</CommandShortcut>
                          </CommandItem>
                          <CommandItem>
                            <BellIcon />
                            <span>Notifications</span>
                          </CommandItem>
                          <CommandItem>
                            <HelpCircleIcon />
                            <span>Help & Support</span>
                          </CommandItem>
                        </CommandGroup>
                        <CommandSeparator />
                        <CommandGroup heading="Tools">
                          <CommandItem>
                            <CalculatorIcon />
                            <span>Calculator</span>
                          </CommandItem>
                          <CommandItem>
                            <CalendarIcon />
                            <span>Calendar</span>
                          </CommandItem>
                          <CommandItem>
                            <ImageIcon />
                            <span>Image Editor</span>
                          </CommandItem>
                          <CommandItem>
                            <CodeIcon />
                            <span>Code Editor</span>
                          </CommandItem>
                        </CommandGroup>
                      </CommandList>
                    </Command>
                  </CommandDialog>
                </div>
              </span>
            </SidebarMenuButton>
          </SidebarMenuItem>
        </SidebarMenu>

       
      </SidebarHeader>

      <SidebarContent>
        <SidebarGroup />
        <SidebarGroup />
      </SidebarContent>

      <SidebarFooter>
        {/* <Avatar className="size-12">
          <AvatarImage
            src="https://github.com/shadcn.png"
            className="grayscale"
          />
          <AvatarFallback>LR</AvatarFallback>
        </Avatar> */}
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
