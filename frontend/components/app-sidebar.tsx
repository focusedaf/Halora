import {
  Sidebar,
  SidebarContent,
  SidebarFooter,
  SidebarGroup,
  SidebarHeader,
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
import { Kbd } from "./ui/kbd";
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar";
import {User} from "./user-profile"
import { Button } from "./ui/button";
import { IconCloud } from "@tabler/icons-react";
import { SearchIcon } from "lucide-react";


export function AppSidebar() {


  return (
    <Sidebar>
      <SidebarHeader className="items-left">
        <Empty>
          <EmptyHeader>
            <EmptyMedia variant="icon">
              <IconCloud />
            </EmptyMedia>
            <EmptyTitle>No data</EmptyTitle>
            <EmptyDescription>No data found</EmptyDescription>
          </EmptyHeader>
          <EmptyContent>
            <Button>Add data</Button>
            <InputGroup>
              <InputGroupInput placeholder="Try searching for chats..." />
              <InputGroupAddon>
                <SearchIcon />
              </InputGroupAddon>
              <InputGroupAddon align="inline-end">
                <Kbd>/</Kbd>
              </InputGroupAddon>
            </InputGroup>
          </EmptyContent>
        </Empty>
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
