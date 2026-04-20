"use client";

import { ArrowLeft } from "lucide-react";
import { useCallback, useEffect, useMemo, useState } from "react";
import { ResponsiveContainer, Tooltip, Treemap } from "recharts";

import { getBudget, getBudgetYears } from "@/lib/api";
import type { BudgetData } from "@/types";

import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";

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

type ChartDatum = {
  id: number;
  name: string;
  size: number;
  amount: number;
  color: string;
  percentage: number;
};

type TreemapContentProps = {
  x: number;
  y: number;
  width: number;
  height: number;
  color?: string;
  name: string;
};

type TooltipProps = {
  active?: boolean;
  payload?: Array<{ payload: ChartDatum }>;
};

function fiscalYearSortValue(fiscalYear: string) {
  const matches = fiscalYear.match(/\d+/g);
  const numericYear =
    matches && matches.length > 0 ? Number(matches[matches.length - 1]) : -1;
  return Number.isFinite(numericYear) ? numericYear : -1;
}

export default function FundingBudgetPage() {
  const [fiscalYear, setFiscalYear] = useState("");
  const [fiscalYears, setFiscalYears] = useState<string[]>([]);
  const [budget, setBudget] = useState<BudgetData[]>([]);
  const [drillPath, setDrillPath] = useState<BudgetData[]>([]);
  const [loading, setLoading] = useState(true);

  function formatCurrency(value: number) {
    return new Intl.NumberFormat("en-US", {
      style: "currency",
      currency: "USD",
      maximumFractionDigits: 0,
    }).format(value);
  }

  const loadBudget = useCallback(async (year: string) => {
    setLoading(true);
    try {
      const data = await getBudget(year || undefined);
      setBudget(data);
      setDrillPath([]);

      const resolvedYear = data[0]?.fiscal_year ?? year;
      if (resolvedYear) {
        setFiscalYear((current) => current || resolvedYear);
        setFiscalYears((current) => {
          if (current.includes(resolvedYear)) return current;
          return [...current, resolvedYear].sort(
            (left, right) =>
              fiscalYearSortValue(right) - fiscalYearSortValue(left),
          );
        });
      }
    } finally {
      setLoading(false);
    }
  }, []);

  const loadFiscalYears = useCallback(async () => {
    const years = await getBudgetYears();
    setFiscalYears(years);
    if (years.length > 0) {
      setFiscalYear((current) => {
        if (current && years.includes(current)) return current;
        return years[0];
      });
    }
  }, []);

  useEffect(() => {
    void loadFiscalYears();
  }, [loadFiscalYears]);

  useEffect(() => {
    void loadBudget(fiscalYear);
  }, [fiscalYear, loadBudget]);

  const currentLevel =
    drillPath.length > 0 ? drillPath[drillPath.length - 1].children : budget;

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

  function handleClick(node: { name?: string }) {
    const found = currentLevel.find((item) => item.category === node?.name);

    if (found?.children?.length) {
      setDrillPath((current) => [...current, found]);
    }
  }

  const CustomTooltip = ({ active, payload }: TooltipProps) => {
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

  const CustomTreemapContent = (props: TreemapContentProps) => {
    const { x, y, width, height, name, color } = props;

    if (!name || width <= 0 || height <= 0) {
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
        No budget data available for {fiscalYear || "the selected fiscal year"}.
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
              <SelectValue placeholder="Select year" />
            </SelectTrigger>
            <SelectContent>
              {fiscalYears.map((year) => (
                <SelectItem key={year} value={year}>
                  {year}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
        </CardHeader>

        <CardContent className="space-y-4">
          <div className="text-lg font-semibold">
            Total: {formatCurrency(totalBudget)}
          </div>

          {drillPath.length > 0 && (
            <Button
              variant="outline"
              size="sm"
              onClick={() => setDrillPath((current) => current.slice(0, -1))}
            >
              <ArrowLeft className="w-4 h-4 mr-2" />
              Back
            </Button>
          )}

          <div className="h-[320px] w-full md:h-[450px]">
            <ResponsiveContainer width="100%" height="100%">
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
                    {total > 0 ? ((item.size / total) * 100).toFixed(1) : "0.0"}
                    %
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
