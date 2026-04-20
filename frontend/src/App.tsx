import { Toaster } from "@/components/ui/toaster";
import { Toaster as Sonner } from "@/components/ui/sonner";
import { TooltipProvider } from "@/components/ui/tooltip";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import Index from "./pages/Index";
import NotFound from "./pages/NotFound";
import Connect from "./pages/Connect";
import Notes from "./pages/Notes";
import Phone from "./pages/Phone";
import Contacts from "./pages/Contacts";
import Pricing from "./pages/Pricing";

const queryClient = new QueryClient();

const App = () => (
  <QueryClientProvider client={queryClient}>
    {/* One block-sized child so % heights work under #root (Electron + frameless). */}
    <div className="flex h-full w-full flex-col bg-[#080808]">
      <TooltipProvider>
        <Toaster />
        <Sonner />
        <BrowserRouter>
          <div className="flex min-h-0 flex-1 flex-col">
            <Routes>
              <Route path="/" element={<Index />} />
              <Route path="/connect" element={<Connect />} />
              <Route path="/notes" element={<Notes />} />
              <Route path="/phone" element={<Phone />} />
              <Route path="/contacts" element={<Contacts />} />
              <Route path="/pricing" element={<Pricing />} />
              <Route path="*" element={<NotFound />} />
            </Routes>
          </div>
        </BrowserRouter>
      </TooltipProvider>
    </div>
  </QueryClientProvider>
);

export default App;
