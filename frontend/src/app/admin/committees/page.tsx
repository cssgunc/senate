"use client";

import {
  AdminCard,
  AdminPageHeader,
  AdminPageShell,
} from "@/components/admin/AdminPageShell";
import { Button } from "@/components/ui/button";
import { Checkbox } from "@/components/ui/checkbox";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Textarea } from "@/components/ui/textarea";
import {
  assignCommitteeMember,
  createCommittee,
  deleteCommittee,
  getAdminCommittees,
  removeCommitteeMember,
  updateCommittee,
} from "@/lib/admin-api";
import { getSenators } from "@/lib/api";
import type { Committee, CommitteeAssignment, Senator } from "@/types";
import type { CreateCommittee } from "@/types/admin";
import { Fragment, useEffect, useState } from "react";

interface CommitteeFormState {
  name: string;
  description: string;
  chair_senator_id: string;
  chair_name: string;
  chair_email: string;
  is_active: boolean;
}

function emptyCommitteeForm(): CommitteeFormState {
  return {
    name: "",
    description: "",
    chair_senator_id: "",
    chair_name: "",
    chair_email: "",
    is_active: true,
  };
}

function toCommitteePayload(form: CommitteeFormState): CreateCommittee {
  return {
    name: form.name.trim(),
    description: form.description.trim(),
    chair_senator_id: form.chair_senator_id
      ? Number(form.chair_senator_id)
      : null,
    chair_name: form.chair_name.trim(),
    chair_email: form.chair_email.trim(),
    is_active: form.is_active,
  };
}

export default function CommitteesPage() {
  const [committees, setCommittees] = useState<Committee[]>([]);
  const [senators, setSenators] = useState<Senator[]>([]);
  const [expanded, setExpanded] = useState<number | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    async function load(): Promise<void> {
      setIsLoading(true);
      try {
        const [adminCommittees, allSenators] = await Promise.all([
          getAdminCommittees(),
          getSenators(),
        ]);
        setCommittees(adminCommittees);
        setSenators(allSenators);
      } catch (error) {
        console.error("Failed to load committees page data:", error);
        alert("Failed to load committees.");
      } finally {
        setIsLoading(false);
      }
    }

    void load();
  }, []);

  function updateLocal(updated: Committee): void {
    setCommittees((prev) =>
      prev.map((c) => (c.id === updated.id ? updated : c)),
    );
  }

  return (
    <AdminPageShell>
      <AdminPageHeader title="Committees Management" />

      <AdminCard>
        <CommitteeForm
          senators={senators}
          onCreate={async (data) => {
            const created = await createCommittee(data);
            setCommittees((prev) => [...prev, created]);
          }}
        />
      </AdminCard>

      <AdminCard className="overflow-x-auto p-0">
        {isLoading && (
          <p className="p-4 text-sm text-slate-500">Loading data...</p>
        )}

        <table className="w-full text-sm">
          <thead className="bg-slate-50">
            <tr>
              <th className="p-3 text-left text-xs font-semibold uppercase tracking-wide text-slate-500">
                Name
              </th>
              <th className="p-3 text-left text-xs font-semibold uppercase tracking-wide text-slate-500">
                Chair
              </th>
              <th className="p-3 text-left text-xs font-semibold uppercase tracking-wide text-slate-500">
                Active
              </th>
              <th className="p-3 text-left text-xs font-semibold uppercase tracking-wide text-slate-500">
                Member Count
              </th>
              <th className="p-3 text-left text-xs font-semibold uppercase tracking-wide text-slate-500">
                Actions
              </th>
            </tr>
          </thead>

          <tbody>
            {committees.map((committee) => (
              <Fragment key={committee.id}>
                <tr className="border-t border-slate-100 align-top">
                  <td className="p-3">{committee.name}</td>
                  <td className="p-3">{committee.chair_name}</td>
                  <td className="p-3">{committee.is_active ? "Yes" : "No"}</td>
                  <td className="p-3">{committee.members.length}</td>
                  <td className="p-3">
                    <div className="flex gap-2">
                      <Button
                        variant="outline"
                        onClick={() =>
                          setExpanded(
                            expanded === committee.id ? null : committee.id,
                          )
                        }
                      >
                        {expanded === committee.id ? "Hide" : "Manage"}
                      </Button>

                      <Button
                        variant="destructive"
                        onClick={async () => {
                          try {
                            await deleteCommittee(committee.id);
                            setCommittees((prev) =>
                              prev.filter((c) => c.id !== committee.id),
                            );
                          } catch (error) {
                            console.error("Failed to delete committee:", error);
                            alert("Failed to delete committee.");
                          }
                        }}
                      >
                        Delete
                      </Button>
                    </div>
                  </td>
                </tr>

                {expanded === committee.id && (
                  <tr className="border-t border-slate-100 bg-slate-50/50">
                    <td className="p-3" colSpan={5}>
                      <CommitteeDetail
                        committee={committee}
                        senators={senators}
                        onUpdate={updateLocal}
                      />
                    </td>
                  </tr>
                )}
              </Fragment>
            ))}
          </tbody>
        </table>
      </AdminCard>
    </AdminPageShell>
  );
}

