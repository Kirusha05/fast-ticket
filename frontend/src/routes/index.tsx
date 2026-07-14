import { createFileRoute } from "@tanstack/react-router";

export const Route = createFileRoute("/")({
  component: HomePage,
});

function HomePage() {
  return (
    <div className="space-y-6 container mx-auto">
      <h1>Home Page</h1>
    </div>
  );
}
