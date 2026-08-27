"use client";

import type { NavigationFlow, NavigationFlowLink } from "@/types/admin";
import { useEffect, useMemo, useRef, useState } from "react";
import { Layer, Rectangle, Sankey, Tooltip } from "recharts";
import type { SankeyLinkProps, SankeyNodeProps } from "recharts";

const SANKEY_HEIGHT = 440;
const MIN_SANKEY_WIDTH = 600;
const SESSION_START_SENTINEL = "__start__";
const SESSION_START_LABEL = "Session Start";

// First three slots of the validated categorical palette (dataviz skill's
// documented default): blue / orange / aqua clear the all-pairs CVD floor,
// which matters here because flow bands from different roots can sit
// directly beside each other (unlike bars/lines, adjacency isn't fixed).
// A 4th+ root folds into OTHER_COLOR rather than cycling back through them.
const FLOW_PALETTE = ["#2a78d6", "#eb6834", "#1baf7a"];
const OTHER_COLOR = "#94a3b8";
const NODE_TEXT_COLOR = "#334155";

function truncateLabel(name: string, max = 32): string {
  return name.length > max ? `${name.slice(0, max - 1)}…` : name;
}

interface FlowNode {
  name: string;
  color: string;
  value: number;
}

interface FlowLink {
  source: number;
  target: number;
  value: number;
}

// Colors every node by the root (session-start or direct-entry page) it
// descends from, so a viewer can trace one flow's path across the diagram
// instead of every band reading as the same flat gray.
function assignNodeColors(nodeCount: number, links: FlowLink[]): string[] {
  const adjacency = new Map<number, number[]>();
  const hasIncoming = new Set<number>();
  for (const link of links) {
    hasIncoming.add(link.target);
    const existing = adjacency.get(link.source);
    if (existing) existing.push(link.target);
    else adjacency.set(link.source, [link.target]);
  }

  const roots = Array.from({ length: nodeCount }, (_, i) => i).filter((i) => !hasIncoming.has(i));
  const colors = new Array<string>(nodeCount).fill(OTHER_COLOR);
  const colored = new Array<boolean>(nodeCount).fill(false);

  roots.forEach((root, rootIndex) => {
    const color = rootIndex < FLOW_PALETTE.length ? FLOW_PALETTE[rootIndex] : OTHER_COLOR;
    const queue = [root];
    while (queue.length > 0) {
      const node = queue.shift();
      if (node === undefined || colored[node]) continue;
      colored[node] = true;
      colors[node] = color;
      for (const next of adjacency.get(node) ?? []) {
        if (!colored[next]) queue.push(next);
      }
    }
  });

  return colors;
}

function buildSankeyData(rawLinks: NavigationFlowLink[]) {
  const nodeIndex = new Map<string, number>();
  const names: string[] = [];

  function indexFor(rawName: string): number {
    let index = nodeIndex.get(rawName);
    if (index === undefined) {
      index = names.length;
      nodeIndex.set(rawName, index);
      names.push(rawName === SESSION_START_SENTINEL ? SESSION_START_LABEL : rawName);
    }
    return index;
  }

  const links: FlowLink[] = rawLinks.map((link) => ({
    source: indexFor(link.source),
    target: indexFor(link.target),
    value: link.count,
  }));

  const colors = assignNodeColors(names.length, links);

  // Each node's own throughput: prefer incoming (how many sessions reached
  // this page), falling back to outgoing for root nodes with no incoming edge.
  const incoming = new Array(names.length).fill(0);
  const outgoing = new Array(names.length).fill(0);
  for (const link of links) {
    outgoing[link.source] += link.value;
    incoming[link.target] += link.value;
  }

  const nodes: FlowNode[] = names.map((name, i) => ({
    name,
    color: colors[i],
    value: incoming[i] > 0 ? incoming[i] : outgoing[i],
  }));

  return { nodes, links };
}

function renderFlowNode(containerWidth: number) {
  return function FlowNodeShape({ x, y, width, height, payload: rawPayload }: SankeyNodeProps) {
    // recharts' SankeyNode type doesn't know about the `color`/`value` fields
    // we attach in buildSankeyData, but it passes our original node objects
    // straight through as payload, so this cast reflects the real runtime shape.
    const payload = rawPayload as unknown as FlowNode;
    const isRightHalf = x + width / 2 > containerWidth / 2;
    const label = `${truncateLabel(payload.name)} · ${payload.value.toLocaleString()}`;
    // No canvas measurement available here, so estimate the label chip's
    // width from character count — just needs to comfortably cover the text.
    const estTextWidth = label.length * 6.4 + 10;
    const textX = isRightHalf ? x - 6 : x + width + 6;
    const chipX = isRightHalf ? textX - estTextWidth : textX;

    return (
      <Layer>
        <Rectangle x={x} y={y} width={width} height={height} fill={payload.color} fillOpacity={0.95} />
        <rect
          x={chipX}
          y={y + height / 2 - 9}
          width={estTextWidth}
          height={18}
          rx={4}
          fill="rgba(255,255,255,0.85)"
        />
        <text
          x={textX}
          y={y + height / 2}
          textAnchor={isRightHalf ? "end" : "start"}
          dominantBaseline="middle"
          fontSize={12}
          fill={NODE_TEXT_COLOR}
        >
          {label}
        </text>
      </Layer>
    );
  };
}

