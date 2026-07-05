import { ArrowRight, CalendarClock, FileWarning, ReceiptText, ShieldAlert } from 'lucide-react'
import { Link } from 'react-router-dom'
import { Badge } from '@/components/ui/badge'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { type TaxSummary, formatNaira } from '@/lib/api'

export default function TaxSummaryCard({ summary }: { summary: TaxSummary }) {
  const nextDeadline = [...summary.deadlines].sort((left, right) => left.daysRemaining - right.daysRemaining)[0] ?? null
  const statusLabel = {
    ready: 'On track',
    needs_setup: 'Setup needed',
    needs_activity: 'Waiting for activity',
    attention: 'Needs attention',
  }[summary.status]

  return (
    <Card className="overflow-hidden border-amber-200 bg-[radial-gradient(circle_at_top_right,_rgba(251,191,36,0.18),_transparent_42%),linear-gradient(180deg,#fff7ed_0%,#ffffff_100%)] shadow-sm">
      <CardHeader className="pb-3">
        <div className="flex items-start justify-between gap-3">
          <div>
            <CardTitle className="flex items-center gap-2 text-base text-neutral-950">
              <ShieldAlert className="h-4 w-4 text-amber-600" />
              Tax Snapshot
            </CardTitle>
            <CardDescription className="mt-1 text-neutral-600">Quick preview of setup, deadlines, and estimated exposure.</CardDescription>
          </div>
          <Badge variant="outline" className="border-amber-300 bg-white/80 text-amber-700">
            {statusLabel}
          </Badge>
        </div>
      </CardHeader>
      <CardContent className="space-y-4">
        <div className="grid grid-cols-2 gap-3">
          <div className="rounded-xl border border-white/70 bg-white/80 p-3">
            <p className="text-[11px] uppercase tracking-[0.16em] text-neutral-500">Estimated total</p>
            <p className="mt-2 text-lg font-bold text-neutral-950">
              {summary.estimate ? formatNaira(summary.estimate.result.totalEstimatedTax) : 'No estimate'}
            </p>
          </div>
          <div className="rounded-xl border border-white/70 bg-white/80 p-3">
            <p className="text-[11px] uppercase tracking-[0.16em] text-neutral-500">TIN status</p>
            <p className="mt-2 text-sm font-semibold text-neutral-900">
              {summary.profile.tin ? summary.profile.tin : 'Not added'}
            </p>
          </div>
        </div>

        <div className="rounded-xl border border-amber-100 bg-white/90 p-3">
          <div className="flex items-center gap-2 text-xs font-semibold uppercase tracking-[0.16em] text-neutral-500">
            <CalendarClock className="h-3.5 w-3.5 text-amber-600" />
            Next deadline
          </div>
          {nextDeadline ? (
            <div className="mt-3 space-y-1">
              <div className="flex items-center justify-between gap-3">
                <p className="text-sm font-semibold text-neutral-950">{nextDeadline.label}</p>
                <StatusPill status={nextDeadline.status} />
              </div>
              <p className="text-sm text-neutral-700">{new Date(nextDeadline.dueDate).toLocaleDateString()}</p>
              <p className="text-xs text-neutral-500">{deadlineCopy(nextDeadline.daysRemaining)}</p>
            </div>
          ) : (
            <p className="mt-3 text-sm text-neutral-600">Add tax setup details to unlock deadline tracking.</p>
          )}
        </div>

        <div className="space-y-2">
          {summary.alerts.slice(0, 2).map((alert) => (
            <div key={`${alert.level}-${alert.title}`} className="rounded-xl border border-white/70 bg-white/80 p-3">
              <div className="flex items-start gap-2">
                <FileWarning className={`mt-0.5 h-4 w-4 ${alert.level === 'critical' ? 'text-red-600' : alert.level === 'warning' ? 'text-amber-600' : 'text-sky-600'}`} />
                <div>
                  <p className="text-sm font-semibold text-neutral-950">{alert.title}</p>
                  <p className="mt-1 text-xs leading-5 text-neutral-600">{alert.message}</p>
                </div>
              </div>
            </div>
          ))}
          {summary.alerts.length === 0 && summary.estimate && (
            <div className="rounded-xl border border-white/70 bg-white/80 p-3">
              <div className="flex items-center gap-2 text-sm font-semibold text-neutral-900">
                <ReceiptText className="h-4 w-4 text-emerald-600" />
                Tax preview is active for this business.
              </div>
            </div>
          )}
        </div>

        <Link to="/taxes" className="inline-flex items-center gap-2 text-sm font-semibold text-amber-700 transition-colors hover:text-amber-800">
          Open tax workspace
          <ArrowRight className="h-4 w-4" />
        </Link>
      </CardContent>
    </Card>
  )
}

function StatusPill({ status }: { status: TaxSummary['deadlines'][number]['status'] }) {
  const classes = {
    overdue: 'border-red-200 bg-red-50 text-red-700',
    urgent: 'border-amber-200 bg-amber-50 text-amber-700',
    upcoming: 'border-sky-200 bg-sky-50 text-sky-700',
    normal: 'border-emerald-200 bg-emerald-50 text-emerald-700',
  }[status]

  return <span className={`rounded-full border px-2 py-1 text-[10px] font-semibold uppercase tracking-[0.16em] ${classes}`}>{status}</span>
}

function deadlineCopy(daysRemaining: number) {
  if (daysRemaining < 0) return `${Math.abs(daysRemaining)} day${Math.abs(daysRemaining) === 1 ? '' : 's'} overdue`
  if (daysRemaining === 0) return 'Due today'
  return `${daysRemaining} day${daysRemaining === 1 ? '' : 's'} remaining`
}
