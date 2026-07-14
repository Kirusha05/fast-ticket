import { LoaderIcon, Ticket } from "lucide-react";

export const LoadingScreen = () => {
  return (
    <div className="fixed inset-0 w-screen h-screen bg-neutral flex items-center justify-center z-50">
      <Ticket className="h-8 w-8 mr-4" />
      <p className="text-white text-4xl font-bold">FastTicket</p>
      <LoaderIcon className="ml-4 animate-spin" />
    </div>
  );
};