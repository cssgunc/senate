import {
  AdminPageHeader,
  AdminPageShell,
} from "@/components/admin/AdminPageShell";

export default function AdminPage() {
  return (
    <AdminPageShell>
      <AdminPageHeader
        title="Dashboard"
        description="Welcome to the Senate admin dashboard. Use the sidebar to manage content."
      />
    </AdminPageShell>
  );
}