function CommitteeForm({
  senators,
  onCreate,
}: {
  senators: Senator[];
  onCreate: (data: CreateCommittee) => Promise<void>;
}) {
  const [form, setForm] = useState<CommitteeFormState>(emptyCommitteeForm());
  const [isSubmitting, setIsSubmitting] = useState(false);

  function handleChairChange(id: string): void {
    if (!id) {
      setForm((prev) => ({
        ...prev,
        chair_senator_id: "",
        chair_name: "",
        chair_email: "",
      }));
      return;
    }

    const senator = senators.find((s) => s.id === Number(id));
    if (!senator) return;

    setForm((prev) => ({
      ...prev,
      chair_senator_id: id,
      chair_name: `${senator.first_name} ${senator.last_name}`,
      chair_email: senator.email,
    }));
  }

  return (
    <div className="space-y-4">
      <h2 className="font-semibold text-slate-900">Create Committee</h2>

      <div className="space-y-2">
        <Label htmlFor="committee-name">Name</Label>
        <Input
          id="committee-name"
          placeholder="Committee name"
          value={form.name}
          onChange={(e) =>
            setForm((prev) => ({ ...prev, name: e.target.value }))
          }
          disabled={isSubmitting}
        />
      </div>

      <div className="space-y-2">
        <Label htmlFor="committee-description">Description</Label>
        <Textarea
          id="committee-description"
          placeholder="Committee description"
          value={form.description}
          onChange={(e) =>
            setForm((prev) => ({ ...prev, description: e.target.value }))
          }
          disabled={isSubmitting}
        />
      </div>

      <div className="space-y-2">
        <Label htmlFor="committee-chair">Chair</Label>
        <Select
          value={form.chair_senator_id}
          onValueChange={handleChairChange}
          disabled={isSubmitting}
        >
          <SelectTrigger id="committee-chair">
            <SelectValue placeholder="Select a chair" />
          </SelectTrigger>
          <SelectContent>
            {senators.map((s) => (
              <SelectItem key={s.id} value={String(s.id)}>
                {s.first_name} {s.last_name}
              </SelectItem>
            ))}
          </SelectContent>
        </Select>
      </div>

      {form.chair_name && (
        <div className="space-y-2 rounded-md bg-slate-50 p-3">
          <div className="space-y-1">
            <p className="text-xs font-semibold uppercase text-slate-500">
              Chair Name
            </p>
            <p className="text-sm text-slate-900">{form.chair_name}</p>
          </div>
          <div className="space-y-1">
            <p className="text-xs font-semibold uppercase text-slate-500">
              Chair Email
            </p>
            <p className="text-sm text-slate-900">{form.chair_email}</p>
          </div>
        </div>
      )}

      <div className="flex items-center gap-2">
        <Checkbox
          id="committee-active"
          checked={form.is_active}
          onCheckedChange={(checked) =>
            setForm((prev) => ({ ...prev, is_active: Boolean(checked) }))
          }
          disabled={isSubmitting}
        />
        <Label htmlFor="committee-active">Active</Label>
      </div>

      <Button
        disabled={isSubmitting}
        onClick={async () => {
          setIsSubmitting(true);
          try {
            await onCreate(toCommitteePayload(form));
            setForm(emptyCommitteeForm());
          } catch (error) {
            console.error("Failed to create committee:", error);
            alert("Failed to create committee.");
          } finally {
            setIsSubmitting(false);
          }
        }}
      >
        {isSubmitting ? "Creating..." : "Create"}
      </Button>
    </div>
  );
}

