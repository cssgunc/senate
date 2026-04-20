"use client";

import { ArrowLeft } from "lucide-react";
import React, { useEffect, useMemo, useState } from "react";
import { ResponsiveContainer, Tooltip, Treemap, TreemapProps } from "recharts";

import { getBudget } from "@/lib/api";
import type { BudgetData } from "@/types";

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Button } from "@/components/ui/button";

const COLORS = [
  "#2563eb",
  "#16a34a",
  "#dc2626",
  "#ca8a04",
  "#9333ea",
  "#0891b2",
  "#f97316",
  "#be123c",
];

type ColoredBudgetData = BudgetData & {
  color: string;
};

type TreeNode = {
  name: string;
  value: number;
  amount: number;
  color: string;
  id: number;
  children?: TreeNode[];
};

type TreemapContentProps = {
  x: number;
  y: number;
  width: number;
  height: number;
  depth: number;
  payload: any;
  name: string;
};

export default function FundingBudgetPage() {
  const [fiscalYear, setFiscalYear] = useState("");
  const [budget, setBudget] = useState<BudgetData[]>([]);
  const [selectedNode, setSelectedNode] = useState<BudgetData | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadBudget();
  }, [fiscalYear]);

  function formatCurrency(value: number) {
    return new Intl.NumberFormat("en-US", {
      style: "currency",
      currency: "USD",
      maximumFractionDigits: 0,
    }).format(value);
  }

  async function loadBudget() {
    setLoading(true);
    try {
      console.log("Loading budget for fiscal year:", fiscalYear);
      const data = await getBudget(fiscalYear);
      setBudget(data);
      setSelectedNode(null);
      console.log("Budget data loaded:", data);
    } finally {
      setLoading(false);
    }
  }

  const currentLevel = selectedNode ? selectedNode.children : budget;

  const chartData = useMemo(() => {
    const total = currentLevel.reduce((sum, item) => sum + item.amount, 0);

    return currentLevel.map((item, index) => ({
      id: item.id,
      name: item.category,
      size: item.amount,
      amount: item.amount,
      color: COLORS[index % COLORS.length],
      percentage: total > 0 ? (item.amount / total) * 100 : 0,
    }));
  }, [currentLevel]);

  const totalBudget = useMemo(() => {
    return budget.reduce((sum, item) => sum + item.amount, 0);
  }, [budget]);

  const total = chartData.reduce((sum, i) => sum + i.size, 0);

  function handleClick(node: any) {
    const found = currentLevel.find(
      (item) => item.category === node?.name
    );

    if (found?.children?.length) {
      setSelectedNode(found);
    }
  }

  const CustomTooltip = ({ active, payload }: any) => {
    if (!active || !payload?.length) return null;

    const data = payload[0].payload;

    return (
      <div className="bg-zinc-900 text-white text-xs rounded-md p-3 shadow-lg border">
        <p className="font-semibold">{data.name}</p>
        <p>{formatCurrency(data.amount)}</p>
        <p>{data.percentage.toFixed(1)}%</p>
      </div>
    );
  };

  const CustomTreemapContent = (props: any) => {
    const { x, y, width, height, name, color } = props;

    if (!name || !color || width <= 0 || height <= 0) {
      console.log("Invalid props", props);
      return <g />;
    }

    return (
      <g>
        <rect
          x={x}
          y={y}
          width={width}
          height={height}
          fill={color ?? "#8884d8"}
          stroke="#fff"
          strokeWidth={2}
        />

        {width > 70 && height > 35 && (
          <text
            x={x + 8}
            y={y + 18}
            fill="white"
            fontSize={12}
            fontWeight="bold"
          >
            {name}
          </text>
        )}
      </g>
    );
  };

  if (loading) {
    return (
      <div className="p-6">
        <div className="h-[450px] w-full rounded-lg border bg-gray-100 animate-pulse" />
      </div>
    );
  }

  if (!budget.length) {
    return (
      <div className="p-6 text-center text-muted-foreground">
        No budget data available for FY {fiscalYear}
      </div>
    );
  }

  return (
    <div className="p-6 space-y-6">
      <Card>
        <CardHeader className="flex flex-row justify-between items-center">
          <CardTitle>Budget Allocation</CardTitle>

          <Select value={fiscalYear} onValueChange={setFiscalYear}>
            <SelectTrigger className="w-40">
              <SelectValue />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="2024-2025">FY 2024-2025</SelectItem>
              <SelectItem value="2025-2026">FY 2025-2026</SelectItem>
              <SelectItem value="2026-2027">FY 2026-2027</SelectItem>
            </SelectContent>
          </Select>
        </CardHeader>

        <CardContent className="space-y-4">
          <div className="text-lg font-semibold">
            Total: {formatCurrency(totalBudget)}
          </div>

          {selectedNode && (
            <Button
              variant="outline"
              size="sm"
              onClick={() => setSelectedNode(null)}
            >
              <ArrowLeft className="w-4 h-4 mr-2" />
              Back
            </Button>
          )}

          <div className="h-[450px] w-full min-h-[450px]">
            <ResponsiveContainer width="100%" height={450}>
              <Treemap
                data={chartData}
                dataKey="size"
                nameKey="name"
                content={CustomTreemapContent}
                onClick={handleClick}
              >
                <Tooltip content={<CustomTooltip />} />
              </Treemap>
            </ResponsiveContainer>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
            {chartData.map((item, index) => (
              <div
                key={item.id}
                className="flex justify-between border rounded-lg p-3"
              >
                <div className="flex items-center gap-2">
                  <div
                    className="w-3 h-3 rounded-sm"
                    style={{
                      backgroundColor: COLORS[index % COLORS.length],
                    }}
                  />
                  <span>{item.name}</span>
                </div>

                <div className="text-right">
                  <div>{formatCurrency(item.amount)}</div>
                  <div className="text-sm text-muted-foreground">
                    {((item.size / total) * 100).toFixed(1)}%
                  </div>
                </div>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>
    </div>
  );
}

