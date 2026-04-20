"use client";

import { Button } from "@/components/ui/button";
import { getSenators } from "@/lib/api";
import {
  assignCommitteeMember,
  createCommittee,
  deleteCommittee,
  getAdminCommittees,
  removeCommitteeMember,
  updateCommittee,
} from "@/lib/mock/admin-api";
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
    <div className="container mx-auto py-8 space-y-6">
      <h1 className="text-4xl font-bold">Admin Committees</h1>

      <CommitteeForm
        senators={senators}
        onCreate={async (data) => {
          const created = await createCommittee(data);
          setCommittees((prev) => [...prev, created]);
        }}
      />

      <div className="overflow-x-auto border rounded-md">
        {isLoading && (
          <p className="text-sm text-muted-foreground p-3">
            Loading committees...
          </p>
        )}

        <table className="w-full text-sm">
          <thead className="bg-muted/50">
            <tr>
              <th className="text-left p-3 font-medium">Name</th>
              <th className="text-left p-3 font-medium">Chair</th>
              <th className="text-left p-3 font-medium">Active</th>
              <th className="text-left p-3 font-medium">Member Count</th>
              <th className="text-left p-3 font-medium">Actions</th>
            </tr>
          </thead>

          <tbody>
            {committees.map((committee) => (
              <Fragment key={committee.id}>
                <tr className="border-t align-top">
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
                  <tr className="border-t bg-muted/20">
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
      </div>
    </div>
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
    <div className="border rounded p-4 space-y-3">
      <h2 className="font-semibold">Create Committee</h2>

      <input
        className="border px-3 py-1"
        placeholder="Name"
        value={form.name}
        onChange={(e) => setForm((prev) => ({ ...prev, name: e.target.value }))}
        disabled={isSubmitting}
      />

      <textarea
        className="border px-3 py-1"
        placeholder="Description"
        value={form.description}
        onChange={(e) =>
          setForm((prev) => ({ ...prev, description: e.target.value }))
        }
        disabled={isSubmitting}
      />

      <select
        className="border px-3 py-1"
        value={form.chair_senator_id}
        onChange={(e) => handleChairChange(e.target.value)}
        disabled={isSubmitting}
      >
        <option value="">Select Chair</option>
        {senators.map((s) => (
          <option key={s.id} value={s.id}>
            {s.first_name} {s.last_name}
          </option>
        ))}
      </select>

      <input className="border px-3 py-1" value={form.chair_name} disabled />
      <input className="border px-3 py-1" value={form.chair_email} disabled />

      <label className="flex items-center gap-2">
        <input
          type="checkbox"
          checked={form.is_active}
          onChange={(e) =>
            setForm((prev) => ({ ...prev, is_active: e.target.checked }))
          }
          disabled={isSubmitting}
        />
        Active
      </label>

      <Button
        className="border px-3 py-1"
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
    <div className="border rounded p-4 space-y-4">
      <h3 className="font-semibold">Committee Details</h3>

      <div className="grid gap-2">
        <input
          className="border px-3 py-1"
          placeholder="Name"
          value={editForm.name}
          onChange={(e) =>
            setEditForm((prev) => ({ ...prev, name: e.target.value }))
          }
        />

        <textarea
          className="border px-3 py-1"
          placeholder="Description"
          value={editForm.description}
          onChange={(e) =>
            setEditForm((prev) => ({ ...prev, description: e.target.value }))
          }
        />

        <select
          className="border px-3 py-1"
          value={editForm.chair_senator_id}
          onChange={(e) => handleChairChange(e.target.value)}
        >
          <option value="">Select Chair</option>
          {senators.map((s) => (
            <option key={s.id} value={s.id}>
              {s.first_name} {s.last_name}
            </option>
          ))}
        </select>

        <input
          className="border px-3 py-1"
          value={editForm.chair_name}
          disabled
        />
        <input
          className="border px-3 py-1"
          value={editForm.chair_email}
          disabled
        />

        <label className="flex items-center gap-2">
          <input
            type="checkbox"
            checked={editForm.is_active}
            onChange={(e) =>
              setEditForm((prev) => ({ ...prev, is_active: e.target.checked }))
            }
          />
          Active
        </label>

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

      <h3 className="font-semibold">Members</h3>

      <div className="space-y-2">
        {committee.members.map((member) => (
          <div key={member.id} className="flex justify-between">
            <span>
              {member.first_name} {member.last_name} - {getRole(member)}
            </span>

            <button
              className="text-red-500"
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

      <div className="flex gap-2 pt-2 border-t">
        <select
          className="border px-3 py-1"
          value={senatorId}
          onChange={(e) => setSenatorId(e.target.value)}
        >
          <option value="">Select senator</option>
          {availableSenators.map((s) => (
            <option key={s.id} value={s.id}>
              {s.first_name} {s.last_name}
            </option>
          ))}
        </select>

        <input
          className="border px-3 py-1"
          placeholder="Role"
          value={role}
          onChange={(e) => setRole(e.target.value)}
        />

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

              const senator = senators.find((s) => s.id === Number(senatorId));
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
  );
}
