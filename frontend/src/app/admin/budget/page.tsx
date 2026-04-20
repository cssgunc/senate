"use client";

import {
  AdminCard,
  AdminPageHeader,
  AdminPageShell,
} from "@/components/admin/AdminPageShell";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import {
  createBudgetData,
  deleteBudgetData,
  updateBudgetData,
} from "@/lib/admin-api";
import { getBudget } from "@/lib/api";
import type { BudgetData } from "@/types";
import { useEffect, useMemo, useState } from "react";

type FlatBudgetNode = {
  id: number;
  parentId: number | null;
  depth: number;
  displayOrder: number;
  fiscalYear: string;
  category: string;
  amount: number;
  description: string | null;
  childCount: number;
  descendantCount: number;
};

type BudgetFormState = {
  fiscal_year: string;
  category: string;
  amount: string;
  description: string;
  parent_category_id: number | null;
};

const EMPTY_FORM: BudgetFormState = {
  fiscal_year: "",
  category: "",
  amount: "",
  description: "",
  parent_category_id: null,
};

const TOP_LEVEL_PARENT_VALUE = "__top_level__";

function errorMessage(error: unknown): string {
  return error instanceof Error ? error.message : "Request failed";
}

function flattenBudget(
  rows: BudgetData[],
  parentId: number | null = null,
  depth: number = 0,
): FlatBudgetNode[] {
  return rows.flatMap((row, index) => {
    const children = flattenBudget(row.children ?? [], row.id, depth + 1);
    return [
      {
        id: row.id,
        parentId,
        depth,
        displayOrder: index + 1,
        fiscalYear: row.fiscal_year,
        category: row.category,
        amount: Number(row.amount),
        description: row.description,
        childCount: (row.children ?? []).length,
        descendantCount: children.length,
      },
      ...children,
    ];
  });
}

function collectDescendantIds(
  rootId: number,
  childrenByParent: Map<number, number[]>,
): Set<number> {
  const descendants = new Set<number>();
  const stack = [...(childrenByParent.get(rootId) ?? [])];

  while (stack.length > 0) {
    const current = stack.pop();
    if (current === undefined || descendants.has(current)) continue;
    descendants.add(current);
    const children = childrenByParent.get(current) ?? [];
    stack.push(...children);
  }

  return descendants;
}

function currency(amount: number): string {
  return new Intl.NumberFormat("en-US", {
    style: "currency",
    currency: "USD",
    maximumFractionDigits: 0,
  }).format(amount);
}