function renderFlowLink({
  sourceX,
  sourceY,
  sourceControlX,
  targetX,
  targetY,
  targetControlX,
  linkWidth,
  payload: rawPayload,
}: SankeyLinkProps) {
  // Same cast as renderFlowNode: payload.source/target are our own node
  // objects at runtime, carrying the color field SankeyNode doesn't declare.
  const payload = rawPayload as unknown as { source: FlowNode; target: FlowNode };
  return (
    <path
      d={`M${sourceX},${sourceY} C${sourceControlX},${sourceY} ${targetControlX},${targetY} ${targetX},${targetY}`}
      fill="none"
      stroke={payload.source.color}
      strokeOpacity={0.45}
      strokeWidth={linkWidth}
    />
  );
}

function FlowTooltip({
  active,
  payload,
}: {
  active?: boolean;
  payload?: { payload: FlowNode | (FlowLink & { source: FlowNode; target: FlowNode }) }[];
}) {
  if (!active || !payload || payload.length === 0) return null;

  const raw = payload[0].payload;
  const isLink = "source" in raw && "target" in raw;
  const color = isLink ? raw.source.color : raw.color;
  const label = isLink ? `${raw.source.name} → ${raw.target.name}` : raw.name;

  return (
    <div className="rounded-md border border-slate-200 bg-white px-3 py-2 text-xs shadow-md">
      <div className="flex items-center gap-1.5 font-semibold text-slate-700">
        <span className="inline-block h-2 w-2 rounded-full" style={{ backgroundColor: color }} />
        {label}
      </div>
      <p className="mt-1 text-slate-600">
        {raw.value.toLocaleString()} session{raw.value === 1 ? "" : "s"}
      </p>
    </div>
  );
}

function useMeasuredWidth(fallback: number) {
  const ref = useRef<HTMLDivElement | null>(null);
  const [width, setWidth] = useState(fallback);

  useEffect(() => {
    const el = ref.current;
    if (!el) return;
    setWidth(el.clientWidth || fallback);
    const observer = new ResizeObserver((entries) => {
      const entry = entries[0];
      if (entry) setWidth(entry.contentRect.width);
    });
    observer.observe(el);
    return () => observer.disconnect();
  }, [fallback]);

  return [ref, width] as const;
}

export default function NavigationFlowChart({
  data,
  isLoading,
}: {
  data: NavigationFlow | null;
  isLoading?: boolean;
}) {
  const [containerRef, measuredWidth] = useMeasuredWidth(MIN_SANKEY_WIDTH);
  const width = Math.max(measuredWidth, MIN_SANKEY_WIDTH);
  const sankeyData = useMemo(() => (data ? buildSankeyData(data.links) : null), [data]);
  const nodeRenderer = useMemo(() => renderFlowNode(width), [width]);

  return (
    <div>
      <h3 className="mb-2 text-sm font-semibold text-slate-700">
        Navigation Flow
        {data && data.total_sessions > 0 && (
          <span className="ml-2 text-xs font-normal text-slate-400">
            ({data.total_sessions.toLocaleString()} sessions analyzed)
          </span>
        )}
      </h3>
      <div ref={containerRef} className="overflow-x-auto rounded-lg border border-slate-200 p-2">
        {isLoading ? (
          <div className="py-20 text-center text-sm text-slate-500">Loading flow…</div>
        ) : !sankeyData || sankeyData.links.length === 0 ? (
          <p className="py-6 text-center text-sm text-slate-500">No data yet.</p>
        ) : (
          <Sankey
            width={width}
            height={SANKEY_HEIGHT}
            data={sankeyData}
            node={nodeRenderer}
            link={renderFlowLink}
            nodePadding={24}
            nodeWidth={12}
            margin={{ top: 8, right: 170, bottom: 8, left: 8 }}
          >
            <Tooltip content={<FlowTooltip />} />
          </Sankey>
        )}
      </div>
    </div>
  );
}
