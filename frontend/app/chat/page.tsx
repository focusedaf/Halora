import { SidebarProvider } from "@/components/ui/sidebar";
import { AppSidebar } from "@/components/app-sidebar";
import ChatInterface from "@/components/custom/ChatInterface";

export default function ChatPage() {
  return (
    <SidebarProvider>
      <AppSidebar />

      <main className="flex min-h-screen min-w-0 flex-1 flex-col">
        <ChatInterface />
      </main>
    </SidebarProvider>
  );
}