export default function AdminBudgetPage() {
  const [isLoading, setIsLoading] = useState(true);
  const [isSaving, setIsSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const [selectedFiscalYear, setSelectedFiscalYear] = useState("");
  const [budgetTree, setBudgetTree] = useState<BudgetData[]>([]);
  const [availableFiscalYears, setAvailableFiscalYears] = useState<string[]>(
    [],
  );

  const [topLevelForm, setTopLevelForm] = useState<BudgetFormState>(EMPTY_FORM);
  const [subCategoryForm, setSubCategoryForm] =
    useState<BudgetFormState>(EMPTY_FORM);
  const [editForm, setEditForm] = useState<BudgetFormState>(EMPTY_FORM);
  const [editingId, setEditingId] = useState<number | null>(null);

  const flatRows = useMemo(() => flattenBudget(budgetTree), [budgetTree]);
  const childrenByParent = useMemo(() => {
    const map = new Map<number, number[]>();
    for (const row of flatRows) {
      if (row.parentId === null) continue;
      const existingChildren = map.get(row.parentId) ?? [];
      existingChildren.push(row.id);
      map.set(row.parentId, existingChildren);
    }
    return map;
  }, [flatRows]);

  const disallowedParentIds = useMemo(() => {
    if (editingId === null) return new Set<number>();
    const disallowed = collectDescendantIds(editingId, childrenByParent);
    disallowed.add(editingId);
    return disallowed;
  }, [editingId, childrenByParent]);

  async function loadBudget(fiscalYear?: string) {
    setIsLoading(true);
    setError(null);
    try {
      const tree = await getBudget(fiscalYear);
      setBudgetTree(tree);

      const fetchedYear =
        tree[0]?.fiscal_year ?? (fiscalYear !== undefined ? fiscalYear : "");

      if (fetchedYear) {
        setSelectedFiscalYear(fetchedYear);
        setTopLevelForm((current) => ({
          ...current,
          fiscal_year: fetchedYear,
        }));
        setSubCategoryForm((current) => ({
          ...current,
          fiscal_year: fetchedYear,
        }));
      }

      const years = new Set(availableFiscalYears);
      if (fetchedYear) years.add(fetchedYear);
      setAvailableFiscalYears(Array.from(years).sort().reverse());
    } catch (err) {
      setError(errorMessage(err));
    } finally {
      setIsLoading(false);
    }
  }

  useEffect(() => {
    void loadBudget();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  async function onCreate(
    form: BudgetFormState,
    resetForm: () => void,
    defaultParentId: number | null,
  ) {
    if (!form.fiscal_year || !form.category || !form.amount) {
      setError("Fiscal year, category, and amount are required.");
      return;
    }

    const amount = Number(form.amount);
    if (!Number.isFinite(amount) || amount <= 0) {
      setError("Amount must be a positive number.");
      return;
    }

    const parentId = form.parent_category_id ?? defaultParentId;
    const siblingCount = flatRows.filter(
      (row) => row.parentId === parentId && row.fiscalYear === form.fiscal_year,
    ).length;

    setIsSaving(true);
    setError(null);
    try {
      await createBudgetData({
        fiscal_year: form.fiscal_year,
        category: form.category,
        amount,
        description: form.description || null,
        parent_category_id: parentId,
        display_order: siblingCount + 1,
      });

      await loadBudget(form.fiscal_year);
      resetForm();
    } catch (err) {
      setError(errorMessage(err));
    } finally {
      setIsSaving(false);
    }
  }

  function startEdit(row: FlatBudgetNode) {
    setEditingId(row.id);
    setEditForm({
      fiscal_year: row.fiscalYear,
      category: row.category,
      amount: row.amount.toString(),
      description: row.description ?? "",
      parent_category_id: row.parentId,
    });
  }

  async function saveEdit() {
    if (editingId === null) return;
    if (!editForm.fiscal_year || !editForm.category || !editForm.amount) {
      setError("Fiscal year, category, and amount are required.");
      return;
    }

    const amount = Number(editForm.amount);
    if (!Number.isFinite(amount) || amount <= 0) {
      setError("Amount must be a positive number.");
      return;
    }

    const existing = flatRows.find((row) => row.id === editingId);
    if (!existing) {
      setError("Could not find selected budget row.");
      return;
    }

    if (
      editForm.parent_category_id !== null &&
      disallowedParentIds.has(editForm.parent_category_id)
    ) {
      setError("Invalid parent category selection.");
      return;
    }

    setIsSaving(true);
    setError(null);
    try {
      await updateBudgetData(editingId, {
        fiscal_year: editForm.fiscal_year,
        category: editForm.category,
        amount,
        description: editForm.description || null,
        parent_category_id: editForm.parent_category_id,
        display_order: existing.displayOrder,
      });
      await loadBudget(editForm.fiscal_year);
      setEditingId(null);
      setEditForm(EMPTY_FORM);
    } catch (err) {
      setError(errorMessage(err));
    } finally {
      setIsSaving(false);
    }
  }

  async function onDelete(row: FlatBudgetNode) {
    const warning =
      row.descendantCount > 0
        ? `Delete ${row.category}? This may also affect ${row.descendantCount} child categor${row.descendantCount === 1 ? "y" : "ies"}.`
        : `Delete ${row.category}?`;
    if (!window.confirm(warning)) return;

    setIsSaving(true);
    setError(null);
    try {
      await deleteBudgetData(row.id);
      await loadBudget(selectedFiscalYear || row.fiscalYear);
      if (editingId === row.id) {
        setEditingId(null);
        setEditForm(EMPTY_FORM);
      }
    } catch (err) {
      setError(errorMessage(err));
    } finally {
      setIsSaving(false);
    }
  }

  return (
    <AdminPageShell className="space-y-8">
      <AdminPageHeader
        title="Budget"
        description="Manage fiscal-year categories for the budget visualization."
      />

      {error ? (
        <p className="rounded-md border border-rose-200 bg-rose-50 px-3 py-2 text-sm text-rose-700">
          {error}
        </p>
      ) : null}

      <AdminCard className="p-4">
        <h2 className="text-lg font-semibold text-slate-900">Fiscal Year</h2>
        <div className="mt-3 flex flex-wrap items-end gap-3">
          <div className="space-y-2">
            <Label htmlFor="fiscal-year-select">
              Select or enter fiscal year
            </Label>
            <Input
              id="fiscal-year-select"
              type="text"
              value={selectedFiscalYear}
              onChange={(event) => setSelectedFiscalYear(event.target.value)}
              list="fiscal-year-options"
              placeholder="FY 2026"
            />
          </div>
          <datalist id="fiscal-year-options">
            {availableFiscalYears.map((year) => (
              <option key={year} value={year} />
            ))}
          </datalist>
          <Button
            onClick={() => void loadBudget(selectedFiscalYear || undefined)}
            disabled={isLoading}
          >
            {isLoading ? "Loading..." : "Load Year"}
          </Button>
        </div>
      </AdminCard>

      <AdminCard className="p-4">
        <h2 className="text-lg font-semibold text-slate-900">
          Add Top-Level Category
        </h2>
        <form
          className="mt-4 grid gap-4 md:grid-cols-2"
          onSubmit={(event) => {
            event.preventDefault();
            void onCreate(
              topLevelForm,
              () =>
                setTopLevelForm((current) => ({
                  ...EMPTY_FORM,
                  fiscal_year: current.fiscal_year,
                })),
              null,
            );
          }}
        >
          <div className="space-y-2">
            <Label htmlFor="top-fiscal-year">Fiscal year</Label>
            <Input
              id="top-fiscal-year"
              type="text"
              value={topLevelForm.fiscal_year}
              onChange={(event) =>
                setTopLevelForm((current) => ({
                  ...current,
                  fiscal_year: event.target.value,
                }))
              }
              required
            />
          </div>

          <div className="space-y-2">
            <Label htmlFor="top-category">Category</Label>
            <Input
              id="top-category"
              type="text"
              value={topLevelForm.category}
              onChange={(event) =>
                setTopLevelForm((current) => ({
                  ...current,
                  category: event.target.value,
                }))
              }
              required
            />
          </div>

          <div className="space-y-2">
            <Label htmlFor="top-amount">Amount</Label>
            <Input
              id="top-amount"
              type="number"
              min="0"
              step="0.01"
              value={topLevelForm.amount}
              onChange={(event) =>
                setTopLevelForm((current) => ({
                  ...current,
                  amount: event.target.value,
                }))
              }
              required
            />
          </div>

          <div className="space-y-2">
            <Label htmlFor="top-description">Description</Label>
            <Input
              id="top-description"
              type="text"
              value={topLevelForm.description}
              onChange={(event) =>
                setTopLevelForm((current) => ({
                  ...current,
                  description: event.target.value,
                }))
              }
            />
          </div>

          <Button
            type="submit"
            disabled={isSaving}
            className="md:col-span-2 w-fit"
          >
            Add Top-Level Category
          </Button>
        </form>
      </AdminCard>

      <AdminCard className="p-4">
        <h2 className="text-lg font-semibold text-slate-900">
          Add Sub-Category
        </h2>
        <form
          className="mt-4 grid gap-4 md:grid-cols-2"
          onSubmit={(event) => {
            event.preventDefault();
            void onCreate(
              subCategoryForm,
              () =>
                setSubCategoryForm((current) => ({
                  ...EMPTY_FORM,
                  fiscal_year: current.fiscal_year,
                })),
              subCategoryForm.parent_category_id,
            );
          }}
        >
          <div className="space-y-2">
            <Label htmlFor="sub-fiscal-year">Fiscal year</Label>
            <Input
              id="sub-fiscal-year"
              type="text"
              value={subCategoryForm.fiscal_year}
              onChange={(event) =>
                setSubCategoryForm((current) => ({
                  ...current,
                  fiscal_year: event.target.value,
                }))
              }
              required
            />
          </div>

          <div className="space-y-2">
            <Label htmlFor="sub-parent">Parent category</Label>
            <Select
              value={String(subCategoryForm.parent_category_id ?? "")}
              onValueChange={(value) =>
                setSubCategoryForm((current) => ({
                  ...current,
                  parent_category_id: value ? Number(value) : null,
                }))
              }
            >
              <SelectTrigger id="sub-parent">
                <SelectValue placeholder="Select parent" />
              </SelectTrigger>
              <SelectContent>
                {flatRows.map((row) => (
                  <SelectItem key={row.id} value={String(row.id)}>
                    {"  ".repeat(row.depth)}
                    {row.category}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>

          <div className="space-y-2">
            <Label htmlFor="sub-category">Category</Label>
            <Input
              id="sub-category"
              type="text"
              value={subCategoryForm.category}
              onChange={(event) =>
                setSubCategoryForm((current) => ({
                  ...current,
                  category: event.target.value,
                }))
              }
              required
            />
          </div>

          <div className="space-y-2">
            <Label htmlFor="sub-amount">Amount</Label>
            <Input
              id="sub-amount"
              type="number"
              min="0"
              step="0.01"
              value={subCategoryForm.amount}
              onChange={(event) =>
                setSubCategoryForm((current) => ({
                  ...current,
                  amount: event.target.value,
                }))
              }
              required
            />
          </div>

          <div className="space-y-2">
            <Label htmlFor="sub-description">Description</Label>
            <Input
              id="sub-description"
              type="text"
              value={subCategoryForm.description}
              onChange={(event) =>
                setSubCategoryForm((current) => ({
                  ...current,
                  description: event.target.value,
                }))
              }
            />
          </div>

          <Button
            type="submit"
            disabled={isSaving}
            className="md:col-span-2 w-fit"
          >
            Add Sub-Category
          </Button>
        </form>
      </AdminCard>

      <AdminCard className="p-4">
        <h2 className="text-lg font-semibold text-slate-900">Budget Tree</h2>
        <div className="mt-4 overflow-x-auto">
          <table className="min-w-full divide-y divide-slate-200 text-sm">
            <thead className="bg-slate-50">
              <tr>
                <th className="px-3 py-2 text-left font-medium text-slate-600">
                  Category
                </th>
                <th className="px-3 py-2 text-left font-medium text-slate-600">
                  Amount
                </th>
                <th className="px-3 py-2 text-left font-medium text-slate-600">
                  Description
                </th>
                <th className="px-3 py-2 text-left font-medium text-slate-600">
                  Actions
                </th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {isLoading ? (
                <tr>
                  <td
                    colSpan={4}
                    className="px-3 py-6 text-center text-slate-500"
                  >
                    Loading data...
                  </td>
                </tr>
              ) : flatRows.length === 0 ? (
                <tr>
                  <td
                    colSpan={4}
                    className="px-3 py-6 text-center text-slate-500"
                  >
                    No records found.
                  </td>
                </tr>
              ) : (
                flatRows.map((row) => (
                  <tr key={row.id}>
                    <td className="px-3 py-2 text-slate-900">
                      <span style={{ paddingLeft: `${row.depth * 1.25}rem` }}>
                        {row.depth > 0 ? "- " : ""}
                        {row.category}
                      </span>
                    </td>
                    <td className="px-3 py-2 text-slate-700">
                      {currency(row.amount)}
                    </td>
                    <td className="px-3 py-2 text-slate-700">
                      {row.description || "-"}
                    </td>
                    <td className="px-3 py-2">
                      <div className="flex gap-3">
                        <button
                          type="button"
                          onClick={() => startEdit(row)}
                          className="text-sm font-medium text-blue-700 hover:text-blue-800"
                        >
                          Edit
                        </button>
                        <button
                          type="button"
                          onClick={() => void onDelete(row)}
                          className="text-sm font-medium text-rose-700 hover:text-rose-800"
                        >
                          Delete
                        </button>
                      </div>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </AdminCard>

      {editingId !== null ? (
        <AdminCard className="border-amber-300 bg-amber-50 p-4">
          <h2 className="text-lg font-semibold text-amber-900">
            Edit Budget Row
          </h2>
          <div className="mt-4 grid gap-4 md:grid-cols-2">
            <div className="space-y-2">
              <Label htmlFor="edit-fiscal-year">Fiscal year</Label>
              <Input
                id="edit-fiscal-year"
                type="text"
                value={editForm.fiscal_year}
                onChange={(event) =>
                  setEditForm((current) => ({
                    ...current,
                    fiscal_year: event.target.value,
                  }))
                }
              />
            </div>

            <div className="space-y-2">
              <Label htmlFor="edit-parent">Parent category</Label>
              <Select
                value={
                  editForm.parent_category_id === null
                    ? TOP_LEVEL_PARENT_VALUE
                    : String(editForm.parent_category_id)
                }
                onValueChange={(value) =>
                  setEditForm((current) => ({
                    ...current,
                    parent_category_id:
                      value === TOP_LEVEL_PARENT_VALUE ? null : Number(value),
                  }))
                }
              >
                <SelectTrigger id="edit-parent">
                  <SelectValue placeholder="Top-level" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value={TOP_LEVEL_PARENT_VALUE}>
                    Top-level
                  </SelectItem>
                  {flatRows
                    .filter((row) => !disallowedParentIds.has(row.id))
                    .map((row) => (
                      <SelectItem key={row.id} value={String(row.id)}>
                        {"  ".repeat(row.depth)}
                        {row.category}
                      </SelectItem>
                    ))}
                </SelectContent>
              </Select>
            </div>

            <div className="space-y-2">
              <Label htmlFor="edit-category">Category</Label>
              <Input
                id="edit-category"
                type="text"
                value={editForm.category}
                onChange={(event) =>
                  setEditForm((current) => ({
                    ...current,
                    category: event.target.value,
                  }))
                }
              />
            </div>

            <div className="space-y-2">
              <Label htmlFor="edit-amount">Amount</Label>
              <Input
                id="edit-amount"
                type="number"
                min="0"
                step="0.01"
                value={editForm.amount}
                onChange={(event) =>
                  setEditForm((current) => ({
                    ...current,
                    amount: event.target.value,
                  }))
                }
              />
            </div>

            <div className="space-y-2 md:col-span-2">
              <Label htmlFor="edit-description">Description</Label>
              <Input
                id="edit-description"
                type="text"
                value={editForm.description}
                onChange={(event) =>
                  setEditForm((current) => ({
                    ...current,
                    description: event.target.value,
                  }))
                }
              />
            </div>

            <div className="md:col-span-2 flex gap-2">
              <Button
                onClick={() => void saveEdit()}
                disabled={isSaving}
                variant="outline"
              >
                Save Changes
              </Button>
              <Button
                onClick={() => {
                  setEditingId(null);
                  setEditForm(EMPTY_FORM);
                }}
                variant="outline"
              >
                Cancel
              </Button>
            </div>
          </div>
        </AdminCard>
      ) : null}
    </AdminPageShell>
  );
}
