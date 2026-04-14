"use client";

import { useEffect, useState } from "react";
import {
  createCommittee,
  updateCommittee,
  deleteCommittee,
  assignCommitteeMember,
  removeCommitteeMember,
} from "@/lib/admin-api";
import { getSenators } from "@/lib/api";
import type { Committee, Senator } from "@/types";

import {
  Card,
  CardContent,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Button } from "@/components/ui/button";

export default function CommitteesPage() {
  const [committees, setCommittees] = useState<Committee[]>([]);
  const [senators, setSenators] = useState<Senator[]>([]);
  const [expanded, setExpanded] = useState<number | null>(null);

  useEffect(() => {
    async function load() {
      const [c, s] = await Promise.all([
        fetch("/api/admin/committees").then((r) => r.json()),
        getSenators(),
      ]);
      setCommittees(c);
      setSenators(s);
    }
    load();
  }, []);

  function updateLocal(updated: Committee) {
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
          const res = await createCommittee(data);
          setCommittees((p) => [...p, res]);
        }}
      />

      <div className="grid gap-4">
        {committees.map((c) => (
          <Card key={c.id}>
            <CardHeader>
              <CardTitle>{c.name}</CardTitle>
              <p className="text-sm text-muted-foreground">
                Chair: {c.chair_name} •{" "}
                {c.is_active ? "Active" : "Inactive"} •{" "}
                {c.members.length} members
              </p>
            </CardHeader>

            <CardContent className="space-y-3">
              <div className="flex gap-2">
                <Button
                  variant="outline"
                  onClick={() =>
                    setExpanded(expanded === c.id ? null : c.id)
                  }
                >
                  {expanded === c.id ? "Hide" : "Manage"}
                </Button>

                <Button
                  variant="destructive"
                  onClick={async () => {
                    await deleteCommittee(c.id);
                    setCommittees((p) =>
                      p.filter((x) => x.id !== c.id),
                    );
                  }}
                >
                  Delete
                </Button>
              </div>

              {expanded === c.id && (
                <CommitteeDetail
                  committee={c}
                  senators={senators}
                  onUpdate={updateLocal}
                />
              )}
            </CardContent>
          </Card>
        ))}
      </div>
    </div>
  );
}

function CommitteeForm({
  senators,
  onCreate,
}: {
  senators: Senator[];
  onCreate: (data: any) => Promise<void>;
}) {
  const [form, setForm] = useState({
    name: "",
    description: "",
    chair_senator_id: "",
    chair_name: "",
    chair_email: "",
    is_active: true,
  });

  function handleChairChange(id: string) {
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
        placeholder="Name"
        value={form.name}
        onChange={(e) =>
          setForm({ ...form, name: e.target.value })
        }
      />

      <textarea
        placeholder="Description"
        value={form.description}
        onChange={(e) =>
          setForm({ ...form, description: e.target.value })
        }
      />

      <select
        value={form.chair_senator_id}
        onChange={(e) => handleChairChange(e.target.value)}
      >
        <option value="">Select Chair</option>
        {senators.map((s) => (
          <option key={s.id} value={s.id}>
            {s.first_name} {s.last_name}
          </option>
        ))}
      </select>

      <input value={form.chair_name} disabled />
      <input value={form.chair_email} disabled />

      <label className="flex items-center gap-2">
        <input
          type="checkbox"
          checked={form.is_active}
          onChange={(e) =>
            setForm({ ...form, is_active: e.target.checked })
          }
        />
        Active
      </label>

      <button
        className="border px-3 py-1"
        onClick={async () => {
          const res = await onCreate(form);
          setForm({
            name: "",
            description: "",
            chair_senator_id: "",
            chair_name: "",
            chair_email: "",
            is_active: true,
          });
        }}
      >
        Create
      </button>
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
  onUpdate: (c: Committee) => void;
}) {
  const [senatorId, setSenatorId] = useState("");
  const [role, setRole] = useState("");

  const existingIds = new Set(committee.members.map((m) => m.id));

  const availableSenators = senators.filter(
    (s) => !existingIds.has(s.id),
  );

  function getRole(member: any) {
    const assignment = member.committees?.find(
      (c: any) => c.committee_id === committee.id,
    );
    return assignment?.role ?? "Member";
  }

  return (
    <div className="border rounded p-4 space-y-4">
      <h3 className="font-semibold">Members</h3>

      {/* Member list */}
      <div className="space-y-2">
        {committee.members.map((m) => (
          <div key={m.id} className="flex justify-between">
            <span>
              {m.first_name} {m.last_name} — {getRole(m)}
            </span>

            <button
              className="text-red-500"
              onClick={async () => {
                await removeCommitteeMember(
                  committee.id,
                  m.id,
                );

                const updated = {
                  ...committee,
                  members: committee.members.filter((x) => x.id !== m.id),
                };

                onUpdate(updated);
              }}
            >
              Remove
            </button>
          </div>
        ))}
      </div>

      {/* Add member */}
      <div className="flex gap-2 pt-2 border-t">
        <select
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
          placeholder="Role"
          value={role}
          onChange={(e) => setRole(e.target.value)}
        />

        <button
          className="border px-3"
          onClick={async () => {
            await assignCommitteeMember(committee.id, {
              senator_id: Number(senatorId),
              role,
            });

            const senator = senators.find((s) => s.id === Number(senatorId));
            if (!senator) return;

            const updated: Committee = {
              ...committee,
              members: [...committee.members, senator],
            };

            onUpdate(updated);

            setSenatorId("");
            setRole("");
          }}
        >
          Add Member
        </button>
      </div>
    </div>
  );
}
