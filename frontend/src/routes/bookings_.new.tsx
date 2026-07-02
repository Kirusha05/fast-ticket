import { createFileRoute } from '@tanstack/react-router'

export const Route = createFileRoute('/bookings_/new')({
  component: RouteComponent,
})

function RouteComponent() {
  return <div>Hello "/bookings_/new"!</div>
}