function CommitteeDetail({
  committee,
  senators,
  onUpdate,
}: {
  committee: Committee;
  senators: Senator[];
  onUpdate: (committee: Committee) => void;
}) {
  const [senatorId, setSenatorId] = useState("");
  const [role, setRole] = useState("");
  const [isSavingCommittee, setIsSavingCommittee] = useState(false);
  const [editForm, setEditForm] = useState<CommitteeFormState>({
    name: committee.name,
    description: committee.description,
    chair_senator_id: "",
    chair_name: committee.chair_name,
    chair_email: committee.chair_email,
    is_active: committee.is_active,
  });

  useEffect(() => {
    const inferredChair = senators.find(
      (senator) => senator.email === committee.chair_email,
    );

    setEditForm({
      name: committee.name,
      description: committee.description,
      chair_senator_id: inferredChair ? String(inferredChair.id) : "",
      chair_name: committee.chair_name,
      chair_email: committee.chair_email,
      is_active: committee.is_active,
    });
  }, [committee, senators]);

  const existingIds = new Set(committee.members.map((member) => member.id));
  const availableSenators = senators.filter(
    (senator) => !existingIds.has(senator.id),
  );

  function getRole(member: Senator): string {
    const assignment = member.committees?.find(
      (item: CommitteeAssignment) => item.committee_id === committee.id,
    );
    return assignment?.role ?? "Member";
  }

  function handleChairChange(id: string): void {
    if (!id) {
      setEditForm((prev) => ({
        ...prev,
        chair_senator_id: "",
        chair_name: "",
        chair_email: "",
      }));
      return;
    }

    const senator = senators.find((s) => s.id === Number(id));
    if (!senator) return;

    setEditForm((prev) => ({
      ...prev,
      chair_senator_id: id,
      chair_name: `${senator.first_name} ${senator.last_name}`,
      chair_email: senator.email,
    }));
  }

  return (
    <div className="space-y-4">
      <h3 className="font-semibold text-slate-900">Committee Details</h3>

      <div className="space-y-4">
        <div className="space-y-2">
          <Label htmlFor="edit-committee-name">Name</Label>
          <Input
            id="edit-committee-name"
            placeholder="Committee name"
            value={editForm.name}
            onChange={(e) =>
              setEditForm((prev) => ({ ...prev, name: e.target.value }))
            }
          />
        </div>

        <div className="space-y-2">
          <Label htmlFor="edit-committee-description">Description</Label>
          <Textarea
            id="edit-committee-description"
            placeholder="Committee description"
            value={editForm.description}
            onChange={(e) =>
              setEditForm((prev) => ({ ...prev, description: e.target.value }))
            }
          />
        </div>

        <div className="space-y-2">
          <Label htmlFor="edit-committee-chair">Chair</Label>
          <Select
            value={editForm.chair_senator_id}
            onValueChange={handleChairChange}
          >
            <SelectTrigger id="edit-committee-chair">
              <SelectValue placeholder="Select a chair" />
            </SelectTrigger>
            <SelectContent>
              {senators.map((s) => (
                <SelectItem key={s.id} value={String(s.id)}>
                  {s.first_name} {s.last_name}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
        </div>

        {editForm.chair_name && (
          <div className="space-y-2 rounded-md bg-slate-50 p-3">
            <div className="space-y-1">
              <p className="text-xs font-semibold uppercase text-slate-500">
                Chair Name
              </p>
              <p className="text-sm text-slate-900">{editForm.chair_name}</p>
            </div>
            <div className="space-y-1">
              <p className="text-xs font-semibold uppercase text-slate-500">
                Chair Email
              </p>
              <p className="text-sm text-slate-900">{editForm.chair_email}</p>
            </div>
          </div>
        )}

        <div className="flex items-center gap-2">
          <Checkbox
            id="edit-committee-active"
            checked={editForm.is_active}
            onCheckedChange={(checked) =>
              setEditForm((prev) => ({ ...prev, is_active: Boolean(checked) }))
            }
          />
          <Label htmlFor="edit-committee-active">Active</Label>
        </div>

        <Button
          variant="outline"
          disabled={isSavingCommittee}
          onClick={async () => {
            setIsSavingCommittee(true);
            try {
              const updated = await updateCommittee(
                committee.id,
                toCommitteePayload(editForm),
              );
              onUpdate(updated);
            } catch (error) {
              console.error("Failed to update committee:", error);
              alert("Failed to update committee.");
            } finally {
              setIsSavingCommittee(false);
            }
          }}
        >
          {isSavingCommittee ? "Saving..." : "Save Committee"}
        </Button>
      </div>

      <h3 className="font-semibold text-slate-900">Members</h3>

      <div className="space-y-2">
        {committee.members.map((member) => (
          <div
            key={member.id}
            className="flex items-center justify-between rounded-md border border-slate-200 bg-slate-50 px-3 py-2"
          >
            <span className="text-sm">
              {member.first_name} {member.last_name} - {getRole(member)}
            </span>

            <button
              className="text-sm font-medium text-rose-600 hover:text-rose-700"
              onClick={async () => {
                try {
                  await removeCommitteeMember(committee.id, member.id);
                  onUpdate({
                    ...committee,
                    members: committee.members.filter(
                      (m) => m.id !== member.id,
                    ),
                  });
                } catch (error) {
                  console.error("Failed to remove committee member:", error);
                  alert("Failed to remove committee member.");
                }
              }}
            >
              Remove
            </button>
          </div>
        ))}
      </div>

      <div className="space-y-3 border-t border-slate-100 pt-3">
        <h4 className="text-sm font-semibold text-slate-700">Add Member</h4>
        <div className="space-y-3">
          <div className="space-y-2">
            <Label htmlFor="add-senator">Senator</Label>
            <Select value={senatorId} onValueChange={setSenatorId}>
              <SelectTrigger id="add-senator">
                <SelectValue placeholder="Select a senator" />
              </SelectTrigger>
              <SelectContent>
                {availableSenators.map((s) => (
                  <SelectItem key={s.id} value={String(s.id)}>
                    {s.first_name} {s.last_name}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>

          <div className="space-y-2">
            <Label htmlFor="add-role">Role</Label>
            <Input
              id="add-role"
              placeholder="e.g., Vice Chair, Member"
              value={role}
              onChange={(e) => setRole(e.target.value)}
            />
          </div>

          <Button
            variant="outline"
            onClick={async () => {
              if (!senatorId) {
                alert("Please select a senator to add.");
                return;
              }

              const selectedRole = role.trim() || "Member";

              try {
                await assignCommitteeMember(committee.id, {
                  senator_id: Number(senatorId),
                  role: selectedRole,
                });

                const senator = senators.find(
                  (s) => s.id === Number(senatorId),
                );
                if (!senator) return;

                const updatedMember: Senator = {
                  ...senator,
                  committees: [
                    ...(senator.committees ?? []),
                    {
                      committee_id: committee.id,
                      committee_name: committee.name,
                      role: selectedRole,
                    },
                  ],
                };

                onUpdate({
                  ...committee,
                  members: [...committee.members, updatedMember],
                });

                setSenatorId("");
                setRole("");
              } catch (error) {
                console.error("Failed to add committee member:", error);
                alert("Failed to add committee member.");
              }
            }}
          >
            Add Member
          </Button>
        </div>
      </div>
    </div>
  );
}
