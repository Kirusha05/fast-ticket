import { ValidateTicketsPage } from '@/features/tickets/components'
import { createFileRoute, redirect } from '@tanstack/react-router'

export const Route = createFileRoute('/validate')({
  component: ValidateTicketsPage,
  beforeLoad: ({ context }) => {
    if (!context.auth.isAuthenticated || !context.auth.isAdmin) {
      throw redirect({
        to: '/events'
      })
    }
  },
})