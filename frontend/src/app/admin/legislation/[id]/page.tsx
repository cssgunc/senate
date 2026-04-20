"use client";

import {
  createLegislationAction,
  deleteLegislationAction,
  updateLegislationAction,
} from "@/lib/admin-api";
import { getLegislationById } from "@/lib/api";
import { Legislation, LegislationAction } from "@/types";
import { useParams, useRouter } from "next/navigation";
import { useCallback, useEffect, useState } from "react";

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
    setEditActionDate(new Date(action.action_date).toISOString().split("T")[0]);
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

  if (isLoading) return <div>Loading details...</div>;
  if (!legislation) return <div>Legislation not found</div>;

  return (
    <div className="space-y-6">
      <button onClick={() => router.back()} className="text-blue-600">
        &larr; Back to List
      </button>

      <div className="bg-white p-6 border rounded-lg shadow-sm">
        <h1 className="text-2xl font-bold mb-4">
          {legislation.bill_number}: {legislation.title}
        </h1>
        <div className="grid grid-cols-2 gap-4 text-sm text-gray-700">
          <p>
            <strong>Status:</strong> {legislation.status}
          </p>
          <p>
            <strong>Type:</strong> {legislation.type}
          </p>
          <p>
            <strong>Sponsor:</strong> {legislation.sponsor_name}
          </p>
          <p>
            <strong>Session:</strong> {legislation.session_number}
          </p>
        </div>
      </div>

      <div className="grid md:grid-cols-2 gap-6">
        {/* Actions Timeline */}
        <div className="bg-white p-6 border rounded-lg shadow-sm">
          <h2 className="text-xl font-bold mb-4">Actions Timeline</h2>
          {!legislation.actions || legislation.actions.length === 0 ? (
            <p className="text-gray-500">No actions recorded yet.</p>
          ) : (
            <div className="space-y-4">
              {legislation.actions.map((action) => (
                <div
                  key={action.id}
                  className="border-l-4 border-blue-500 pl-4 py-1"
                >
                  {editingActionId === action.id ? (
                    <form onSubmit={handleUpdateAction} className="space-y-2">
                      <input
                        required
                        type="date"
                        className="w-full p-2 border rounded"
                        value={editActionDate}
                        onChange={(e) => setEditActionDate(e.target.value)}
                      />
                      <input
                        required
                        type="text"
                        className="w-full p-2 border rounded"
                        value={editActionType}
                        onChange={(e) => setEditActionType(e.target.value)}
                      />
                      <textarea
                        required
                        className="w-full p-2 border rounded"
                        rows={2}
                        value={editActionDescription}
                        onChange={(e) =>
                          setEditActionDescription(e.target.value)
                        }
                      />
                      <div className="flex gap-3 text-sm">
                        <button
                          type="submit"
                          className="text-blue-600 hover:underline"
                        >
                          Save
                        </button>
                        <button
                          type="button"
                          onClick={cancelEditAction}
                          className="text-gray-600 hover:underline"
                        >
                          Cancel
                        </button>
                      </div>
                    </form>
                  ) : (
                    <>
                      <div className="flex justify-between">
                        <strong>
                          {new Date(action.action_date).toLocaleDateString()} -{" "}
                          {action.action_type}
                        </strong>
                        <div className="flex gap-3 text-xs">
                          <button
                            onClick={() => beginEditAction(action)}
                            className="text-blue-600 hover:underline"
                          >
                            Edit
                          </button>
                          <button
                            onClick={() => handleDeleteAction(action.id)}
                            className="text-red-500 hover:underline"
                          >
                            Delete
                          </button>
                        </div>
                      </div>
                      <p className="text-sm text-gray-700 mt-1">
                        {action.description}
                      </p>
                    </>
                  )}
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Add Action Form */}
        <div className="bg-white p-6 border rounded-lg shadow-sm h-fit">
          <h2 className="text-xl font-bold mb-4">Add New Action</h2>
          <form onSubmit={handleAddAction} className="space-y-4">
            <div>
              <label className="block text-sm font-medium mb-1">Date</label>
              <input
                required
                type="date"
                className="w-full p-2 border rounded"
                value={actionDate}
                onChange={(e) => setActionDate(e.target.value)}
              />
            </div>
            <div>
              <label className="block text-sm font-medium mb-1">
                Type (for example, Sent to Committee)
              </label>
              <input
                required
                type="text"
                className="w-full p-2 border rounded"
                value={actionType}
                onChange={(e) => setActionType(e.target.value)}
              />
            </div>
            <div>
              <label className="block text-sm font-medium mb-1">
                Description
              </label>
              <textarea
                required
                className="w-full p-2 border rounded"
                rows={3}
                value={actionDescription}
                onChange={(e) => setActionDescription(e.target.value)}
              />
            </div>
            <button
              type="submit"
              className="w-full bg-blue-600 text-white rounded p-2 hover:bg-blue-700"
            >
              Add Action
            </button>
          </form>
        </div>
      </div>
    </div>
  );
}
