// HITL Approval Dashboard — the core safety feature.
// TODO: fetch via api.getApproval(params.id), render ApprovalDashboard with
// edit/reject/merge actions and PayloadPreview before api.executeApproval().
export default function ApprovalPage({ params }: { params: { id: string } }) {
  return <div className="p-8">TODO: approval dashboard for {params.id}</div>;
}
