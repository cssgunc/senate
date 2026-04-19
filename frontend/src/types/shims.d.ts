// Shims for third-party modules that may not be installed in the temporary environment.
declare module "@tanstack/react-table" {
  export type ColumnDef<T, V = any> = any;
  export type RowData = any;
  export function flexRender(...args: any[]): any;
  export const getCoreRowModel: any;
  export const getSortedRowModel: any;
  export const getPaginationRowModel: any;
  export const getFilteredRowModel: any;
  export type SortingState = any;
  export function useReactTable(...args: any[]): any;
}

declare module "@tiptap/react" {
  export const useEditor: any;
  export const EditorContent: any;
}

declare module "@tiptap/starter-kit" {
  const StarterKit: any;
  export default StarterKit;
}

declare module "@radix-ui/react-select" {
  export const Root: any;
  export const Group: any;
  export const Value: any;
  export const Trigger: any;
  export const Icon: any;
  export const ScrollUpButton: any;
  export const ScrollDownButton: any;
  export const Content: any;
  export const Portal: any;
  export const Viewport: any;
  export const Label: any;
  export const Item: any;
  export const ItemIndicator: any;
  export const ItemText: any;
  export const Separator: any;
  const Select: any;
  export default Select;
}
