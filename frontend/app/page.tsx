import { redirect } from "next/navigation";

export default function Home() {
  return (
    // <div className="flex flex-col flex-1 items-center justify-center">
    //   Welcome To Halora Bitches!!!!
    // </div>

    redirect("/chat")
  );
}
