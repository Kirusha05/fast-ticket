import { Ticket } from "lucide-react";

export function Footer() {
  const columns = [
    {
      title: "Product",
      links: ["Browse events", "Sell tickets", "Pricing", "Mobile app"],
    },
    {
      title: "Company",
      links: ["About", "Careers", "Blog", "Press"],
    },
    {
      title: "Support",
      links: ["Help center", "Contact us", "Refund policy", "Status"],
    },
    {
      title: "Legal",
      links: ["Terms of service", "Privacy policy", "Cookie policy"],
    },
  ];

  return (
    <footer className="border-t text-zinc-400 px-6 mt-12">
      <div className="space-y-10 container mx-auto py-12">
        <div className="grid grid-cols-2 md:grid-cols-6 gap-8">
          {/* Brand */}
          <div className="col-span-2">
            <div className="flex items-center gap-2 text-white">
              <Ticket className="h-5 w-5 text-white" />
              <span className="font-bold text-xl">
                FastTicket
              </span>
            </div>
            <p className="mt-3 text-sm text-zinc-500 max-w-xs">
              Find, book, and manage tickets for shows, sports, and events near you.
            </p>
          </div>

          {/* Link columns */}
          {columns.map((col) => (
            <div key={col.title} className="col-span-1">
              <h4 className="text-sm font-medium text-white mb-3">
                {col.title}
              </h4>
              <ul className="space-y-2">
                {col.links.map((link) => (
                  <li key={link}>
                    <a
                      href="#"
                      className="text-sm text-zinc-500 hover:text-zinc-200 transition-colors"
                    >
                      {link}
                    </a>
                  </li>
                ))}
              </ul>
            </div>
          ))}
        </div>

        {/* Ticket-stub perforation divider */}
        {/* <div className="relative my-10 flex items-center">
          <div className="h-3 w-3 rounded-full bg-zinc-950 border border-zinc-800 -ml-1" />
          <div className="flex-1 border-t border-dashed border-zinc-800" />
          <div className="h-3 w-3 rounded-full bg-zinc-950 border border-zinc-800 -mr-1" />
        </div> */}

        {/* Bottom bar */}
        <div className="flex flex-col sm:flex-row items-center justify-between gap-3 text-xs text-zinc-600">
          <p>© {new Date().getFullYear()} FastTicket, Inc. All rights reserved.</p>
          <div className="flex items-center gap-4">
            <a href="#" className="hover:text-zinc-300 transition-colors">
              Terms
            </a>
            <a href="#" className="hover:text-zinc-300 transition-colors">
              Privacy
            </a>
            <a href="#" className="hover:text-zinc-300 transition-colors">
              Cookies
            </a>
          </div>
        </div>
      </div>
    </footer>
  );
}
