"use client";

import {
  AdminBackButton,
  AdminCard,
  AdminPageHeader,
  AdminPageShell,
} from "@/components/admin/AdminPageShell";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import {
  createLegislationAction,
  deleteLegislationAction,
  updateLegislationAction,
} from "@/lib/admin-api";
import { getLegislationById } from "@/lib/api";
import type { Legislation, LegislationAction } from "@/types";
import { useParams, useRouter } from "next/navigation";
import { useCallback, useEffect, useState } from "react";

function toDateInputValue(value: string): string {
  return new Date(value).toISOString().split("T")[0];
}

export default function LegislationDetailsPage() {
  const router = useRouter();
  const { id } = useParams() as { id: string };
  const numId = Number(id);

  const [legislation, setLegislation] = useState<Legislation | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  // State for the "New Action" Form
  const [actionDate, setActionDate] = useState("");
  const [actionType, setActionType] = useState("");
  const [actionDescription, setActionDescription] = useState("");

  // State for editing existing actions
  const [editingActionId, setEditingActionId] = useState<number | null>(null);
  const [editActionDate, setEditActionDate] = useState("");
  const [editActionType, setEditActionType] = useState("");
  const [editActionDescription, setEditActionDescription] = useState("");

  const fetchDetails = useCallback(async () => {
    setIsLoading(true);
    try {
      const data = await getLegislationById(numId);
      setLegislation(data);
    } catch (e) {
      console.error(e);
    } finally {
      setIsLoading(false);
    }
  }, [numId]);

  useEffect(() => {
    fetchDetails();
  }, [fetchDetails]);

  const handleAddAction = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await createLegislationAction(numId, {
        action_date: new Date(actionDate).toISOString(),
        action_type: actionType,
        description: actionDescription,
      });
      // Clear form
      setActionDate("");
      setActionType("");
      setActionDescription("");
      // Refresh timeline
      fetchDetails();
    } catch (err) {
      alert("Failed to add action");
    }
  };

  const beginEditAction = (action: LegislationAction) => {
    setEditingActionId(action.id);
    setEditActionDate(toDateInputValue(action.action_date));
    setEditActionType(action.action_type);
    setEditActionDescription(action.description);
  };

  const cancelEditAction = () => {
    setEditingActionId(null);
    setEditActionDate("");
    setEditActionType("");
    setEditActionDescription("");
  };

  const handleUpdateAction = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!editingActionId) return;

    try {
      await updateLegislationAction(numId, editingActionId, {
        action_date: new Date(editActionDate).toISOString(),
        action_type: editActionType,
        description: editActionDescription,
      });
      cancelEditAction();
      fetchDetails();
    } catch {
      alert("Failed to update action");
    }
  };

  const handleDeleteAction = async (actionId: number) => {
    if (!window.confirm("Delete this action?")) return;
    try {
      await deleteLegislationAction(numId, actionId);
      fetchDetails();
    } catch (err) {
      alert("Failed to delete action");
    }
  };

  if (isLoading) {
    return (
      <AdminPageShell>
        <div className="py-20 text-center text-slate-500">Loading data...</div>
      </AdminPageShell>
    );
  }

  if (!legislation) {
    return (
      <AdminPageShell>
        <div className="py-20 text-center text-slate-500">
          Legislation not found.
        </div>
      </AdminPageShell>
    );
  }

  return (
    <AdminPageShell>
      <AdminBackButton
        onClick={() => router.back()}
        label="Back to Legislation List"
      />

      <AdminPageHeader
        title={`${legislation.bill_number}: ${legislation.title}`}
        description="Review the legislation metadata and manage timeline actions."
      />

      <AdminCard>
        <div className="grid gap-4 text-sm text-slate-700 sm:grid-cols-2">
          <p>
            <span className="font-semibold text-slate-900">Status:</span>{" "}
            {legislation.status}
          </p>
          <p>
            <span className="font-semibold text-slate-900">Type:</span>{" "}
            {legislation.type}
          </p>
          <p>
            <span className="font-semibold text-slate-900">Sponsor:</span>{" "}
            {legislation.sponsor_name}
          </p>
          <p>
            <span className="font-semibold text-slate-900">Session:</span>{" "}
            {legislation.session_number}
          </p>
        </div>
      </AdminCard>

      <div className="grid gap-6 lg:grid-cols-2">
        <AdminCard>
          <h2 className="mb-4 text-lg font-semibold text-slate-900">
            Actions Timeline
          </h2>
          {!legislation.actions || legislation.actions.length === 0 ? (
            <p className="text-slate-500">No actions recorded yet.</p>
          ) : (
            <div className="space-y-4">
              {legislation.actions.map((action) => (
                <div
                  key={action.id}
                  className="rounded-md border border-slate-200 bg-slate-50 p-4"
                >
                  {editingActionId === action.id ? (
                    <form onSubmit={handleUpdateAction} className="space-y-2">
                      <Input
                        required
                        type="date"
                        value={editActionDate}
                        onChange={(e) => setEditActionDate(e.target.value)}
                      />
                      <Input
                        required
                        type="text"
                        value={editActionType}
                        onChange={(e) => setEditActionType(e.target.value)}
                      />
                      <Textarea
                        required
                        rows={2}
                        value={editActionDescription}
                        onChange={(e) =>
                          setEditActionDescription(e.target.value)
                        }
                      />
                      <div className="flex gap-2">
                        <Button type="submit" size="sm">
                          Save
                        </Button>
                        <Button
                          type="button"
                          variant="outline"
                          size="sm"
                          onClick={cancelEditAction}
                        >
                          Cancel
                        </Button>
                      </div>
                    </form>
                  ) : (
                    <>
                      <div className="flex justify-between">
                        <strong className="text-slate-900">
                          {new Date(action.action_date).toLocaleDateString()} -{" "}
                          {action.action_type}
                        </strong>
                        <div className="flex gap-3 text-xs font-medium">
                          <button
                            onClick={() => beginEditAction(action)}
                            className="text-blue-700 hover:text-blue-800"
                          >
                            Edit
                          </button>
                          <button
                            onClick={() => handleDeleteAction(action.id)}
                            className="text-rose-700 hover:text-rose-800"
                          >
                            Delete
                          </button>
                        </div>
                      </div>
                      <p className="mt-1 text-sm text-slate-700">
                        {action.description}
                      </p>
                    </>
                  )}
                </div>
              ))}
            </div>
          )}
        </AdminCard>

        <AdminCard className="h-fit">
          <h2 className="mb-4 text-lg font-semibold text-slate-900">
            Add New Action
          </h2>
          <form onSubmit={handleAddAction} className="space-y-4">
            <div className="space-y-2">
              <Label htmlFor="new-action-date">Date</Label>
              <Input
                id="new-action-date"
                required
                type="date"
                value={actionDate}
                onChange={(e) => setActionDate(e.target.value)}
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="new-action-type">
                Type (for example, Sent to Committee)
              </Label>
              <Input
                id="new-action-type"
                required
                type="text"
                value={actionType}
                onChange={(e) => setActionType(e.target.value)}
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="new-action-description">Description</Label>
              <Textarea
                id="new-action-description"
                required
                rows={3}
                value={actionDescription}
                onChange={(e) => setActionDescription(e.target.value)}
              />
            </div>
            <Button type="submit" className="w-full">
              Add Action
            </Button>
          </form>
        </AdminCard>
      </div>
    </AdminPageShell>
  );
}
