import { createFileRoute, redirect } from "@tanstack/react-router";

export const Route = createFileRoute("/")({
  component: HomePage,
  // No homepage for now
  beforeLoad: () => {
    throw redirect({
      to: "/events",
    });
  },
});

function HomePage() {
  return (
    <div className="space-y-6 container mx-auto">
      <h1>Home Page</h1>
    </div>
  );
}
